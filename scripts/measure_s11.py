from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import time
from switch_network import SwitchNetwork
from cmt_vna import VNA
import warnings

warnings.filterwarnings("ignore")

parser = ArgumentParser(
    description="Measure S11 of a DUT connected to a VNA.",
    formatter_class=ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    "--osl",
    default=False,
    action="store_true",
    help="Perform calibration measurement.",
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
    "-c",
    "--cadence",
    type=float,
    default=300,
    help="How often to measure S11 in seconds.",
)
parser.add_argument(
    "-m",
    "--max_files",
    type=int,
    default=100,
    help="Maximum number of files to save.",
)
parser.add_argument(
    "--outdir",
    type=str,
    default="/home/charlie/eigsep/CMT-VNA/data",
    help="Output directory.",
)
parser.add_argument(
    "-n",
    "--num_data",
    type=int,
    default=1,
    help="Number of datasets to take each time.",
)
args = parser.parse_args()
snw = SwitchNetwork()  # make switch network object
vna = VNA(ip="127.0.0.1", port=5025, switch_network=snw)
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
    for i in range(args.max_files):
        if args.osl:  # measures standards, saves them to vna object
            vna.add_OSL(std_key="vna")
            snw.switch("VNAANT")

        print(f"reading file {i+1} of {args.max_files}")
        vna.read_data(num_data=args.num_data)
        vna.write_data(outdir=args.outdir)
        print("finished writing")
        time.sleep(args.cadence)
except KeyboardInterrupt:
    print("Keyboard interrupt, exiting.")
    vna.write_data(outdir=args.outdir)  # short final write
finally:
    snw.powerdown()
