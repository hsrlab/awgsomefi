from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from typing import Tuple

class SkoptModel(str, Enum):
    GBRT = "gbrt"
    GP = "gp"

# https://scikit-optimize.github.io/stable/modules/generated/skopt.gp_minimize.html
class SkoptAcquisition(str, Enum):
    LCB = "LCB"
    EI = "EI"
    PI = "PI"
    # Only with `SkoptModel.GP`
    GP_HEDGE = "gp_hedge"


@dataclass
class SkoptParams:
    point_count: int
    segment_length: Tuple[int, int]
    time_offset: Tuple[int, int]
    model: SkoptModel
    acquisition: SkoptAcquisition

    initial_points: int
    glitches_per_sample: int
    total_points: int

    slew_limit: float

    @classmethod
    def from_dict(cls, config):
        waveform = config['Waveform']
        opt = config['Optimization']

        new_config = {**waveform, **opt}

        segment_lengths = new_config['segment_length']
        time_offsets = new_config['time_offset']

        new_config['segment_length'] = (segment_lengths['lower'], segment_lengths['upper'])
        new_config['time_offset'] = (time_offsets['lower'], time_offsets['upper'])
        new_config['model'] = SkoptModel(new_config['model'])
        new_config['acquisition'] = SkoptAcquisition(new_config['acquisition'])
        return cls(**new_config)

@dataclass
class SmacParams:
    point_count: Tuple[int, int]
    segment_length: Tuple[int, int]
    time_offset: Tuple[int, int]

    initial_points: int
    total_points: int

    slew_limit: float

    @classmethod
    def from_dict(cls, config):
        waveform = config['Waveform']
        opt = config['Optimization']

        new_config = {**waveform, **opt}

        point_counts = new_config['point_count']
        segment_lengths = new_config['segment_length']
        time_offsets = new_config['time_offset']

        new_config['segment_length'] = (segment_lengths['lower'], segment_lengths['upper'])
        new_config['time_offset'] = (time_offsets['lower'], time_offsets['upper'])
        new_config['point_count'] = (point_counts['lower'], point_counts['upper'])
        return cls(**new_config)
