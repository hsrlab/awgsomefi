from typing import Dict

from awgsomefi.awgctrl.parameters.resolution import Resolution
from awgsomefi.awgctrl import AWG
from awgsomefi.config.parsers.optimization import parse_skopt, parse_smac
from awgsomefi.oceangen.polynomial.interpolation import PolynomialFactory
from awgsomefi.scopectrl.devices.siglentSDS import SiglentSDS

class InitializationError(Exception):
    pass

def opamp(raw_configurations: Dict):
    return raw_configurations['instruments']['OPAMP']

def parse_lab(raw_config):
    lab_config = raw_config['lab']
    lab_name = lab_config['lab_active']
    return lab_config.get(lab_name)

def parse_instruments(raw_config):
    instrument_config = raw_config['instruments']
    return instrument_config

# Parse awg and ploynomial generators
def initialize_lab(raw_configurations: Dict):
    lab = parse_lab(raw_configurations)
    instruments = parse_instruments(raw_configurations)

    devices = {}

    if "AWG" in lab:
        lab_awg = lab['AWG']
        channels: list = lab_awg["enabled"]

        awg = AWG.get_awg(ip=lab_awg['ip'], model=lab_awg['model'], setup_params=instruments["AWG"])

        if awg is None:
            raise InitializationError("Could not find AWG on network")

        resolution: Resolution = awg.properties['resolution']
        channel_voltages = awg.channel_voltages

        # Setup AWG device
        devices['AWG'] = awg

        # Setup polynomial generators for each channel
        devices['polygen'] = {}
        for channel, voltage in channel_voltages.items():
            poly = PolynomialFactory(resolution, voltage)
            devices['polygen'][channel] = poly

        # Save the voltage configurations of the channel
        devices["channel_voltage"] = channel_voltages

        for channel in channels:
            awg.enable_channel(channel)

    if "Scope" in lab:
        lab_scope = lab['Scope']
        channels = lab_scope["enabled"]
        scope = SiglentSDS(lab_scope["ip"])

        if scope is None:
            raise InitializationError("Could not find scope on network")

        devices["scope"] = scope
        devices["scope-channel"] = channels[0] if len(channels) else None


    return devices

def initialize_opt_params(raw_configurations: Dict):
    skopt = parse_skopt(raw_configurations)
    smac = parse_smac(raw_configurations)
    return dict(skopt=skopt, smac=smac)


parsers = {
    "lab": initialize_lab,
    "optimization": initialize_opt_params
}
