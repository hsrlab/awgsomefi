
#from TargetDriver.glitc_stm import run_glitch
import time
from TargetDriver.controllers.controller import ACKError
from awgsomefi.targets import nec

from awgsomefi.awgctrl import AWG
from awgsomefi.awgctrl.parameters import ArbWave, wave

from awgsomefi.config import config
from awgsomefi.scopectrl.devices.siglentSDS import SiglentSDS
from awgsomefi.targets import *

from awgsomefi.oceangen.polynomial.interpolation import PolynomialFactory
from awgsomefi.oceangen.optimize import objective_run

from scipy.interpolate import CubicHermiteSpline

from stable_baselines3.common.vec_env import VecNormalize, DummyVecEnv
from stable_baselines3.common.env_checker import check_env
from stable_baselines3 import PPO, SAC

import matplotlib.pyplot as plt
import gym
import numpy as np
import functools


def glitch(xs, ys, total_time, **kwargs):
    assert len(xs) == len(ys)
    assert len(xs) > 1

    awg: AWG = config['lab']['AWG']
    channel = 1
    polygen: PolynomialFactory = config['lab']['polygen'][channel]

    xs = np.interp(xs, [0, total_time], [0, polygen.resolution.horizontal])

    poly = CubicHermiteSpline(xs, ys, np.zeros_like(xs))
    poly = polygen.lift(poly)
    _, waveform = poly.eval_all(plot=False)

    wave = ArbWave.from_period(period=total_time, waveform=waveform, phase=0)

    awg.setup_arbitrary(channel, "rl_glitch", wave)
    obj = objective_run(mcu_target, 100, **kwargs)
    print("objective", obj)
    return obj

def glitch_nec(xs, ys, total_time, glitch_count=10, *, delay, leak_scorer, **kwargs):
    assert len(xs) == len(ys)
    assert len(xs) > 1

    awg: AWG = config['lab']['AWG']
    channel = 1
    polygen: PolynomialFactory = config['lab']['polygen'][channel]

    xs = np.interp(xs, [0, total_time], [0, polygen.resolution.horizontal])

    poly = CubicHermiteSpline(xs, ys, np.zeros_like(xs))
    poly = polygen.lift(poly)
    _, waveform = poly.eval_all(plot=False)
    #plt.show()

    wave = ArbWave.from_period(period=total_time, waveform=waveform, phase=0)

    awg.setup_arbitrary(channel, "rl_glitch", wave)
    awg.set_trig_delay(1, delay)
    #obj = objective_run(mcu_target, 100, **kwargs)
    obj = leak_scorer(glitch_count)
    print("objective", obj)
    return obj

def start_greedy_random(total_time: int, block: int, raw_expected, target, test=False):
    polygen: PolynomialFactory = config['lab']['polygen'][1]
    expected_1 = raw_expected[0], raw_expected[0] + raw_expected[1]
    expected_2 = raw_expected[2], raw_expected[2] + raw_expected[3]
    delay4, delay6 = nec.nec_attacks.get_time_offset(target)

    if target % 4 == 2:
        delay = delay6
        expect = expected_2
        print("delay6", expected_2)
    else:
        delay = delay4
        expect = expected_1

    nec_leaker = functools.partial(nec.nec_adapter.nec_leak_score, idx=block, expectation=set(expect))
    fake_leaker = lambda *_: np.random.uniform(0, 1)

    scorer = nec_leaker
    if test:
        scorer = fake_leaker

    nec_glitcher = functools.partial(glitch_nec, delay=delay, leak_scorer=scorer)

    best_glitch = -2
    voltage = polygen.voltage * 1000
    for i in range(1):
        print(f"Starting glitch iteration {i}. Best glitch {best_glitch}")
        ldone = rdone = False

        stepsxl: list[float] = []
        stepsxr: list[float] = []

        stepsy = [voltage.norm, voltage.norm]

        best_ystep = 0
        center_x = np.random.uniform(50.0, total_time - 50)
        position = 1

        while not ldone or not rdone:
            try_x = [0.0] + stepsxl + [center_x] + stepsxr + [total_time]
            max_reward = -2
            for stepy in np.linspace(voltage.low, voltage.high, 6):
                time.sleep(1)
                try_y = stepsy.copy()
                try_y.insert(position, stepy)
                reward = 1 - nec_glitcher(try_x, try_y, total_time)
                if reward > max_reward:
                    max_reward = reward
                    best_ystep = stepy

            stepsy.insert(position, best_ystep)

            if not stepsxl:
                boundl = center_x
            else:
                boundl = stepsxl[0]

            if not stepsxr:
                boundr = center_x
            else:
                boundr = stepsxr[-1]

            ldone = boundl - 50 < 50
            rdone = boundr + 50 > total_time - 50

            if rdone and not ldone:
                stepsxl.insert(0, np.random.randint(50, int(boundl) - 50))
                position = 1
                print("Right is done. Picking left")

            elif ldone and not rdone:
                stepsxr.append(np.random.randint(int(boundr) + 50, total_time - 50))
                position = -1
                print("Left is done. Picking right")

            elif not rdone and not ldone:
                if np.random.randint(0, 2):
                    stepsxl.insert(0, np.random.randint(50, int(boundl) - 50))
                    position = 1
                    print("Randomly picked left")
                else:
                    stepsxr.append(np.random.randint(int(boundr) + 50, total_time - 50))
                    position = -1
                    print("Randomly picked right")

        print("Both sides done")
        final_stepsx = [0.0] + stepsxl + [center_x] + stepsxr + [total_time]
        final_stepsy = stepsy
        total_reward = 1 - nec_glitcher(final_stepsx, final_stepsy, total_time, glitch_count=20)

        print("Total success rate:", total_reward)
        print("Waveform found:", final_stepsx, final_stepsy)

        return final_stepsx, final_stepsy

def start_greedy_scopeless(total_time: int, block: int, raw_expected, target):
    polygen: PolynomialFactory = config['lab']['polygen'][1]
    expected_1 = raw_expected[0], raw_expected[0] + raw_expected[1]
    expected_2 = raw_expected[2], raw_expected[2] + raw_expected[3]

    delay4, delay6 = nec.nec_attacks.get_time_offset(target)

    if target % 4 == 2:
        delay = delay6
        expect = expected_2
        print("delay6", expected_2)
    else:
        delay = delay4
        expect = expected_1

    nec_leaker = functools.partial(nec.nec_adapter.nec_leak_score, idx=block, expectation=set(expect))
    nec_glitcher = functools.partial(glitch_nec, delay=delay, leak_scorer=nec_leaker)

    best_glitch = -2
    best_waveform = ([], [])

    voltage = polygen.voltage * 1000
    dvdt = (voltage.high - voltage.low)/100
    for i in range(10):
        print(f"Starting glitch iteration {i}. Best glitch {best_glitch}")
        done = False
        stepsx = [0.0]
        stepsy = [voltage.norm]
        step = stepsx[0], stepsy[0]
        while not done:
            stepx = np.random.uniform(50.0, total_time/4)
            try_x = np.cumsum(stepsx + [stepx])
            if try_x[-1] > total_time:
                done = True
                break

            try_x = np.append(try_x, total_time)

            upper_bound = min(voltage.high, stepsy[-1] + dvdt * stepx)
            lower_bound = max(voltage.low, stepsy[-1] - dvdt * stepx)
            
            print("bounds", lower_bound, "-", upper_bound)

            max_reward = -2
            for stepy in np.linspace(lower_bound, upper_bound, 5, endpoint=False):
                try_y = stepsy + [stepy] + [voltage.norm]
                reward = 1 - nec_glitcher(try_x, try_y, total_time)
                if reward > max_reward:
                    max_reward = reward
                    step = stepx, stepy
                    print("Best intermediate", try_x, try_y)

            if not done:
                stepsx.append(step[0])
                stepsy.append(step[1])

        final_stepsx = np.append(np.cumsum(stepsx), total_time)
        final_stepsy = stepsy + [voltage.norm]
        total_reward = 1 - nec_glitcher(final_stepsx, final_stepsy, total_time, glitch_count=20)
        if total_reward > best_glitch:
            best_glitch = total_reward
            best_waveform = final_stepsx, final_stepsy

        print("Best waveform", best_waveform, best_glitch)
    print("Final Best waveform", best_waveform, best_glitch)
    return best_waveform


def start_rl_scopeless(total_time: int, block: int, raw_expected, target):
    polygen: PolynomialFactory = config['lab']['polygen'][1]
    #scope: SiglentSDS = config['lab']['scope']
    #scope_channel = config['lab']['scope-channel']
    #env = gym.make("Glitch-v0", total_time=total_time, scope_channel=scope_channel,
    #               glitch=glitch, scope=scope, voltage=polygen.voltage
    #)
    expected_1 = raw_expected[0], raw_expected[0] + raw_expected[1]

    delay4, delay6 = nec.nec_attacks.get_time_offset(target)

    nec_leaker = functools.partial(nec.nec_adapter.nec_leak_score, idx=block, expectation=set(expected_1))
    nec_glitcher = functools.partial(glitch_nec, delay=delay6, leak_scorer=nec_leaker)


    env = gym.make("Glitch-scopless-v0", total_time=total_time,
                   glitch=nec_glitcher, voltage=polygen.voltage
    )

    #model = PPO("MultiInputPolicy", env, verbose=1, batch_size=4, n_steps=4, device="cpu")
    model = PPO.load("ppo_model_nec_two", env=env)
    env.reset()
    try:
        model.learn(total_timesteps=20, progress_bar=True)
    except KeyboardInterrupt:
        print("Exiting")
    except ACKError as e:
        print("ACKError", e)
    finally:
        model.save("ppo_model_nec_two")

