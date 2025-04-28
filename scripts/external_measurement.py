import numpy as np
from cmt_vna import VNA
import matplotlib.pyplot as plt

vna = VNA()

freqs = vna.setup(fstop=1.e9, npoints=100, source='EXT') #replace BUS with EXT for EXTernal source

plt.ion()
fig,ax = plt.subplots(1,1,figsize=(8,8))
line, = ax.plot(freqs/1e6, np.ones(len(freqs)))
ax.set_xlabel('Frequency (MHz)')
ax.set_ylabel('Out (idk)')
ax.grid()

while True:
    try:
        data = vna.measure_S11()
        line.set_ydata(data)
        fig.canvas.draw()
        fig.canvas.flush_events()
    except KeyboardInterrupt:
        break
