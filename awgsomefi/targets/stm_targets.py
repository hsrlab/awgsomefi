from awgsomefi.awgctrl.parameters.wave import ArbWave
from awgsomefi.oceangen import glitch
from awgsomefi.oceangen.objectives import loop_escape_objective
from awgsomefi.awgctrl import AWG
from awgsomefi.config import config

from TargetDriver.glitch_stm import run_glitch as stm_glitch

import matplotlib.pyplot as plt

awg: AWG = config['lab']['AWG']

def stm_target(*args, **kwargs):
    """
    Loop escape
    """
    return stm_glitch()

def test_u_glitch(channel, period, low, plot=False, **kwargs):
    waveform, _ = glitch.generate_spline_equispaced(channel, [low], plot=plot, **kwargs)
    try_glitch = ArbWave.from_period(period=period, waveform=waveform, phase=0)
    awg.setup_arbitrary(1, "u_glitch", try_glitch)
    print("Score:", loop_escape_objective(stm_target, 100, only_score=True))

def test_all_w_glitch_spline(channel, period, low1, high, low2, plot=False, **kwargs):
    waveform, _ = glitch.generate_hermite_spline_equispaced(channel, [low1, high, low2], plot=plot)
    try_glitch = ArbWave.from_period(period=period, waveform=waveform, phase=0)
    awg.setup_arbitrary(1, "all_w_glitch", try_glitch)
    print("Score:", loop_escape_objective(stm_target, 100, only_score=True, **kwargs))

def test_all_wv_glitch_spline(channel, period, low1, high1, low2, high2, low3, plot=False, **kwargs):
    waveform, _ = glitch.generate_hermite_spline_equispaced(channel, [low1, high1, low2, high2, low3], plot=plot, **kwargs)
    try_glitch = ArbWave.from_period(period=period, waveform=waveform, phase=0)
    awg.setup_arbitrary(1, "all_wv_glitch", try_glitch)
    print("Score:", loop_escape_objective(stm_target, 100, only_score=True))

def test_all_w_glitch_spline_pos(channel, period, low1, high, low2, posa, posb, posc, plot=False, **kwargs):
    waveform, _ = glitch.generate_hermite_spline(channel, [posa, posb, posc], [low1, high, low2],plot=plot)
    try_glitch = ArbWave.from_period(period=period, waveform=waveform, phase=0)
    awg.setup_arbitrary(1, "all_w_glitch", try_glitch)
    score, overview = loop_escape_objective(stm_target, 100, only_score=False, **kwargs)
    print("Score:", score)
    print("Glitch results:", overview)
