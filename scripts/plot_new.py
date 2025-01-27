import argparse
import numpy as np
import matplotlib.pyplot as plt
import os
import time
import matplotlib
from datetime import datetime
from cmt_vna import S911T
from mistdata import cal_s11 as cal
import warnings
warnings.filterwarnings('ignore')

def calibrate(cal_file, calkit, s11):
    """
    Calibrate the s11 data we're plotting.

    Parameters:
        cal_file (str): Path to npz file, must contain keyword arguments "open", "short", "load"
        s11 (np.array): Array containing s11 data. Must have same number of points as data in cal_file.

    Returns:
        np.array: Calibrated data.
    """
    osl_data = np.load(cal_file)
    open_data = osl_data['open']
    shor_data = osl_data['short']
    load_data = osl_data['load']
    gamma_measured = np.vstack([open_data, shor_data, load_data])

    gamma_true = calkit.std_gamma

    sparams = cal.network_sparams(gamma_true, gamma_measured)
    gamma_prime = cal.embed_sparams(sparams, s11)
    return gamma_prime    

def load_npz_data(filename, cal_file=None, calkit=None):
    """
    Load data from a .npz file.

    Parameters:
        filename (str): Path to the .npz file to load.
        cal_file (None or str): Points to the calibration file to be used.

    Returns:
        numpy.lib.npyio.NpzFile: The loaded data object, or None if loading fails.
    """
    try:
        data = np.load(filename)['s11']
        if cal_file:
            data = calibrate(cal_file, calkit, s11)
        return data
    except:
        print('Unable to load file. Returning None')
        return None

def live_plot(freq, s11_file, live_dir, output_filename, cal_file=None):
    """
    Continuously check a directory for new .npz files and plot new data on top of the existing plot.

    Parameters:
        freq (str): Frequency data filename.
        s11_data (str): Initial S11 file.
        live_dir (str): Directory to watch for new .npz files.
        output_filename (str): File to which the plot figure will be saved.
        cal_file (None or str): If none, it will plot raw S11.
    """
    if cal_file:
        calkit = S911T(freq_Hz=freq) #initialize calkit object here, pass to load_npz_data
        s11_data = load_npz_data(s11_file, cal_file=cal_file, calkit=calkit)
    else:
        s11_data = load_npz_data(s11_file)
    plt.ion()  # Enable interactive mode
    fig, ax = plt.subplots(figsize=(10, 6))
    s11_line, = ax.plot(freq, 20*np.log10(np.abs(s11_data)), label=f"S11 ({s11_file[-19:-4]})", color="tab:red")

    ax.set_xlabel("Frequency")
    ax.set_ylabel("Data")
    ax.set_title("S11 Data")
    ax.grid(True)
    plt.tight_layout()
    
    time_to_beat = s11_file
    try:
        while True:
            new_files = [os.path.join(live_dir,i) for i in os.listdir(live_dir) if (os.path.join(live_dir, i) > time_to_beat) & ('npz' in i)]
            if len(new_files) > 0:
                time_to_beat = new_files[-1]
                time.sleep(1)
                for i in new_files:
                    if cal_file:
                        s11_data = load_npz_data(i, cal_file=cal_file)
                    else:
                        s11_new = load_npz_data(i) 
                    ax.plot(freq, 20*np.log10(np.abs(s11_new)), label=f"S11 ({i[-19:-4]})", alpha=0.7)
                    plt.draw()
                    plt.pause(0.1)
    except:
        plt.savefig(output_filename)
                

def main():
    """
    Main function to parse arguments, load data, and plot the results.
    """
    parser = argparse.ArgumentParser(description="Load and plot data from .npz files.")
    parser.add_argument("s11", help="Path to the S11 .npz file.")
    parser.add_argument("--output", default=None, help="Filename to save the figure (optional).")
    parser.add_argument("--live", default=None, help="Directory to watch for live S11 data.")
    parser.add_argument("--cal", default=False, action="store_true", help="If True, will automatically calibrate s11 data before plotting. Default is False.")
    args = parser.parse_args()

    # Load data from the provided files
    try:
        freq_file = max(os.listdir(f'{args.live}/freqs'))
    except:
        print('no frequency file to pull from. exiting')
        return
    freq = np.load(os.path.join(f'{args.live}/freqs', freq_file))['freq']

    if args.cal:
        live_plot(freq, args.s11, args.live, args.output, max(os.listdir(f'{args.live}/cals')))
    else:
        live_plot(freq, args.s11, args.live, args.output)

if __name__ == "__main__":
    main()

