from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from datetime import datetime
import numpy as np
from cmt_vna import VNA
from cmt_vna import calkit as cal
import warnings

warnings.filterwarnings("ignore")

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
    "--outdir",
    type=str,
    default="/home/charlie/eigsep/CMT-VNA/data",
    help="Output directory.",
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

calkit = cal.S911T(freq_Hz=freq)
model_stds = calkit.std_gamma

print("Measuring standards at the VNA port")
vna.add_OSL(std_key="vna")

print("Measuring at the top of the cable")
vna.add_OSL(std_key="cable")

# get vna sparams
vna_sprms = calkit.sparams(stds_meas=vna.data["vna"])
sparams = {"vna": vna_sprms}

# de-embed vna sprms from cable standards
cable_ref_vna_stds = cal.calibrate(
    kit=calkit, gammas=vna.data["cable"], sprms_dict=sparams
)
vna.data["cable_ref_vna"] = cable_ref_vna_stds

# get cable sparams
cable_sprms = calkit.sparams(stds_meas=vna.data["cable_ref_vna"])
sparams["cable"] = cable_sprms

date = datetime.now().strftime("%Y%m%d_%H%M%S")
np.savez(f"{args.outdir}/{date}_sparams.npz", **sparams)

vna.write_data(args.outdir)
