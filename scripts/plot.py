import numpy as np
from cmt_vna import S911T, calkit
import matplotlib.pyplot as plt
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

parser = ArgumentParser(description='Calibrate and plot S11 data.', 
    formatter_class = ArgumentDefaultsHelpFormatter
)

parser.add_argument('--file', '-f', help='file data is stored in')

parser.add_argument('--outdir', default='/home/charlie/eigsep/CMT-VNA/data/', help='where outputs will be saved')

args = 
