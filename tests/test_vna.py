import numpy as np
from cmt_vna import VNA
from cmt_vna import calkit as cal

def test_add_sparams():
    #set measured standards to be the model standards, get sprms
    fake_freqs = np.linspace(50e6, 250e6,1000)
    kit = cal.S911T(freq_Hz=fake_freqs)
    model_stds = kit.std_gamma
    
    vna = VNA()
    vna.stds['test'] = model_stds #set the vna measured standards to the models
    
    #add the new sparams
    vna.add_sparams(kit=kit, sprm_key='test', std_key='test')

    test_sprms=vna.sparams['test']
    s11 = test_sprms[0]
    s12s21 = test_sprms[1]
    s22 = test_sprms[2]

    assert np.allclose(s11, 0) #should be 0, perfect through
    assert np.allclose(s12s21, 1) #should be 1
    assert np.allclose(s22, 0) #should be 0

def test_calibrate_gammas():
    fake_freqs = np.linspace(50e6, 250e6,1000)
    kit = cal.S911T(freq_Hz=fake_freqs)
    
    #make fake gammas all ones, all zeros
    fake_gamma1 = np.zeros(len(fake_freqs), dtype=np.complex_)
    fake_gamma = np.ones(len(fake_freqs), dtype=np.complex_)
    vna = VNA()
    vna.gammas['test'] = fake_gamma
    vna.gammas['test1'] = fake_gamma1 
    
    #fake perfect thru sparameters
    thru_sparams = np.empty((3, len(fake_freqs)), dtype=complex)
    thru_sparams[0] = 0 #S11
    thru_sparams[1] = 1 #S12S21
    thru_sparams[2] = 0 #S22
    vna.sparams['test'] = thru_sparams #add sparams to the vna
    vna.sparams['test1'] = thru_sparams #add same sparams to vna
    #de-embed the thru_sparams
    answer = np.vstack([fake_gamma, fake_gamma1])
    test = vna.calibrate_gammas(sprm_keys=['test', 'test1'])
    assert np.allclose(answer, test)

def test_calibrate_stds():
    fake_freqs = np.linspace(50e6, 250e6,1000)
    kit = cal.S911T(freq_Hz=fake_freqs)
    model_stds = kit.std_gamma
    vna = VNA()

    #set model standards as measured again
    vna.stds['test'] = model_stds
    #set perfect thru sparameters
    thru_sparams = np.empty((3, len(fake_freqs)), dtype=complex)
    thru_sparams[0] = 0 #S11
    thru_sparams[1] = 1 #S12S21
    thru_sparams[2] = 0 #S22
    vna.sparams['test'] = thru_sparams

    #de-embed perfect thru from the models
    new_key = vna.calibrate_std(sprm_key='test', std_key='test')
    
    #the new calibrated standards should be the same as the model
    assert np.allclose(vna.stds['test'], vna.stds[new_key])
    assert new_key == 'test_ref_test'
