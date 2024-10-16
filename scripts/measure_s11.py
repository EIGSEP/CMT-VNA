from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from time import sleep
from cmt_vna import VNA

parser = ArgumentParser(
    description="Measure S11 of a DUT connected to a VNA.",
    formatter_class=ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    "--cal", type=bool, default=True, help="Perform calibration."
)
parser.add_argument(
    "--fstart", type=float, default=1e6, help="Start frequency in Hz."
)
parser.add_argument(
    "--fstop", type=float, default=250e6, help="Stop frequency in Hz."
)
parser.add_argument(
    "--npoints", type=int, default=1601, help="Number of frequency points."
)
parser.add_argument(
    '--ifbw', type=float, default=1e3, help='IF bandwidth in Hz.'
)
parser.add_argument(
    '--power', type=float, default=-10, help='Power level in dBm.'
)
parser.add_argument(
    "--cadence",
    type=float, 
    default=300,
    help="How often to measure S11 in seconds.",
)
parser.add_argument(
    "--max_files",
    type=int,
    default=100,
    help="Maximum number of files to save.",
)
parser.add_argument(
    "--outdir", type=str, default=".", help="Output directory."
)
args = parser.parse_args()


vna = VNA(ip="127.0.0.1", port=5025)
print(f"Connected to {vna.id}.")

if args.cal:
    vna.calibrate_OSL()
    print("Calibration complete.")

vna.setup_S11(
    fstart=args.fstart,
    fstop=args.fstop,
    npoints=args.npoints,
    ifbw=args.ifbw,
    power_dBm=args.power,
)

i = 0
while i < args.max_files:
    try:
        freq, s11 = vna.measure_S11()
        np.savez(f"{args.outdir}/s11_{i}.npz", freq=freq, s11=s11)
        i += 1
    except KeyboardInterrupt:
        break
