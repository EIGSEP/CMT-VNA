import numpy as np
import pyvisa
import time
from datetime import datetime
from .calkit import S911T
import mistdata.cal_s11 as cal

IP = "127.0.0.1"
PORT = 5025


class VNA:

    def __init__(self, to=100000, ip=IP, port=PORT):
        self.rm = pyvisa.ResourceManager("@py")
        self.s = self.rm.open_resource(f"TCPIP::{ip}::{port}::SOCKET")
        self.s.read_termination = "\n"
        self.s.timeout = to

    @property
    def id(self):
        return self.s.query("*IDN?\n")

    @property
    def opc(self):
        """
        Query operation complete status
        """
        return self.s.query("*OPC?\n")

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
        return freq

    def measure_S11(self, verbose = False):
        '''
        Get S11 measurement. Can be used for standards and antenna measurements. 

        verbose : boolean (Default = False).
             If true, prints time it took for sweep.

        Returns : numpy array of complex S11 measurement.
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

    def calibrate_OSL(self):
        '''
        Iterate through standards for measurement.

        Returns : dictionary with keys 'open', 'short', 'load'.
        '''
        standards = ['open', 'short', 'load'] #set osl standard list
        osl_data = dict()
        #iterate through standards, take data and add to dictionary
        for standard in standards:
             print(f'connect {standard} and press enter')
             input()
             data = self.measure_S11()
             osl_data[standard] = data
        return osl_data

    def add_sparams(self, freq, stds_file):
        '''
        Takes in a frequency array and a file with the standards measurement at the end of the vna.
        '''
        kit = S911T(freq_Hz=freq)
        osl = np.load(stds_file)
        stds_meas = np.vstack([osl['open'], osl['short'], osl['load']])
        params = kit.sparams(stds_meas=stds_meas)
        self.sparams = params
