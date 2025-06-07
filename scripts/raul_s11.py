
import sys
import numpy as np
import pyvisa as pyvisa

import re
import subprocess


# Example of execution: 
# $ python3 vna.py -40 40 125 350 100

POWER_dBm = sys.argv[1]
FLOW_MHz  = sys.argv[2]
FHIGH_MHz = sys.argv[3]
NPOINTS   = sys.argv[4]
IFBW_Hz   = sys.argv[5]





# List USB devices and store in 'devices' dictionary
# --------------------------------------------------
device_re = re.compile(b"Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
df = subprocess.check_output("lsusb")
devices=[]
for i in df.split(b'\n'):
	if i:
		info = device_re.match(i)
		if info:
			dinfo = info.groupdict()
			dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
			devices.append(dinfo)
#print(devices)

# Determine if Copper Mountain VNA is connected
# ---------------------------------------------
connected = 0
for i in range(len(devices)):
	tag = devices[i]['tag'].decode('utf-8')
	# print(tag)
	if 'Copper Mountain technologies R60' in tag:
		connected = 1

# If NOT Connected, exit
# ----------------------
if connected == 0:
	print('0,0,0')
	exit()	

# If YES Connected, establish a VISA connection
# ---------------------------------------------
else:
	IP_VNA = 'localhost'
	rm     = pyvisa.ResourceManager('@py')
	VNA    = rm.open_resource('TCPIP0::' + IP_VNA + '::5025::SOCKET')








# Function to configure VNA
# -------------------------
def S11_configuration(POWER_dBm='0', FLOW_MHz='40', FHIGH_MHz='125', NPOINTS='350', IFBW_Hz='100'):
	"""
	This function is ready
	"""

	# The VNA ends each line with this. Reads will time out without this
	VNA.read_termination='\n'

	# Set a really long timeout period for slow sweeps
	VNA.timeout = 100000

	# Set up the Power, start freq, stop freq, Npoints, and IFBW
	values=[]
	VNA.write_ascii_values('CALC:FORM SCOM\n',values)               # Formats the reading as complex S11 (Re/Im)
	VNA.write_ascii_values('SOUR:POW '+ POWER_dBm +'\n',values)     # Power in dBm
	VNA.write_ascii_values('SENS:AVER:COUN 1\n',values)             # Number of traces averaged
	VNA.write_ascii_values('SENS:FREQ:STAR '+ FLOW_MHz +' MHZ;STOP '+ FHIGH_MHz +' MHZ\n',values)
	VNA.write_ascii_values('SENS:SWE:POIN '+ NPOINTS +'\n',values)  # Number of points, 125*N + 1, where N is number of points per MHz
	VNA.write_ascii_values('SENS:BWID '+ IFBW_Hz +'HZ\n',values)
	VNA.write_ascii_values('TRIG:SOUR BUS\n',values)

	return 0








# Function to measure S11
# -----------------------
def S11_measurement():
	"""
	This function is ready
	"""

	# Trigger a measurement
	values=[]
	VNA.write_ascii_values('TRIG:SEQ:SING\n',values) # Trigger a single sweep
	x = VNA.query('*OPC?\n')                             # Wait for measurement to complete
	print(x)
	
	# To make sure we are getting new data
	f   = 0
	S11 = 0
	S11_complex = 0

	# Read out data
	f   = VNA.query("SENS:FREQ:DATA?\n")             # Get frequency data as string
	S11 = VNA.query("CALC:TRAC:DATA:FDAT?\n")        # Get S11 data as string

	# Reformatting the data
	f = f.split(",")
	f = [float(i)/1e6 for i in f]                    # in MHz
	f = np.array(f)

	S11  = S11.split(",")
	S11  = [float(s) for s in S11]
	re_S11 = np.array(S11[::2])
	im_S11 = np.array(S11[1::2])
	S11_complex = re_S11 + 1j*im_S11

	return f, S11_complex




# Configure VNA
# -------------
o = S11_configuration(POWER_dBm=POWER_dBm, FLOW_MHz=FLOW_MHz, FHIGH_MHz=FHIGH_MHz, NPOINTS=NPOINTS, IFBW_Hz=IFBW_Hz)


# Measure S11
# -----------
f_s11, s11 = S11_measurement()


# Reformat the frequency and S11 arrays before printing them out at terminal
# --------------------------------------------------------------------------
for i in range(len(f_s11)):
	if i == 0:
		string_f = str(f_s11[i])
		string_real_s11 = str(np.real(s11[i]))
		string_imag_s11 = str(np.imag(s11[i]))
	else:	
		string_f = string_f + ',' + str(f_s11[i])
		string_real_s11 = string_real_s11 + ',' + str(np.real(s11[i]))
		string_imag_s11 = string_imag_s11 + ',' + str(np.imag(s11[i]))


# Print out results to terminal
# -----------------------------
print(string_f + ',' + string_real_s11 + ',' + string_imag_s11)







