from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from datetime import datetime
import numpy as np
import time
from cmt_vna import VNA
from cmt_vna import S911T
import matplotlib.pyplot as plt
import mistdata.cal_s11 as cal
import warnings
warnings.filterwarnings('ignore')

parser = ArgumentParser(
    description="Measure S11 of a DUT connected to a VNA.",
    formatter_class=ArgumentDefaultsHelpFormatter,
)

parser.add_argument(
    "--cal", default=False, action='store_true', help='calibrate with OSL'
)

parser.add_argument(
    "--plot", default=False, action='store_true', help="Plot."
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
    "-c", "--cadence",
    type=float,
    default=300,
    help="How often to measure S11 in seconds.",
)
parser.add_argument(
    "-m", "--max_files",
    type=int,
    default=100,
    help="Maximum number of files to save.",
)
parser.add_argument(
    "--outdir", type=str, default="/home/charlie/eigsep/CMT-VNA/data", help="Output directory."
)
args = parser.parse_args()


vna = VNA(ip="127.0.0.1", port=5025)
print(f"Connected to {vna.id}.")

freq = vna.setup(
    fstart=args.fstart,
    fstop=args.fstop,
    npoints=args.npoints,
    ifbw=args.ifbw,
    power_dBm=args.power,
)

i = 0
try:
    while i < args.maxfiles:
        if args.cal:
            calkit = S911T(freq) #initialize the calkit

            vna.calibrate_OSL()
            vna.add_sparams(kit=calkit)

        i += 0
        vna.read_data()
        vna.write_data(outdir = args.outdir)
        time.sleep(args.cadence)

except KeyboardInterrupt:
    print('Shutting down.')
    vna.write_data(outdir=args.outdir)




