"""
Toy targets to test basic functionality of optimization functions without an explicit DUT
"""

import random


def toyopt(height, period):
    """
    Random function to test Bayes Opt
    """
    probp = (period - 500)/(20000-500)
    probh = (height - 0.5)/(2 - 0.5)

    realprob = (probh + probp)/2
    uni = random.uniform(0, 1)

    print(height, period)
    return realprob > uni

def random_target():
    """
    Good luck optimizing this..
    """
    uni = random.uniform(0, 1)
    return uni > 0.5
