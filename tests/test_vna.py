import numpy as np
from cmt_vna import VNA
from cmt_vna import S911T
from mistdata import cal_s11 as cal

DATA_DIR = '../data/'

CAL_DIR = os.path.join(DATA_DIR, 'cals')
CAL_FILE = os.path.join(CAL_DIR, max(os.listdir(CAL_DIR)))
CAL = np.load(CAL_FILE)
osl = np.vstack([CAL['open'], CAL['short'], CAL['load']])
FREQS = CAL['freqs']
calkit = S911T(freq_Hz=FREQS) #new calkit with meas freqs

def test_vna_sprms(calkit, osl, CAL_FILE):
    vna_sprms = cal.network_sparams(gamma_true=calkit.std_gamma, gamma_meas=osl) #vna_prms acquired
    
    vna = VNA()
    vna.add_sparams(stds_file=CAL_FILE, kit=calkit)
    
    assert np.allclose(vna.sparams, vna_sprms)
