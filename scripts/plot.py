import sys
import numpy as np
from cmt_vna import calkit as cal
from cmt_vna import VNA
import matplotlib.pyplot as plt
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

parser = ArgumentParser(description='Calibrate and plot S11 data.', 
    formatter_class = ArgumentDefaultsHelpFormatter
)

parser.add_argument('--file', '-f', help='file prefix.')
parser.add_argument('--outdir', default='/home/charlie/eigsep/CMT-VNA/data/', help='where outputs will be saved')

args = parser.parse_args()

vna = VNA()

try:
    sparams_file = np.load(f'{args.file}_sparams.npz')
    sparams = dict(sparams_file.items())
except FileNotFoundError:
    print('No sparam file.')
try:
    gammas_file = np.load(f'{args.file}_gammas.npz')
    gammas = dict(gammas_file.items())
except FileNotFoundError:
    print('No gammas file.')

freqs = gammas.pop('freqs')

calkit=cal.S911T(freq_Hz=freqs)

try:
    assert len(gammas) > 0
except AssertionError:
    print('No gammas in your file to plot. Exiting...')
    sys.exit(1)

gammas_cal = vna.calibrate_gammas(sprm_keys=list(gammas.keys()))

plt.ion()
fig,ax = plt.subplots(2,1, figsize=(8,8), sharex=True)
ax[0].plot(freqs/1e6, 20*np.log10(np.abs(gammas_cal.T)))
ax[0].set_ylabel('S11 Mag [dB]')
ax[0].grid()

ax[1].plot(freqs/1e6, np.angle(gammas_cal.T, deg=True))
ax[1].set_ylabel('S11 Phase (deg)')
ax[1].set_xlabel('Freqs [MHz]')
ax[1].grid()

plt.suptitle('S11 Graphs')

plt.show()










