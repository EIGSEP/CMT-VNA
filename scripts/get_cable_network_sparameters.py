from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from datetime import datetime
import numpy as np
import time
from cmt_vna import VNA
from cmt_vna import S911T
from cmt_vna import calkit as cal
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

parser = ArgumentParser(
    description="Measure S11 of a DUT connected to a VNA.",
    formatter_class=ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    "--fstart", type=float, default=1e6, help="Start frequency in Hz."
)
parser.add_argument(
    "--fstop", type=float, default=250e6, help="Stop frequency in Hz."
)
parser.add_argument(
    "--npoints", type=int, default=1001, help="Number of frequency points."
)
parser.add_argument(
    "--ifbw", type=float, default=100, help="IF bandwidth in Hz."
)
parser.add_argument(
    "--power", type=float, default=-40, help="Power level in dBm."
)
parser.add_argument(
    "--outdir", type=str, default="/home/charlie/eigsep/CMT-VNA/data", help="Output directory."
)

args = parser.parse_args()

i = 0
vna = VNA(ip="127.0.0.1", port=5025)
print(f"Connected to {vna.id}.")
freq = vna.setup(
    fstart=args.fstart,
    fstop=args.fstop,
    npoints=args.npoints,
    ifbw=args.ifbw,
    power_dBm=args.power,
)

calkit = S911T(freq_Hz = freq)
model_stds = calkit.std_gamma

print('Measuring standards at the VNA port')
OSL = vna.measure_OSL() #gets osl standards at vna
OSL_arr = np.array([d for key, d in OSL.items()])

#vna s parameters 
vna_sprms = cal.network_sparameters(gamma_true=model_stds, gamma_meas=OSL_arr)

print("Measuring at the top of the cable")
OSL_cable = vna.measure_OSL()
OSL_cable_arr = np.array([d for key, d in OSL_cable.items()])

#De embed vna sparameters from the standards at the cable port
OSL_cable_ref_vna = cal.de_embed_sparams(sparams=vna_sprms, gamma_prime=OSL_cable_arr)

#compare the cable measurements with vna sprm de-embedded to the models
cable_nw_sprms = cal.network_sparams(gamma_true=model_stds, gamma_meas=OSL_cable_ref_vna)

date = datetime.now().strftime('%Y%m%d_%H%M%S')
np.savez(f'{outdir}/{date}_cable_new_sprms.npz',freqs=freq, sprms=cable_nw_sprms)
np.savez(f'{outdir}/{date}_vna_stds.npz',**OSL)
np.savez(f'{outdir}/{date}_cable_stds.npz', **OSL_cable) 

