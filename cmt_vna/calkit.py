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
        c_coefs = ( 6.18E-45,-226E-36, 2470E-27,-7.425E-15)
        c_open = np.polyval(c_coefs, freq_Hz)
        open_delay = 30.821E-12 #s
        open_loss = 2E9 #Ohm/s

        #short standard
        l_coefs = (-6.13E-42,303.8E-33, -5010E-24, 27.98E-12)
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

    def sparams(self, stds_meas, model=None):
        '''
        Returns a scattering matrix based on measured and model standards.
        IN
        stds_meas : np.array (3, N)
            The standards reflection coefficients measured at the desired reference plane.
        model : np.array (3,N) or None
            If none, the model reflection coefficient given by Copper Mountain is used.
        OUT
        np.array (3,N)
            (S11, S12*S21, S22) s matrix.
        '''
        if not model:
            model = self.std_gamma #get model standards if none are provided
        sparams = cal_s11.network_sparams(model, stds_meas)
        return sparams
