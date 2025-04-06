import numpy as np
from .calkit import S911T
from . import calkit as cal
import pyvisa
import time
from datetime import datetime

IP = "127.0.0.1"
PORT = 5025


class VNA:

    def __init__(self, to=100000, ip=IP, port=PORT):
        self.rm = pyvisa.ResourceManager("@py")
        self.s = self.rm.open_resource(f"TCPIP::{ip}::{port}::SOCKET")
        self.s.read_termination = "\n"
        self.s.timeout = to
        self._clear_data()

    @property
    def id(self):
        return self.s.query("*IDN?\n")

    @property
    def opc(self):
        """
        Query operation complete status
        """
        return self.s.query("*OPC?\n")

    def _clear_data(self):
        self.sparams=dict() 
        self.gammas = dict()
        self.stds=dict()
        self.stds_meta = dict()

    def setup(self, fstart=1e6, fstop=250e6, npoints=1000, ifbw=100, power_dBm=0):
        """
        Setup S11 measurement.

        IN
        fstart : float
            Start frequency in Hz
        fstop : float
            Stop frequency in Hz
        npoints : int
            Number of points in the frequency sweep
        ifbw : float
            Intermediate frequency bandwidth in Hz
        power_dBm : float
            Power level in dBm

        OUT
        adds freqs attribute to vna object. returns freqs array as well.
        """
        self.s.write(
            "FORM:DATA REAL\n"
        )  # get data as 64-bit binary values
        self.s.write(
            "CALC:FORM SCOM\n"
        )  # get s11 as real and imag
        self.s.write(
            f"SOUR:POW {power_dBm}\n"
        )  # power level
        self.s.write(
            "SENS1:AVER:COUN 1\n"
        )  # number of averages
        self.s.write(
            "SWE:TYPE LIN\n"
        ) #linear sweep instead of point by point
        self.s.write(f"SENS1:FREQ:STAR {fstart} HZ\n")
        self.s.write(f"SENS1:FREQ:STOP {fstop} HZ\n")
        self.s.write(f"SENS1:SWE:POIN {npoints}\n")
        self.s.write(f"SENS1:BWID {ifbw} HZ\n")
        self.s.write("TRIG:SOUR BUS\n")
        freq = self.s.query_binary_values('SENS1:FREQ:DATA?', container=np.array, is_big_endian=True, datatype='d')
        freq = [float(i) for i in freq]
        self.freqs = np.array(freq)
        return np.array(freq)

    def measure_S11(self, verbose = False):
        '''
        Get S11 measurement (complex). Can be used for standards and antenna measurements. 
        '''
        t0 = time.time()
        self.s.write('TRIG:SEQ:SING') #sweep
        if self.opc and verbose: #check if the sweep is done before proceeding
             print('swept')
        data = self.s.query_binary_values('CALC:TRAC:DATA:FDAT?', container=np.array, is_big_endian=True, datatype='d')#query the values
        if self.opc and verbose: #if verbose and the query is done, print time
             print(f'{time.time() - t0 : .2f} seconds to sweep.')
        data = np.array([float(i) for i in data]) #change to complex floats
        data = data[0::2] + 1j * data[1::2]
        return data #returns complex data

    def measure_OSL(self,auto= False):
        '''Iterate through all standards for measurement. Returns dictionary with keys 'open', 'short', and 'load'.'''

        OSL = dict()
        standards = ['open', 'short', 'load'] #set osl standard list
        for standard in standards:
             if not auto: #testing/manual osl measurements
                 print(f'connect {standard} and press enter')
                 input() 
             elif auto:#automatic osl measurements
                 print('doing switch network things')
                 #TODO: do switch network stuff
             data = self.measure_S11()
             OSL[standard] = data
        return OSL

    def add_OSL(self, std_key='vna', overwrite=False, auto=False): 
        '''
        Iterate through standards for measurement. Adds standards measurement to self.stds.
        
        IN
        sprm_key : key value to assign to the OSL entry in self.stds. default is vna.
        overwrite : mainly for dev. allows you to overwrite key value pairs in self.stds. 
        auto : also mainly for dev. if auto is False, you have to manually attach the OSL standards. 
        '''
        ###So I don't accidentally overwrite standards when I'm testing### 
        if not overwrite:
            try:
                assert std_key not in list(self.stds.keys())
            except AssertionError:
                print('You are about to overwrite the standards that already exist. Would you like to overwrite? (y/n)')
                decision = input()
                if decision.lower() == 'n':
                    return
                else:
                    print('overwriting.')
        ##################################################################
        OSL = self.measure_OSL(auto=auto)
        self.stds[std_key] = np.array(list(OSL.values()))
        self.stds_meta[std_key] = list(OSL.keys())

    def read_data(self, num_data=1): 
        '''
        reads num_data s11s, adds them to self.gammas.
        IN
        num_data : number of measurements to take in a sitting.
        '''
        i = 0
        while i < num_data:
            i += 1 
            gamma = self.measure_S11()
            date = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.gammas[date] = gamma
    
    def write_data(self, outdir, save_sprms=True, save_stds=True): 
        '''
        writes all the data in vna to an npz, clears the data that was just written.
        '''
        date = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        
        self.gammas['freqs'] = self.freqs
        np.savez(f'{outdir}/{date}_gammas.npz', **self.gammas)
        #always saves the gammas/freqs, but only saves sparams and standards if you tell it to (default is to save them)
        if save_sprms and len(self.sparams.keys()) != 0: 
            np.savez(f'{outdir}/{date}_sparams.npz', **self.sparams) 
        if save_stds and len(self.stds.keys()) != 0:
            np.savez(f'{outdir}/{date}_standards.npz', **self.stds) 
        self._clear_data()

    def add_sparams(self, kit, sprm_key, std_key='vna'):
        '''
        Adds sparams with key to self.sparams dict.
        
        IN
        kit : CalKit object.
        sprm_key : key for new sparam array.
        std_key : key of osl to use for extracting sparams. 
        '''
        
        stds_meas = self.stds[std_key] 
        params = cal.network_sparams(gamma_true=kit.std_gamma, gamma_meas=stds_meas)
        self.sparams[sprm_key] = params

    def calibrate_gammas(self,sprm_keys):
        '''calibrates all gamma values with respect to all networks 

           IN
           kit: CalKit object.
           sprm_keys : sparams to de-embed from the gammas.
           OUT
           returns the calibrated gammas as an array. 
        '''
        gammas = np.array(list(self.gammas.values()))
        for sprm_key in sprm_keys:
            sprm = self.sparams[sprm_key]
            gammas = cal.de_embed_sparams(sparams=sprm, gamma_prime=gammas)
        return gammas

    def calibrate_std(self, sprm_key, std_key):
        '''adds a calibrated osl standard to self.stds
           IN
           sprm_key : key for the sparams being de-embedded from the standards.
           std_key : key for the osl standards that are being calibrated.
           OUT
           Adds the calibrated osl standards to self.stds and returns the new key for the calibrated stds.
'''
        osl = self.stds[std_key] 
        sprm = self.sparams[sprm_key]
        cal_osl = cal.de_embed_sparams(sparams=sprm, gamma_prime=osl)
        new_key = f'{std_key}_ref_{sprm_key}'
        self.stds[new_key] = cal_osl
        return new_key        


