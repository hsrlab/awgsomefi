from awgsomefi.parameters import VoltageBound
from typing import Dict

def parse_voltage_target(raw_configurations: Dict) -> VoltageBound:
    """
    Parse raw configurations into a VoltageBound instance.
    Takes into account OPAMP gain.
    """
    gain = raw_configurations['instruments']['target']['opamp_gain']
    voltage = parse_voltage_noamp(raw_configurations) / gain
    return voltage

def parse_voltage_noamp(raw_configurations: Dict):
    awg_config = raw_configurations['instruments']['AWG']
    voltage = VoltageBound(awg_config['voltage_min'],
                           awg_config['voltage_max'],
                           awg_config['voltage_norm']
    ) 
    
    return voltage
