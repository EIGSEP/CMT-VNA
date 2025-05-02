import sys
import numpy as np
import matplotlib.pyplot as plt

plt.figure()
for filename in sys.argv[1:]:
    print(f'Reading {filename}')
    npz = np.load(filename)
    freqs, data = npz['freqs'], npz['data']
    plt.plot(freqs/1e6, 20*np.log10(np.abs(data)), label=filename)
plt.legend()
plt.show()
