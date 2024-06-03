from awgsomefi.awgctrl.devices.awggeneric import ChannelID
from awgsomefi.config import config
from awgsomefi.oceangen.polynomial.interpolation import PolynomialFactory
from awgsomefi.parameters.waveform import GlitchParams

polygens = config['lab']['polygen']


#####################
#  Hermite Splines  #
#####################
def generate_hermite_spline_equispaced(channel: ChannelID, voltages, plot=False):
    """
    Generates a waveform using a cubic Hermite spline given voltages
    The interpolation points are equispaced
    """

    polygen: PolynomialFactory = polygens[channel]

    positions = polygen.get_equispaced_points(len(voltages))

    return generate_hermite_spline(channel, positions, voltages, plot)

def generate_hermite_spline(channel: ChannelID, positions, voltages, plot=False):
    """
    Generates a waveform using a cubic Hermite spline given voltages and corresponding interpolation points.
    """
    assert len(voltages) == len(positions)

    polygen: PolynomialFactory = polygens[channel]

    poly = polygen.interpolate_hermite_spline(positions, voltages)
    _, points = poly.eval_all(plot)

    return points, poly

#####################
#  Regular Splines  #
#####################
def generate_spline(channel: ChannelID, positions, voltages, configuration="clamped", plot=False):
    """
    Generates a waveform using a cubic Hermite spline given voltages and corresponding interpolation points.

    For meaning of `configuration`, see documentation for CubicSpline: `https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.CubicSpline.html`
    """
    assert len(voltages) == len(positions)

    polygen: PolynomialFactory = polygens[channel]

    poly = polygen.interpolate_spline(positions, voltages, configuration)
    _, points = poly.eval_all(plot)

    return points, poly

def generate_spline_equispaced(channel: ChannelID, voltages, configuration="clamped", plot=False):

    polygen: PolynomialFactory = polygens[channel]

    positions = polygen.get_equispaced_points(len(voltages))

    return generate_spline(channel, positions, voltages, configuration, plot)


######################
#  Cheb Polynomials  #
######################
def generate_chebyshev(channel: ChannelID, voltages, plot=False):
    """
    Generates a Chebyshev polynomial waveform by interpolating the given voltages on Chebyshev nodes
    """

    polygen: PolynomialFactory = polygens[channel]
    xs = polygen.get_chebyshev_nodes(len(voltages))
    poly = polygen.interpolate_chebyshev(xs, voltages)
    _, points = poly.eval_all(plot)

    return points, poly

####################
#  Modular Splines #
####################
def generate_modular_params(channel: ChannelID, voltages, rand_segments, slew):
    """
    Generates the glitch parameters to be used with `generate_hermite_spline`
    """
    polygen: PolynomialFactory = polygens[channel]
    device_voltages = polygen.voltage

    def get_voltage(index):
        if 0 <= index < len(voltages):
            return voltages[index]
    
        return device_voltages.norm

    segment_offsets = []
    for i, segment in enumerate(rand_segments):
        min_time = abs(get_voltage(i-1) - get_voltage(i))/slew
        segment_offsets.append(segment + min_time)

    final_offset = segment_offsets[-1]
    segments = segment_offsets[:-1]
    
    assert len(voltages) == len(segments)

    return GlitchParams.from_segments(segments, voltages, final_offset)
