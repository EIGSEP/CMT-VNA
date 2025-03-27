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
    "--osl", default=False, action='store_true', help="Perform calibration measurement."
)
parser.add_argument(
    "--cal", default=None, help="File with which to calibrate."
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


i = 0
while i < args.max_files:
    vna = VNA(ip="127.0.0.1", port=5025)
    print(f"Connected to {vna.id}.")

    freq = vna.setup(
        fstart=args.fstart,
        fstop=args.fstop,
        npoints=args.npoints,
        ifbw=args.ifbw,
        power_dBm=args.power,
    )

    if args.osl: #measures standards, saves them, uses them to calibrate meas
        calkit = S911T(freq_Hz=freq)
        vna.add_OSL()
        vna.add_sparams(kit=calkit)
    if args.cal:
        calkit = S911T(freq_Hz=freq)
        vna.from_file(args.cal)
        vna.add_sparams(kit=calkit)

    print("Calibration complete.")
    print("Connect DUT and hit enter")
    input()

    if not vna._running:
        vna._running = True
    try:
        vna.read_data(num_data = args.num_data)
        vna.write_data(outdir=args.outdir)
        del vna 
        time.sleep(args.cadence)
    except KeyboardInterrupt:
        vna.write_data(outdir=args.outdir)
        break
    finally:
        i += 1
        print('finished writing')
