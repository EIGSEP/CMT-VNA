from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import numpy as np
import time
from cmt_vna import VNA
import matplotlib.pyplot as plt
from cmt_vna import calkit as cal
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
    "--plot",
    default=False,
    action="store_true",
    help="If true, output calibrated plot.",
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
parser.add_argument(
    "--sprm_file",
    default=None,
    help=(
        "file that holds the sparameters of the cable system. Adds the "
        "sparameters to the vna object, which is then written to file.",
    ),
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
    if args.osl:  # measures standards, saves them, uses them to calibrate meas
        calkit = cal.S911T(freq_Hz=freq)
        vna.add_OSL(std_key="vna")
        vna.add_sparams(kit=calkit, sprm_key="vna", std_key="vna")
        if args.sprm_file is not None:
            cable_sparams = np.load(args.sprm_file)["cable"]
            vna.sparams["cable"] = cable_sparams

    print("Calibration complete.")
    print("Connect DUT and hit enter")
    input()

    try:
        print("reading")
        vna.read_data(num_data=args.num_data)
        print("done reading")
        if args.osl:
            gamma_cals = vna.calibrate_gammas(
                sprm_keys=list(vna.sparams.keys())
            )
        if args.plot:
            plt.ion()
            fig, ax = plt.subplots(2, 1, figsize=(8, 8))
            ax[0].set_xlabel("freqs [Hz]")
            ax[0].set_ylabel("S11 Mag [dB]")
            ax[0].grid()
            ax[1].set_xlabel("freqs [Hz]")
            ax[1].set_ylabel("S11 Phase [deg]")
            ax[1].grid()
            if args.osl:
                ax[0].plot(freq, 20 * np.log10(gamma_cals.T))
                ax[1].plot(freq, np.angle(gamma_cals, deg=True).T)
            else:
                ax[0].plot(
                    freq, 20 * np.log10(np.array(list(vna.gammas.values())).T)
                )
                ax[1].plot(
                    freq,
                    np.angle(np.array(list(vna.gammas.values())), deg=True).T,
                )

            plt.show()

    except KeyboardInterrupt:
        break
    finally:
        i += 1
        vna.write_data(outdir=args.outdir)
        time.sleep(args.cadence)
        print("finished writing")
