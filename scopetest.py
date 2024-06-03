from awgsomefi.scopectrl import SiglentSDS
import numpy as np

import matplotlib.pyplot as plt

scope = SiglentSDS('192.168.0.4')
#scope.get_waveform(3)
#scope.trig_normal()
#vdiv = (scope.get_vdiv(3))
        

scope._write(f"WAV:SOUR C3")
print(scope._ask(b"WAV:SOUR?"))
waveform = scope.get_waveform(scope_channel=3)
##print(waveform)
#
##print(scope._ask(b"*IDN?"))
##desc = scope._ask(b"WAV:DATA?")
##print(desc)
###print(waveform.normalized)
###print(len(waveform.normalized))
#
print(waveform)
plt.plot(waveform.normalized + 3 - 1)
plt.show()
##np.save("./dataset/waveforms/cheb_glitch.npy", waveform.normalized + 3)
##np.save("./dataset/waveforms/spline_glitch.npy", waveform.normalized - 1 + 3)
