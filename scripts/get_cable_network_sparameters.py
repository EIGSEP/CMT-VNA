'''Script for finding the s-parameters of a cable network.Takes OSL standards measurements at the vna port and then OSL standards for each string in the list variable sparams_to_find. Saves the s-parameters of network represented to separate npzs, then writes all the OSL standards measured to another file.
'''
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from datetime import datetime
import numpy as np
from cmt_vna import VNA
from switch_network import SwitchNetwork
from cmt_vna import calkit as cal
import warnings

warnings.filterwarnings("ignore")

parser = ArgumentParser(
    description='Script for finding the s-parameters of a cable network.', 
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
    "--outdir",
    type=str,
    default="/home/charlie/eigsep/CMT-VNA/data",
    help="Output directory.",
)

args = parser.parse_args()

sparams_to_find = ['VNAANT', 'VNAN', 'VNAO', 'VNAS', 'VNAL']

i = 0
snw = SwitchNetwork()
vna = VNA(ip="127.0.0.1", port=5025, switch_nw=snw)
print(f"Connected to {vna.id}.")
freq = vna.setup(
    fstart=args.fstart,
    fstop=args.fstop,
    npoints=args.npoints,
    ifbw=args.ifbw,
    power_dBm=args.power,
)
calkit = cal.S911T(freq_Hz=freq)
model_stds = calkit.std_gamma

print("Measuring standards at the VNA port")
vna.add_OSL(std_key="vna")
try:
    for n in sparams_to_find:
        snw.switch(n, verbose=True) 
        print(f"Measuring at the top of the nw {n}")
        vna.add_OSL(std_key=f"{n}")
        
        # get vna sparams
        vna_sprms = calkit.sparams(stds_meas=vna.data["vna"])
        sparams = {"vna": vna_sprms}
        
        # de-embed vna sprms from nw standards
        nw_ref_vna_stds = cal.calibrate(
            gammas=vna.data[f"{n}"], sprms_dict=sparams
        )
        vna.data[f"{n}_ref_vna"] = nw_ref_vna_stds
        
        # get nw sparams
        nw_sprms = calkit.sparams(stds_meas=vna.data[f"{n}_ref_vna"])
        sparams[f"{n}"] = nw_sprms
        
        date = datetime.now().strftime("%Y%m%d_%H%M%S")
        np.savez(f"{args.outdir}/{date}_{n}_sparams.npz", **sparams)
except KeyboardInterrupt:
    print('exiting...')
finally:
    vna.write_data(args.outdir)
