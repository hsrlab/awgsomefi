
from typing import Dict

from awgsomefi.parameters.optimization_params import SkoptParams, SmacParams

def parse_skopt(raw_configurations: Dict):
    return SkoptParams.from_dict(raw_configurations['skopt'])

def parse_smac(raw_configurations: Dict):
    return SmacParams.from_dict(raw_configurations['smac'])
