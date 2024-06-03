import gym
from gym import spaces
import numpy as np
from numpy._typing import NDArray
from scipy.interpolate import CubicHermiteSpline
from awgsomefi.parameters.voltage import VoltageBound

class GlitchEnvScopeless(gym.Env):
    """Custom Environment that follows gym interface"""
  #metadata = {'render.modes': ['human']}

    # Let's guess that if abs(dy/dx) > 0.08 we should punish the agent
    def __init__(self, total_time: int, glitch, voltage: VoltageBound, max_steps=8):
        super(GlitchEnvScopeless, self).__init__()
        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        # x, y
        # total_time
        # 300 ys (*10)
        self.max_steps = max_steps
        self.steps = 0

        self.xs = []
        self.ys = []
        self.total_time = total_time
        self.glitch = glitch
        self.voltage = voltage * 1000

        #self.action_space = spaces.Box(low=np.array([50.0, float(voltage.low*1000)]), high=np.array([total_time/2, float(voltage.high*1000)]))

        self.action_space = spaces.Box(low=-1, high=1, shape=(2,))

        # 1V chosen the margin of error for the recorded waveform
        self.observation_space = spaces.Dict({
            "wave": spaces.Box(low=self.voltage.low, high=self.voltage.high, shape=(total_time,)),
            "x": spaces.Box(low=0.0, high=total_time, shape=(1,)),
            "y": spaces.Box(low=self.voltage.low, high=self.voltage.high, shape=(1,)),
        })

    def step(self, action: NDArray):
        reward = 0
        done = False
        info = {}

        # de-normalize the actions
        x, y = action
        x = np.interp(x, [-1, 1], [50.0, self.total_time/4])
        y = np.interp(y, [-1, 1], [self.voltage.low, self.voltage.high])

        self.steps += 1

        if self.steps >= self.max_steps or sum(self.xs) + x + self.total_time//20 >= self.total_time:
            done = True

            posx = self.total_time
            posy = self.voltage.norm

            xs = np.array(self.xs)
            ys = np.array(self.ys)

            xs = np.append(np.cumsum(xs), posx)
            ys = np.append(ys, posy)

            px = xs[-1]
            py = ys[-1]

            mult = self.max_steps - self.steps

        else:
            mult = 0
            done = False

            xs = np.array(self.xs + [x])
            ys = np.array(self.ys + [y])

            #np.append(xs, x)
            #np.append(ys, y)

            self.xs.append(x)
            self.ys.append(y)

            xs = np.append(np.cumsum(xs), self.total_time)
            ys = np.append(ys, self.voltage.norm)

            px = xs[-2]
            py = ys[-2]

            posx = xs[-1]
            posy = ys[-1]

        print(xs, ys)

        reward = 1 - self.glitch(xs, ys, total_time=self.total_time)
    
        #if np.abs((py - y)/(px - x)) > self.derivative:
        #    reward -= 0.1

        poly = CubicHermiteSpline(xs, ys, np.zeros_like(xs))
        evals = np.arange(self.total_time)
        wave = poly(evals).astype(np.float32)

        observation = {
            "wave": wave,
            "x": np.array([posx], dtype=np.float32),
            "y": np.array([posy], dtype=np.float32),
        }

        print("reward", reward)
        return observation, reward, done, info

    def reset(self):
        self.steps = 0
        self.xs = [0.0]
        self.ys = [self.voltage.norm]
        
        wave = np.array(self.ys*self.total_time, dtype=np.float32)
        observation = {
            "wave": wave,
            "x": np.array(self.xs, dtype=np.float32),
            "y": np.array(self.ys, dtype=np.float32)
        }
        return observation

    def render(self, mode='human'):
        pass

    def close (self):
        pass
