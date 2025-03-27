from cmt_vna import S911T, VNA
import numpy as np
import matplotlib.pyplot as plt
import time

vna = VNA()
freq= vna.setup(npoints=100)
calkit = S911T(freq_Hz = freq)

vna.add_OSL()
print('Calibration data taken. Connect DUT and press enter.')
input()
vna.add_sparams(kit=calkit)

vna.start_recording(num_data=5)

plt.ion()
fig,ax = plt.subplots(1,1)
ax.set_xlabel('Freqs [Hz]')
ax.set_ylabel('S11 [dB]')
ax.grid()
try:
    i = 0
    while True:
        data_keys = list(vna.data.keys())[4+i:]
        if len(data_keys) > 0:
            data = vna.data[data_keys[0]]
            data_cal = vna.de_embed(gamma_meas = data)
            ax.plot(freq, 20*np.log10(np.abs(data_cal)), label=data_keys[0])
            ax.legend()
            fig.canvas.draw()
            i += 1
            plt.pause(1)
except KeyboardInterrupt:
    print('shutting down')
finally:
    vna.write_data('/home/charlie/eigsep/CMT-VNA/data')
    plt.show()
    vna.end_recording()
