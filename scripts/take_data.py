import numpy as np
import sys
from cmt_vna import VNA

#FSTART, FSTOP = 250e6, 1.8e9
#FSTART, FSTOP = 50e6, 250e6
FSTART, FSTOP = 10e6, 1e9

assert len(sys.argv) == 2
filename = sys.argv[-1]
vna = VNA()
freqs = vna.setup(fstart=FSTART, fstop=FSTOP,npoints=1000, power_dBm=0)
data = vna.measure_S11()
print(f'Saving to {filename}')
np.savez(filename, freqs=freqs, data=data)
