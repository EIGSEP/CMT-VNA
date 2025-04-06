import numpy as np
from cmt_vna import S911T, calkit
import matplotlib.pyplot as plt
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

parser = ArgumentParser(description='Calibrate and plot S11 data.', 
    formatter_class = ArgumentDefaultsHelpFormatter
)

parser.add_argument('--file', '-f', help='file prefix.')

parser.add_argument('--outdir', default='/home/charlie/eigsep/CMT-VNA/data/', help='where outputs will be saved')

args = parser.parse_args()

vna = VNA()

try:
    sparams = np.load(f'{args.file}_sparams.npz').values()
except FileNotFoundError:
    print('No sparam file.')
try:
    standards = np.load(f'{args.file}_standards.npz').values()
except FileNotFoundError:
    print('No standards file.')
try:
    gammas = np.load(f'{args.file}_gammas.npz').values()
except FileNotFoundError:
    print('No gammas file.')

freqs = gammas['freqs']

