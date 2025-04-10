import sys
import numpy as np
from cmt_vna import calkit as cal
from cmt_vna import VNA
import matplotlib.pyplot as plt
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

parser = ArgumentParser(description='Calibrate and plot S11 data.', 
    formatter_class = ArgumentDefaultsHelpFormatter
)

parser.add_argument('--file', '-f', help='data file.')
parser.add_argument('--sprm_file', '-s', default=None, help='file containing cable sparams.')
parser.add_argument('--outdir', default='/home/charlie/eigsep/CMT-VNA/data/', help='where outputs will be saved')

args = parser.parse_args()

data_file = np.load(args.file)
data = dict(data_file.items())

sparams_file = np.load(args.sprm_file)
if len(sparams_file.keys()) > 1:
    print(f'Theres more than one sparam dataset here: {list(sparams_file.keys())}. Which do you want to keep?')
    decision = input()
    cable_sparams = sparams_file[decision]
else:
    cable_sparams = np.array([sparams_file.values()])

freqs = gammas.pop('freqs')
sparams = dict()

freqs = data.pop('freqs')
try:
    vna_stds = data.pop('vna')
except KeyError:
    print('No vna standards, not supported by this script. Exiting...')
    sys.exit(1)

calkit=cal.S911T(freq_Hz=freqs)

#getting the vna sparameters
vna_sprms = calkit.sparams(stds_meas=vna_stds)

#adding all sparams to sparam dict
sparams['vna'] = vna_sprms
sparams['balun_cable'] = cable_sparams

try: #if theres nada after extracting freqs and osl, can't do anything
    assert len(data) > 0
except AssertionError:
    print('No gammas in your file to plot. Exiting...')
    sys.exit(1)

#calibrate all gammas wrt all sparams in sparams dict
gammas_cal = vna.calibrate(kit=calkit, gammas=np.array(list(data.values())), sprms_dict=sparams)

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

plt.show(block=True)

