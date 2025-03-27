'''Script just for me to get calibration data for messing around.'''

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
parser.add_argument("--fstart", type=float, default = 50e6, help='startfreq')
parser.add_argument("--fstop", type=float, default = 250e6, help='stopfreq')

args = parser.parse_args()

vna = VNA(to=1000000, ip='127.0.0.1', port=5025)
freq = vna.setup(
    fstart = args.fstart,
    fstop = args.fstop,
    npoints = args.points,
    ifbw = args.ifbw,
    power_dBm = 0)

vna.add_OSL()
vna.write_data(outdir = args.outdir)
