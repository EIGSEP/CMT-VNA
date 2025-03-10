from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from datetime import datetime
import numpy as np
import time
from cmt_vna import VNA

parser = ArgumentParser(
    description="Measure S11 of a DUT connected to a VNA.",
    formatter_class=ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    "--cal", default=False, action='store_true', help="Perform calibration."
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

if args.cal:
    OSL = vna.calibrate_OSL()
    date = datetime.now().strftime("%Y%m%d_%H%M%S")
    #save calibration data
    np.savez(f"{args.outdir}/cals/{date}_calibration.npz", open=OSL['open'], short=OSL['short'], load=OSL['load'], freqs= freq)
    print("Calibration complete.")
    print("Connect DUT and hit enter")
    input()

i = 0
while i < args.max_files:
    try:
        gamma = vna.measure_S11(verbose=True)
        date = datetime.now().strftime("%Y%m%d_%H%M%S")
        np.savez(f"{args.outdir}/{date}.npz", gamma=gamma, freqs = freq)
        i += 1
        time.sleep(args.cadence)
    except KeyboardInterrupt:
        break
