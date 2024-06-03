from dataclasses import dataclass, field
import numpy as np

@dataclass
class Resolution:
    """ AWG resolution """
    vertical_bits: int
    horizontal_bits: int

    vertical: int = field(init=False)
    horizontal: int = field(init=False)

    def __post_init__(self):
        """ Find maximum values based on the resolution """
        self.vertical = (1 << self.vertical_bits) - 1
        self.horizontal = (1 << self.horizontal_bits) - 1

    def rescale_horizontal(self, value, domain):
        """ Rescale from the domain to the horizontal resolution """
        return np.interp(value, domain, [0, self.horizontal])

    def rescale_vertical(self, value, domain):
        """ Rescale from voltage range to the vertical resolution """
        return np.interp(value, domain,
                [-self.vertical//2, self.vertical//2])

