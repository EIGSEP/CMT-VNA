import argparse
import numpy as np
import matplotlib.pyplot as plt
import os
import time
import matplotlib
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def load_npz_data(filename):
    """
    Load data from a .npz file.

    Parameters:
        filename (str): Path to the .npz file to load.

    Returns:
        numpy.lib.npyio.NpzFile: The loaded data object, or None if loading fails.
    """
    try:
        data = np.load(filename)['s11']
        return data
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

def live_plot(freq, s11_file, live_dir, output_filename):
    """
    Continuously check a directory for new .npz files and plot new data on top of the existing plot.

    Parameters:
        freq (str): Frequency data filename.
        s11_data (str): Initial S11 file.
        live_dir (str): Directory to watch for new .npz files.
        output_filename (str): File to which the plot figure will be saved.
    """
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
            new_files = [os.path.join(live_dir,i) for i in os.listdir(live_dir) if (os.path.join(live_dir, i) > time_to_beat) & ('freq' not in i)]
            if len(new_files) > 0:
                time_to_beat = new_files[-1]
                time.sleep(1)
                for i in new_files:
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
    parser.add_argument("freq", help="Path to the frequency .npz file.")
    parser.add_argument("s11", help="Path to the S11 .npz file.")
    parser.add_argument("--output", default=None, help="Filename to save the figure (optional).")
    parser.add_argument("--live", default=None, help="Directory to watch for live S11 data.")

    args = parser.parse_args()

    # Load data from the provided files
    freq_data = np.load(args.freq)
    s11_data = load_npz_data(args.s11)

    if freq_data is None or s11_data is None:
        print("Failed to load one or more files. Exiting.")
        return

    try:
        freq = freq_data["freq"]
        s11 = s11_data
    except KeyError as e:
        print(f"Missing expected data in one of the files: {e}")
        return

    live_plot(freq, args.s11, args.live, args.output)

if __name__ == "__main__":
    main()

