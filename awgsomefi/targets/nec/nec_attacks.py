from typing import Tuple
from awgsomefi.config import config
from awgsomefi.awgctrl import AWG
from awgsomefi.oceangen import glitch
from awgsomefi.awgctrl.parameters import ArbWave
import awgsomefi.oceangen.optimize as optimizer
import awgsomefi.oceangen.smactimize as smactimize

import functools
import datetime

import numpy as np

from awgsomefi.parameters.waveform import GlitchParams

from .nec_adapter import nec_leak, nec_disable, nec_reenable, nec_leak_score, nec_leak_score_vector, nec_short_checksum, mass_verify, nec_leak_histogram
from .constants import *

awg: AWG = config['lab']['AWG']

def get_time_offset(byte_target: int) -> Tuple[int, int]:
    """
    Given target 4 bytes to leak, provides the time offset for attacking the first and second couplet.

    Will most likely need adjustment!  `collect_histogram()` might be able to help with that
    """
    assert byte_target < 0x100
    assert byte_target % 2 == 0
    two_offset = delay2 + (byte_target//4) * (word2_offset - 320)
    base_offset = two_offset + 500 - MAGIC_offset
    #two_offset = int(1193535.0 + (byte_target//4)*4 * (13155.5))
    return base_offset, two_offset+10

def test_leakage(block: int, target: int, raw_expected: bytes, glitch_params: GlitchParams, time_offset=0, tries=100):
    """
    If bytes are known ahead of time, we can test how well given waveforms perform.

    raw_expected
    """
    expected_1 = raw_expected[0], raw_expected[0] + raw_expected[1]
    expected_2 = raw_expected[2], raw_expected[2] + raw_expected[3]

    base_time, offset_time = get_time_offset(target)
    waveform, _ = glitch.generate_hermite_spline(1, glitch_params.norm_ts, glitch_params.voltages, plot=False)
    try_glitch = ArbWave.from_period(period=glitch_params.period, waveform=waveform, phase=0)

    if target % 4 != 0:
        time = offset_time
        expected = expected_2
    else:
        time = base_time
        expected = expected_1

    awg.setup_arbitrary(1, "nec_glitch", try_glitch)
    awg.set_trig_delay(1, time + time_offset)

    score_vec, fps = nec_leak_score_vector(tries, expected, idx=block)

    tries = sum(score_vec)
    print(f"Success Single:", f"{score_vec[1]}/{tries}")
    print(f"Success Double:", f"{score_vec[2]}/{tries}")
    print(f"Success Total:", f"{score_vec[1]+score_vec[2]}/{tries}")
    print(f"False Positive Count:", f"{score_vec[3]}/{tries}")
    print(f"False Positives:", fps)
    print(f"Errors:", f"{score_vec[4]}/{tries}")
    #print(f"Leaked {len(possibilities_1)}")
    return score_vec

def collect_histogram(block, target_couplet, glitch_params: GlitchParams, time_offset=0, tries=100, sample_count=20, search_range=[-1500, 1500]):
    """
    Scans a given time search range. Useful for seeing at what point in time glitches work the best.
    """
    base_time, offset_time = get_time_offset(target_couplet)

    if target_couplet % 4 != 0:
        time = offset_time
    else:
        time = base_time

    waveform, _ = glitch.generate_hermite_spline(1, glitch_params.norm_ts, glitch_params.voltages, plot=False)
    try_glitch = ArbWave.from_period(period=glitch_params.period, waveform=waveform, phase=0)

    time_hist = {}
    
    import json
    awg.setup_arbitrary(1, "nec_glitch", try_glitch)
    for i, time in enumerate(np.linspace(time + search_range[0], time + search_range[1], sample_count)):
        print(f"Iteration {i}")
        awg.set_trig_delay(1, time + time_offset)
        time_hist[time] = nec_leak_histogram(tries, idx=block)
        #print("hist:", time_hist[time])

        with open(f"histograms/raw/glitch_histogram_{datetime.datetime.now()}.json", 'w') as f:
            json.dump(time_hist, f)

    return time_hist

# glitch_params=(490, (0.06960520233806726, 0.08646895688544246, 0.07160240600478679), (16, 53, 68))
def leak_quad(block: int, found_bytes: bytes, glitch_params: GlitchParams, time_offset=(0, 0)):
    """
    Tried to leak 4 bytes at `block` with `found_bytes` found so far.

    XXX: Returns with nothing if bytes not found. During attack it should keep restarting until it finds something
    """
    #glitch_params1 = 490, (0.06960520233806726, 0.08646895688544246, 0.07160240600478679), (16, 53, 68)
    #glitch_params0 = 490, (0.06960520233806726, 0.08646895688544246, 0.07160240600478679), (16, 53, 68)

    target_couplet = len(found_bytes)
    print(f"Leaking 4 bytes starting at byte {target_couplet} at block {block}")

    base_time, offset_time = get_time_offset(target_couplet)

    waveform1, _ = glitch.generate_hermite_spline(1, glitch_params.norm_ts, glitch_params.voltages, plot=False)
    try_glitch1 = ArbWave.from_period(period=glitch_params.period, waveform=waveform1, phase=0)

    awg.set_trig_delay(1, base_time + time_offset[0])

    # XXX: I'm trying two different types of glitches
    # Play around with those to see what's actually needed
    awg.setup_arbitrary(1, "nec_glitch", try_glitch1)
    possibilities_1: list[int] = nec_leak(20, idx=block)
    print(f"Leaked {len(possibilities_1)}")

    awg.set_trig_delay(1, offset_time + time_offset[1])

    possibilities_2: list[int] = nec_leak(20, idx=block)
    print(f"Leaked {len(possibilities_2)}")

    possibilities_1.sort()
    possibilities_2.sort()
    guess = mass_verify(block, possibilities_1, possibilities_2, found_bytes)
    print("Found:", guess)

    nec_disable()

def tune_glitch_smac(block: int, target_couplet: int, raw_expected, limited=None, recall=False):
    expected_1 = raw_expected[0], raw_expected[0] + raw_expected[1]
    expected_2 = raw_expected[2], raw_expected[2] + raw_expected[3]

    base_time, offset_time = get_time_offset(target_couplet)
    if target_couplet % 4 != 0:
        time = offset_time
        expected = expected_2
    else:
        time = base_time
        expected = expected_1

    if limited == 1:
        expected = [expected[0]]
    if limited == 2:
        expected = [expected[1]]

    print("looking for:", expected)
    nec_leaker = functools.partial(nec_leak_score_vector, idx=block, expectation=expected)

    if recall:
        return smactimize.smac_view_nec(1, nec_leaker, time)
    model = smactimize.smac_optimize_nec(1, nec_leaker, time)
    return model

def tune_glitch_skopt(block: int, target_couplet: int, raw_expected, limited=None):
    expected_1 = raw_expected[0], raw_expected[0] + raw_expected[1]
    expected_2 = raw_expected[2], raw_expected[2] + raw_expected[3]

    base_time, offset_time = get_time_offset(target_couplet)
    if target_couplet % 4 != 0:
        time = offset_time
        expected = expected_2
    else:
        time = base_time
        expected = expected_1

    if limited == 1:
        expected = [expected[0]]
    if limited == 2:
        expected = [expected[1]]

    print("looking for:", expected)
    nec_leaker = functools.partial(nec_leak_score, idx=block, expectation=expected)

    model = optimizer.bayes_optimize_modular(1, nec_leaker, time)
    return model
