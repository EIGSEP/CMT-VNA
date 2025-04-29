import numpy as np
import matplotlib.pyplot as plt
from cmt_vna import VNA

vna = VNA()
freqs = vna.setup(fstart=250e6, fstop=1.8e9, npoints=1000, power_dBm=0)
#input('please connect the jank board and press enter.')
jank_data = vna.measure_S11()
#print(len(jank_data))
#input('please connect the rocketship board and press enter.')
#rocketship_data = vna.measure_S11()
#print(len(rocketship_data))

plt.figure()
plt.plot(freqs/1e6, 20*np.log10(np.abs(jank_data)), label='jank board')
#plt.plot(freqs/1e6, 20*np.log10(np.abs(rocketship_data)), label='rocketship board')
plt.legend()
plt.show()
