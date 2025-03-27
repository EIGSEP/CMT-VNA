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
    "-n", "--num_data",
    type=int,
    default=1,
    help="Number of S11s to collect at a time.",
)

parser.add_argument(
    "--outdir", type=str, default="/home/charlie/eigsep/CMT-VNA/data", help="Output directory."
)

parser.add_argument(
    "--nw_sprm_file",default=None, type=str,help="File that contains the s parameters of the network between switches and antenna. Default is None, which means it will only de-embed the vna sparameters."
)

args = parser.parse_args()

i = 0
try:
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

        calkit = S911T(freq) #initialize the calkit

        vna.add_OSL()
        vna.add_sparams(kit=calkit)
        print('Connect DUT and press enter.')
        input()

        plt.ion()
        fig,ax = plt.subplots(2,1,figsize=(8,8), sharex=True)
        ax[0].set_xlabel('Freqs [Hz]')
        ax[0].set_ylabel('S11 [dB]')
        
        ax[1].set_xlabel('Freqs [Hz]')
        ax[1].set_ylabel('S11 Phase [deg]')
        ax[0].grid()
        ax[1].grid()

        vna.start_recording(num_data = args.num_data)
        
        j = 0
        still_plotting = vna._running
        while still_plotting:
            data_keys = list(vna.data.keys())[4+j:]
            if len(data_keys) > 0:
                data = vna.data[data_keys[0]]
                data = vna.de_embed(gamma_meas = data)
                if args.nw_sprm_file:
                    sprms = np.load(args.nw_sprm_file)['sprms']
                    data = vna.de_embed(gamma_meas=data)
                ax[0].plot(freq, 20*np.log10(np.abs(data)))
                ax[1].plot(freq, np.angle(data, deg=True))
                plt.tight_layout()
                fig.canvas.draw()
                plt.pause(1)
                j += 1
                still_plotting = vna._running

        vna.write_data(outdir=args.outdir)
        del vna

        i += 1

        time.sleep(args.cadence)
        
except KeyboardInterrupt:
    print('Shutting down.')

finally:
    try:
        vna.write_data(args.outdir)
        vna.end_recording()
        print('all done')
    except NameError:
        print('all done.')
