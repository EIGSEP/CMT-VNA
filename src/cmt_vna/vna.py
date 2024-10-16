from datetime import datetime
import socket
import numpy as np

IP = "127.0.0.1"
PORT = 5025


class VNA:

    def __init__(self, ip=IP, port=PORT):
        self.ip = ip
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.ip, self.port))

    def __close__(self):
        self.s.close()

    @property
    def id(self):
        self.s.sendall(b"*IDN?\n")
        return self.s.recv(4096).decode()

    @property
    def opc(self):
        """
        Query operation complete status
        """
        self.s.sendall(b"*OPC?\n")
        return self.s.recv(4096).decode()

    def calibrate_OSL(self):
        standards = {"open": "OPEN", "short": "SHOR", "load": "LOAD"}
        for name, code in standards.items():
            print(f"Connect {name} standard, then press enter")
            input()
            cmd = f"SENS:CORR:COLL:{code} 1\n"
            self.s.sendall(cmd.encode())
            print(self.opc)  # wait for operation complete

        self.s.sendall(b"SENS:CORR:COLL:METH:SOLT1 1\n")
        self.s.sendall(b"SENS:CORR:COLL:SAVE\n")

    def setup_S11(
        self, fstart=1e6, fstop=250e6, npoints=1000, ifbw=100, power_dBm=0
    ):
        """
        Setup S11 measurement

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
        self.s.sendall("CALC:FORM SCOM\n".encode())  # get s11 as real and imag
        self.s.sendall(f"SOUR:POW {power_dBm}\n".encode())  # power level
        self.s.sendall("SENS:AVER:COUN 1\n".encode())  # number of averages
        self.s.sendall(f"SENS:FREQ:STAR {fstart} HZ\n".encode())
        self.s.sendall(f"SENS:FREQ:STOP {fstop} HZ\n".encode())
        self.s.sendall(f"SENS:SWE:POIN {npoints}\n".encode())
        self.s.sendall(f"SENS:BWID {ifbw} HZ\n".encode())
        self.s.sendall(b"TRIG:SOUR BUS\n")
        return self.opc




    def measure_S11(self):
        """
        Measure S11 parameter and save CSV file

        Returns
        -------
        freq : np.array
            Frequency points in MHz
        s11 : np.array
            Complex-valued S11 parameter in dB

        """
        self.s.sendall("TRIG:SEQ:SING\n".encode())
        if self.opc:
            print("Measurement complete")
    
        # get frequencies
        self.s.sendall(b"SENS:FREQ:DATA?\n")
        freq = self.s.recv(4096).decode().split(",")
        freq = np.array([float(f)/1e6 for f in freq])

        # get s11
        self.s.sendall(b"CALC:TRAC:DATA:FDAT?\n")
        s11 = self.s.recv(4096).decode().split(",")
        s11 = np.array([float(s) for s in s11])
        s11 = s11[0::2] + 1j*s11[1::2]  # convert to complex

        return freq, s11

