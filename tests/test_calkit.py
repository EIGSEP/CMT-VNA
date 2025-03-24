import mistdata.cal_s11 as cal
from cmt_vna import VNA
from cmt_vna import S911T
import numpy as np

def test_S911T():
    #recalculate standards, compare to the ones in S911T

    Z0 = 50
    fake_freqs = np.linspace(50e6, 250e6, 1001)
    calkit = S911T(freq_Hz = fake_freqs)

    #open standard
    c_open = -7.425E-15 + 2470E-27 * fake_freqs - 226E-36 * fake_freqs**2 + 6.18E-45 * fake_freqs**3
    c_delay = 30.821e-12 #s
    c_loss = 2e9 #Ohm/s
    
    Z_off_open = Z0 + (1-1j) * c_loss / (4 * np.pi * fake_freqs) * np.sqrt(fake_freqs/1e9)
    gamma_off_open = cal.impedance_to_gamma(Z_off_open, Z0)
    Z_ter_open = -1j / (2 * np.pi * fake_freqs * c_open)
    gamma_ter_open = cal.impedance_to_gamma(Z_ter_open, Z0)
    g_l_open = 1j * 2 * np.pi * fake_freqs * c_delay + (1+1j) * c_delay * c_loss / (2 * Z0) * np.sqrt(fake_freqs/1e9)
    gamma_open = gamma_off_open * (1 - np.exp(-2 * g_l_open) - gamma_off_open * gamma_ter_open) + gamma_ter_open * np.exp(-2 * g_l_open)
    gamma_open /= 1 - gamma_off_open * (np.exp(-2 * g_l_open) * gamma_off_open + gamma_ter_open * (1 - np.exp(-2 * g_l_open)))

    assert np.allclose(calkit.open.gamma_ter, gamma_ter_open)
    assert np.allclose(calkit.open.gamma_off, gamma_off_open)
    assert np.allclose(calkit.open.gamma, gamma_open)

    # short standard
    l_short = 27.98e-12 - 5010E-24 * fake_freqs + 303.8E-33 * fake_freqs**2 - 6.13E-42 * fake_freqs**3
    l_delay = 30.688E-12 #s
    l_loss = 2E9 #Ohm/s

    Z_off_short = Z0 + (1-1j) * l_loss / (4 * np.pi * fake_freqs) * np.sqrt(fake_freqs/1e9)
    gamma_off_short = cal.impedance_to_gamma(Z_off_short, Z0)
    Z_ter_short = 1j * 2 * np.pi * fake_freqs * l_short
gamma_ter_short = cal.impedance_to_gamma(Z_ter_short, Z0)

    g_l_short = 1j * 2 * np.pi * fake_freqs * l_delay + (1+1j) * l_delay * l_loss / (2 * Z0) * np.sqrt(fake_freqs/1e9)

    gamma_short = gamma_off_short * (1 - np.exp(-2 * g_l_short) - gamma_off_short * gamma_ter_short) + gamma_ter_short * np.exp(-2 * g_l_short)
    gamma_short /= 1 - gamma_off_short * (np.exp(-2 * g_l_short) * gamma_off_short + gamma_ter_short * (1 - np.exp(-2 * g_l_short)))
    
    assert np.allclose(calkit.short.gamma_ter, gamma_ter_short)
    assert np.allclose(calkit.short.gamma_off, gamma_off_short)
    assert np.allclose(calkit.short.gamma, gamma_short)

def test_sparams():
    calkit = S911T(freq_Hz = fake_freqs)
    gamma = calkit.std_gamma
    
    #gamma should be equal to the self gamma, so will get a perfect through Smatrix
    sprms = calkit.sparams(gamma)
    assert np.allclose(sprms[0], 0) #s11
    assert np.allclose(sprms[1], 1) #s12s21
    assert np.allclose(sprms[2], 0) #s22
