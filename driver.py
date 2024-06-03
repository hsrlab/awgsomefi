import matplotlib.pyplot as plt

from awgsomefi.awgctrl import AWG
from awgsomefi.awgctrl.devices.awggeneric import ChannelID
from awgsomefi.awgctrl.parameters import ArbWave, SquareWave
from awgsomefi.oceangen import glitch
from awgsomefi.config import config

from awgsomefi.targets import nec, stm_target
from awgsomefi.glitch_parameters import version_newdouble

def setup_clock(awg, channel: ChannelID):
    """
    OCXO should probably be used instead of AWG clock
    """
    clock = SquareWave(frequency=8000000)
    awg.setup_square(channel, clock)

awg: AWG = config['lab']['AWG']
GLITCH_CHANNEL = 1

def example_glitch_setup():
    pts = [0.1, 0.3, 0.11, 0.21]
    plot = True
    period = 500 # ns
    waveform, _ = glitch.generate_spline_equispaced(GLITCH_CHANNEL, pts, plot=plot)
    try_glitch = ArbWave.from_period(period=period, waveform=waveform, phase=0)
    awg.setup_arbitrary(1, "testing", try_glitch)

def nec_glitch():
    block = 5 # 0x00-0xff  sequence
    #block = 6 # 0xff-0x00  sequence
    #block = 14 # Fixed 4-byte repetitions

    """
    Test Waveform (78K0R)
    """
    #nec.test_leakage(block, 16, bytes([0x10, 0x11, 0x12, 0x13]), glitch_params=version_newdouble, tries=1000, time_offset=-85)
    nec.leak_quad(block, bytes(range(0, 16)), glitch_params=version_newdouble)


    """
    Waveform searching (78K0R)
    """
    #nec.tune_glitch_skopt(block, 0x12, bytes([0x10, 0x11, 0x12, 0x13]))
    #nec.tune_glitch_smac(block, 0x12, bytes([0x10, 0x11, 0x12, 0x13]))


def main():
    nec_glitch()

if __name__ == "__main__":
    nec.enable()

    try:
        main()
    finally:
        nec.disable()

    # Show any plots
    plt.show()
