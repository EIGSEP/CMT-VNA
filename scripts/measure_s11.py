from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from datetime import datetime
import numpy as np
import time
from cmt_vna import VNA
import matplotlib.pyplot as plt
from cmt_vna import calkit as cal
import warnings
warnings.filterwarnings('ignore')

parser = ArgumentParser(
    description="Measure S11 of a DUT connected to a VNA.",
    formatter_class=ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    "--osl", default=False, action='store_true', help="Perform calibration measurement."
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
parser.add_argument(
    "-n", "--num_data",
    type=int,
    default=1,
    help="Number of datasets to take each time.",
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
while i < args.max_files:
    if args.osl: #measures standards, saves them to vna object
        calkit = cal.S911T(freq_Hz=freq)
        vna.add_OSL(std_key='vna')
        print("Calibration complete.")
    
    print("Connect DUT and hit enter")
    input()

    try:
        print('reading')
        vna.read_data(num_data = args.num_data)
        print('done reading')
       
    except KeyboardInterrupt:
        break
    finally:
        i += 1
        vna.write_data(outdir=args.outdir)
        time.sleep(args.cadence)
        print('finished writing')
