import datetime
import skopt
import numpy as np

import matplotlib.pyplot as plt

from skopt import gp_minimize, gbrt_minimize
from skopt.plots import plot_objective, plot_convergence
from awgsomefi.awgctrl.devices.awggeneric import ChannelID

from awgsomefi.awgctrl.parameters.wave import ArbWave
from awgsomefi.awgctrl import AWG
from awgsomefi.config import config
from awgsomefi.parameters.optimization_params import SkoptAcquisition, SkoptModel, SkoptParams
from awgsomefi.parameters.voltage import VoltageBound
from awgsomefi.parameters.waveform import GlitchParams

from . import glitch

from .objectives import loop_escape_objective


def get_algorithm(skopt_config: SkoptParams):
    if skopt_config.model == SkoptModel.GP:
        optimize = gp_minimize
    elif skopt_config.model == SkoptModel.GBRT: 
        optimize = gbrt_minimize
    else:
        raise ValueError(f"Invalid optimization algorithm: {SkoptModel}")

    return optimize



def bayes_optimize_modular(channel: ChannelID, target, timing, fileload=None):
    store = "dataset/" + f"nec_modular_{datetime.datetime.now()}.gz"

    skopt_config: SkoptParams = config['optimization']['skopt']
    awg: AWG = config['lab']['AWG']
    point_count = skopt_config.point_count
    device_voltages: VoltageBound = awg.channel_voltages[channel]

    def opt(x):

        segment_count = point_count + 1
        timing_offset = x[0]
        rand_segments = x[1:1+segment_count]
        voltages = x[1+segment_count:1+segment_count+point_count]

        glitch_params = glitch.generate_modular_params(
                channel,
                voltages,
                rand_segments,
                skopt_config.slew_limit / 100 # Convert from V/100ns to V/ns
        )

        waveform, _ = glitch.generate_hermite_spline(channel, glitch_params.norm_ts, glitch_params.voltages, plot=False)
        try_glitch = ArbWave.from_period(period=glitch_params.period, waveform=waveform, phase=0)

        #offset = np.random.randint(-100, 100)
        awg.setup_arbitrary(channel, "nec_glitch", try_glitch)
        awg.set_trig_delay(channel, timing + timing_offset)


        print("Glitch Parameters", glitch_params)
        print("at time", timing_offset)

        score = target(skopt_config.glitches_per_sample)
        print("total score:", score)
        print()

        return score

    # x0 and y0 are loaded if we are resuming optimization
    extra = {}
    if fileload is not None:
        old_res = skopt.load("dataset/"+fileload)
        extra["x0"] = old_res.x_iters
        extra["y0"] = old_res.func_vals


    periods = [skopt_config.segment_length for _ in range(point_count+1)]
    voltage_ranges = [(device_voltages.low, device_voltages.high) for _ in range(point_count)]
    timing_offset_range = [skopt_config.time_offset]

    # 0.5 to 2 volts
    # 0.5 microsecond to 2 microsecond
    optimize = get_algorithm(skopt_config)

    print(timing_offset_range + periods + voltage_ranges,)
    res = optimize(opt,
                timing_offset_range + periods + voltage_ranges,  # proposal polynomial
                n_initial_points=skopt_config.initial_points,
                acq_func=skopt_config.acquisition.value,
                n_calls=skopt_config.total_points,
                n_jobs=1,
                **extra
    )

    assert res is not None

    print(res.x)
    print(res.fun)
    plot_convergence(res)
    skopt.dump(res, store, store_objective=False)
    #plot_objective(res)
    plt.show()
    return res
