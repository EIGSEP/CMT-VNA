from mistdata.cal_s11 import CalKit, CalStandard
from mistdata import cal_s11 
import numpy as np

class BasicLoadStandard:
    def __init__(self, impedance, Z0=50):
        self.impedance = impedance
        self.Z0 = Z0
    
    @property
    def gamma(self):
        return cal_s11.impedance_to_gamma(self.impedance, self.Z0) 

class S911T(CalKit):
    def __init__(self, freq_Hz, match_resistance=50):
        """
        Values for EIGSEP calibration kit.

        Parameters:
            freq_Hz (np.array of floats) : Frequency Range in Hz.
            match_resistance (float) : Resistance of match standard in ohms.
        """

        Z0 = 50

        #open standard 
        c_coefs = (-7.425E-15, 2470E-27, -226E-36, 6.18E-45)
        c_open = np.polyval(c_coefs, freq_Hz)
        open_delay = 30.821E-12 #s
        open_loss = 2E9 #Ohm/s

        #short standard
        l_coefs = (27.98E-12, -5010E-24, 303.8E-33, -6.13E-42)
        l_short = np.polyval(l_coefs, freq_Hz)
        short_delay = 30.688E-12 #s
        short_loss = 2E9 #Ohm/s

        #load standard
        load_Z = 50 #Ohm
        load = np.ones(len(freq_Hz)) * load_Z

        super().__init__(freq_Hz, Z0=Z0)
        self.add_open(c_open, open_loss, open_delay)
        self.add_short(l_short, short_loss, short_delay)
        self.load = BasicLoadStandard(load)

    @property
    def std_gamma(self):
        open_gamma = self.open.gamma
        shor_gamma = self.short.gamma
        load_gamma = self.load.gamma
        gamma = np.vstack([open_gamma, shor_gamma, load_gamma])
        return gamma
