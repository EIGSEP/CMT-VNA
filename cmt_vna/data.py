import numpy as np
import pyvisa
import time
from datetime import datetime
from .calkit import S911T
import mistdata.cal_s11 as cal
import threading
import matplotlib.pyplot as plt

class S11:
    
    def __init__(self):
        self.freqs = [] 
        self.gamma = dict()
        self.stds = dict() #dictionary of 3d arrays, keys say where measured
        self.sparams = dict() #same vibe

    def from_file(self, filename, network):
        '''
        Populates data from a file that has been written.
        '''
        file = np.load(filename)
        data = dict(file)
        try:
            if (len(self.freqs) != 0) and not np.allclose(self.freqs, data['freqs']):
                print('These frequency arrays dont match. Aborting.')
                return
            self.freqs = data['freqs']
        except KeyError:
            print('no frequency data.')
        try:
            stds_meas = np.vstack([data['open'], data['short'], data['load']])
            self.stds[network] = stds_meas
        except KeyError:
            print('no standards data.')
        try:
            sprms = data['sprms']
            self.sparams[network] = sprms 
        except KeyError:
            print('no sparam data.')
        keys = ['freqs', 'open', 'short', 'load']
        gammas = {key: d for key,d in data.items() if key not in keys}
        self.gamma.update(gammas)
       
    def add_sparams(self, network, stds_meas, stds_ref=None):
        '''Takes the network name, the calkit, the measured osl standards, and the reference standards (default is None, which gives the calkit models, otherwise you can pass a (3,N) array). Assumes you have already de-embedded necessary s parameters from the standards measurement.'''
        if stds_ref is None:
            calkit = S911T(freq_Hz=self.freqs)
            stds_ref = calkit.std_gamma
        sprms = cal.network_sparams(gamma_true=stds_ref, gamma_meas=stds_meas)
        self.sparams[network] = sprms

    def de_embed(self, gamma_meas, sprms_key=None):
        '''
        de-embeds s-parameters from measurements. Default is to de-embed self.sparams. sprms_file can be a file path, sprms_network can be a (3,N) np array, both default to None.
        '''
        if sprms_key is None:
            sprms = self.sparams
        gamma_cal = cal.de_embed_sparams(sprms, gamma_meas)
        return gamma_cal


