import numpy as np
import matplotlib.pyplot as plt
from cmt_vna import VNA

vna = VNA()
freqs = vna.setup(fstart=250e6, fstop=1.8e9, power_dBm=0)
data = vna.measure_S11()

plt.figure()
plt.plot(freqs/1e6, 20*np.log10(np.abs(data)))
plt.show()
