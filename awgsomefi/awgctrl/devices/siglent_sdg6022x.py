import struct

from typing import List, Dict

from awgsomefi.parameters.voltage import VoltageBound

from .awggeneric import AwgGeneric, ChannelID
from ..parameters import CommonWave, SquareWave, ArbWave, Resolution, OperationMode, SineWave, PulseWave

class SiglentSDG6022x(AwgGeneric):
    channels = 2
    channel_voltages = {}


    def enable_channel(self, channel: ChannelID):
        self._write(F"C{channel}:OUTP ON")

    def disable_channel(self, channel: ChannelID):
        self._write(F"C{channel}:OUTP OFF")

    def combine_channels(self, channel: ChannelID):
        command = f"C{channel}:CMBN ON"
        self._write(command)

    def set_trig_delay(self, channel: ChannelID, length):
        command = f"C{channel}:BTWV DLAY,{length*10**-9:.9f}"
        self._write(command)
        self.wait_complete()

    def setup_arbitrary(self, channel: ChannelID, name: str, wave: ArbWave, mode: OperationMode = OperationMode.BURST):

        self.set_operation_mode(channel, mode)
        def _setup_common(wave: ArbWave):
            command = (
                f"FREQ,{wave.frequency},"
                f"AMPL,{self.channel_voltages[channel].amplitude},"
                f"OFST,{self.channel_voltages[channel].offset},"
                f"PHASE,{wave.phase},"
            )
            return command

        def _points_to_stream(data: List[int]) -> bytes:
            extData = [data[0]] * 20
            extData.extend(data)
            extData.extend([data[-1]]* 20)
            result = b''.join([struct.pack('<h', point) for point in extData])
            return result

        command = f"C{channel}:WVDT WVNM,{name},".encode()

        command += _setup_common(wave).encode()

        # Create a named waveform
        data = b"WAVEDATA," + _points_to_stream(wave.waveform)
        self._write_raw(command + data)

        self.wait_complete()

        # Set channel to the waveform
        self._write(f"C{channel}:ARWV NAME,{name}")

        # Set DDS mode to avoid external stuttering
        self._write(f"C{channel}:SRATE MODE,DDS")

        self.wait_complete()

    def setup_pulse(self, channel: ChannelID, pulse: PulseWave):
        def _setup_common(wave: CommonWave):
            command = (
                f"FRQ,{wave.frequency},"
                f"AMP,{self.channel_voltages[channel].amplitude},"
                f"OFST,{self.channel_voltages[channel].offset},"
            )
            return command

        command =  f"C{channel}:BTWV STATE,ON,"
        command += f"TRSR,EXT,DUTY,99.999,"
        command += "CARR,WVTP,PULSE,"
        command += _setup_common(pulse)
        command += f"FALL,{pulse.fall/10**9:.9f}"

        self._write(command)

        self.wait_complete()

        self._write("C{channel}:OUTP PLRT,INVT")

    def setup_dc(self, channel: ChannelID, voltage: float):
        command = f"C{channel}:BSWV WVTP,DC,OFST,{voltage}"
        self._write(command)

    def setup_square(self, channel: ChannelID,  wave: SquareWave):
        def _setup_common(wave: SquareWave):
            command = (
                f"FRQ,{wave.frequency},"
                f"HLEV,{self.channel_voltages[channel].high},"
                f"LLEV,{self.channel_voltages[channel].low},"
                f"PHASE,{wave.phase},"
            )
            return command
        command  = f"C{channel}:BSWV WVTP,SQUARE,"
        command += _setup_common(wave)
        command += f"DUTY,{wave.duty}"
        self._write(command)

    def setup_sine(self, channel: ChannelID, wave: SineWave):
        def _setup_common(wave: SineWave):
            command = (
                f"FRQ,{wave.frequency},"
                f"AMPL,{self.channel_voltages[channel].amplitude},"
                f"OFST,{self.channel_voltages[channel].offset},"
                f"PHASE,{wave.phase},"
            )
            return command
        command  = f"C{channel}:BSWV WVTP,SINE,"
        command += _setup_common(wave)
        self._write(command)


    def get_channel_wave(self, channel: ChannelID) -> bytes:
        return self._ask_raw(f"C{channel}:ARWV?".encode())

    def set_load(self, channel: ChannelID, resistance=None, hiZ=False):
        if resistance is None and hiZ:
            load = "HZ"

        elif resistance is not None and not hiZ:
            if 50 <= resistance <= 100000:
                load = resistance
            else:
                raise ValueError("Resistance must be between 50 and 100000")

        else:
            raise ValueError("Set either 'hiZ' OR value for 'resistance'")

        self._write(f"C{channel}:OUTP LOAD,{load}")

    # Burst state: ON
    # Trigger: external
    # Time: 1 cycle
    def set_operation_mode(self, channel: ChannelID, mode: OperationMode):
        if mode == OperationMode.BURST:
            self._write(f"C{channel}:BTWV STATE,ON,TRSR,EXT,TIME,1")
        elif mode == OperationMode.SWEEP:
            pass
            #self._write(f"C{channel}:SWWV STATE,ON")
        else:
            raise ValueError("Invalid Operation Mode")

    def set_polarity_normal(self, channel: ChannelID):
        self._write(f"C{channel}:OUTP PLRT,NOR")

    def set_polarity_invert(self, channel: ChannelID):
        self._write(f"C{channel}:OUTP PLRT,INVT")

    def protect_on(self):
        self._write("VOLTPRT ON")

    def reset(self):
        return self._write("*RST")

    def wait_complete(self):
        return self._ask("*OPC?")

    @property
    def sysinfo(self):
        return self._ask("*IDN?")

    @property
    def properties(self) -> Dict:
        return {
            "resolution": Resolution(vertical_bits=16, horizontal_bits=12)
        }
