# `awgsomefi`: Arbitrary Waveform Voltage Fault Injection

This repository contains the waveform generating framework 'awgsomefi' that is used in the paper "Analysis of Arbitrary Waveform Generation for Voltage Glitches" published at FDTC 2023.

Please note that this code was not specifically prepared for use by others. There is no tutorial, documentation, or other goodies to make this more polished. This is primarily intended as additional proof of our work and to encourage collaborations.

This code is released under the license terms of the Apache 2.0 license (see LICENSE). Copyright: 2023-2024 by Vincent Immler.

## Setup and Installation
This repository is tested only on Linux (Ubuntu 22 LTS) so we will be using `bash` commands. It assumes access to an STM32F0308DISCOVERY board as the debug protocol for Renesas 78K0R chips was implemented using this board.

1. Make sure you have access to the [fmpi-stm32f0](https://github.com/decryptofy/debug-renesas-fmpi-stm32f0) repository and have SSH setup to clone from it.

2. The repository is tested on Python 3.10, but couple earlier version of Python 3 should also work.

```console
$ python --version
Python 3.10.6
```

3. Create a virtual environment `python -m venv venv` and activate it `source venv/bin/activate`

4. install all required packages with `pip install -r requirements.txt`

5. Look through configuration files at `awgsomefi/config/configurations/*.yaml` and modify as needed

6. Try running `python driver.py`

7. Run `deactivate` when done using the virtual environment



## `awgsomefi` Modules
- `config`: Configuring the framework

  The configurations live here as YAML files.
  Includes information such as voltages for the fault injections, parameters for waveform searching, and instrument information such as IP addresses to connect to using `vxi11`.

- `oceangen`: Waveform generation

   Responsible for generating different types of glitch waveforms (e.g. using Hermite splines) and searching for optimal waveform using [skopt](https://github.com/scikit-optimize/scikit-optimize) and [SMAC3](https://github.com/automl/SMAC3)

- `targets`: Interface with Device Under Test (DUT) through the STM32 controller

  Contains algorithms and procedures running the attacks on the Renesas 78K0R as well as conducting loop escape tests.

- `awgctrl`, `psuctrl`, and `scopectrl`: Instrument controllers

  `awgctrl` is thoroughly used in the framework. `psuctrl` should work, but wasn't needed since we never had to power-cycle the power supply. `scopectrl` used *experimentally* in `feature_radar` to extract the waveform captured by the oscilloscope.

- `enforcer`: Waveform generation with Reinforcement Learning.

  **Experimental**! Likely needs to be rewritten.


## Additional Modules
- `fourier`: Waveform Analysis and Plotting

  Can be used to generate plots from captured waveforms.
  Supports various modes of Fourier and wavelet transforms.

- `histograms`: Glitch Sweeping

  Sweeping timing for the 78K0R glitches showcasing the bytes in memory that are leaked.
  Histograms are recorded as json files and plots can be generated using `parse.py`
