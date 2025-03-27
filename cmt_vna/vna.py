import numpy as np
import pyvisa
import time
from datetime import datetime
from .calkit import S911T
import mistdata.cal_s11 as cal
import threading
import matplotlib.pyplot as plt

IP = "127.0.0.1"
PORT = 5025


class VNA:

    def __init__(self, to=100000, ip=IP, port=PORT):
        self.rm = pyvisa.ResourceManager("@py")
        self.s = self.rm.open_resource(f"TCPIP::{ip}::{port}::SOCKET")
        self.s.read_termination = "\n"
        self.s.timeout = to
        self._clear_data()
        self._running = False
        self._thread = None

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
        self.data =dict() 

    def setup(self, fstart=1e6, fstop=250e6, npoints=1000, ifbw=100, power_dBm=0):
        """
        Setup S11 measurement.

        Parameters
        ----------
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
        self.data['freqs'] = freq
        return np.array(freq)

    def measure_S11(self, verbose = False):
        '''
        Get S11 measurement. Can be used for standards and antenna measurements. 
        '''
        t0 = time.time()
        self.s.write('TRIG:SEQ:SING')
        if self.opc and verbose: #check if the sweep is done before proceeding
             print('swept')
        data = self.s.query_binary_values('CALC:TRAC:DATA:FDAT?', container=np.array, is_big_endian=True, datatype='d')#query the values
        if self.opc and verbose: #if verbose and the query is done, print time
             print(f'{time.time() - t0 : .2f} seconds to sweep.')
        data = np.array([float(i) for i in data]) #change to complex floats
        data = data[0::2] + 1j * data[1::2]
        return data

    def measure_OSL(self):
        #iterate through standards, take data and add to dictionary
        OSL = dict()
        standards = ['open', 'short', 'load'] #set osl standard list
        for standard in standards:
             print(f'connect {standard} and press enter')
             input()
             data = self.measure_S11()
             OSL[standard] = data
        return OSL

    def add_OSL(self, overwrite=False): 
        '''
        Iterate through standards for measurement. Adds standards measurement to self.data.
        '''
        if not overwrite:
            try:
                assert 'open' not in list(self.data.keys())
                assert 'short' not in list(self.data.keys())
                assert 'load' not in list(self.data.keys())
            except AssertionError:
                print('You are about to overwrite the standards that already exist. Would you like to overwrite? (y/n)')
                decision = input()
                if decision.lower() == 'n':
                    return
                else:
                    print('overwriting.')
        OSL = self.measure_OSL()
        for key, d in OSL.items():
            self.data[key] = d


    def add_sparams(self, kit):
        '''
        Adds sparams attribute to the VNA object.
        '''
        osl = self.data
        stds_meas = np.vstack([osl['open'], osl['short'], osl['load']])
        params = kit.sparams(stds_meas=stds_meas) #defaults to model standards
        self.sparams = params

    def de_embed(self, gamma_meas, sprms=None):
        '''
        de-embeds s-parameters from measurements. Default is to de-embed self.sparams. sprms_file can be a file path, sprms_network can be a (3,N) np array, both default to None.
        '''
        if not sprms:
            sprms = self.sparams
        gamma_cal = cal.de_embed_sparams(sprms, gamma_meas)
        return gamma_cal

    def read_data(self, num_data=1): 
        '''
        reads num_data s11s, adds them to self.data.
        '''
        i = 0
        while i < num_data and self._running:
            i += 1 
            gamma = self.measure_S11()
            date = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.data[date] = gamma
        self._running = False

    def start_recording(self, num_data):
        self._running = True
        self._thread = threading.Thread(target=self.read_data, args=(num_data,))
        self._thread.daemon = True
        self._thread.start()
 
    def end_recording(self):
        try:
            assert self._thread != None
        except AssertionError:
            return
        self._running = False
        self._thread.join()

    def write_data(self, outdir): 
        '''
        writes all the data in self.data to an npz.
        '''
        date = datetime.now().strftime("%Y%m%d_%H%M%S")
        if len(self.data.keys()) <= 4:
            print(f'you are saving {list(self.data.keys())}. Do you want to save? (y/n)')
            decision = input()
            if decision.lower() == 'n':
                return
        np.savez(f'{outdir}/{date}.npz', **self.data) 
        self._clear_data()

    def from_file(self, filename):
        '''
        Populates VNA data from a file that has been written.
        '''
        file = np.load(filename)
        try:
            data = dict(file)
            keys = ['freqs', 'open', 'short', 'load']
            assert all(x in list(data.keys()) for x in keys)
        except AssertionError:
            print('not all required keys are here for de_embedding. proceed? (y/n)')
            decision = input()
            if decision.lower() == 'n':
                return
            else:
                print('writing to vna')
        except Exception as e:
            print(e)
            return
        self.data = data
