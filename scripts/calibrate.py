import numpy as np
from cmt_vna import VNA
from datetime import datetime
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

parser = ArgumentParser(
    description="Get standards measurements.",
    formatter_class = ArgumentDefaultsHelpFormatter)

parser.add_argument("--outdir", type=str, default='/home/charlie/eigsep/CMT-VNA/data', help='Output directory')
parser.add_argument("--points", type=int, default=1001, help='npoints to collect')
parser.add_argument("--ifbw", type=int, default=100, help='if bandwidth [Hz]')
args = parser.parse_args()

vna = VNA(to=1000000, ip='127.0.0.1', port=5025)
freq = vna.setup(
    fstart = 50e6,
    fstop = 250e6,
    npoints = args.points,
    ifbw = args.ifbw,
    power_dBm = 0)

date = datetime.now().strftime("%Y%m%d_%H%M%S")
np.savez(f'{args.outdir}/{date}_freqs.npz', freq=freq)

OSL = vna.calibrate_OSL()
date = datetime.now().strftime("%Y%m%d_%H%M%S")
np.savez(f'{args.outdir}/{date}_calibration.npz', open=OSL['open'], short=OSL['short'], load=OSL['load'])
