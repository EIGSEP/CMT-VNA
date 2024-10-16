import numpy as np
import pyvisa

IP = "127.0.0.1"
PORT = 5025


class VNA:

    def __init__(self, ip=IP, port=PORT):
        self.rm = pyvisa.ResourceManager("@py")
        self.s = self.rm.open_resource(f"TCPIP::{ip}::{port}::SOCKET")
        self.s.read_termination = "\n"
        self.s.timeout = 100000

    @property
    def id(self):
        return self.s.query("*IDN?\n")

    @property
    def opc(self):
        """
        Query operation complete status
        """
        return self.s.query("*OPC?\n")

    def calibrate_OSL(self):
        standards = {"open": "OPEN", "short": "SHOR", "load": "LOAD"}
        for name, code in standards.items():
            print(f"Connect {name} standard, then press enter")
            input()
            cmd = f"SENS:CORR:COLL:{code} 1"
            self.s.write(cmd)
            print(self.opc)  # wait for operation complete

        self.s.write("SENS:CORR:COLL:METH:SOLT1 1")
        self.s.write("SENS:CORR:COLL:SAVE")

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
        values = []
        self.s.write_ascii_values(
            "CALC:FORM SCOM\n", values
        )  # get s11 as real and imag
        self.s.write_ascii_values(
            f"SOUR:POW {power_dBm}\n", values
        )  # power level
        self.s.write_ascii_values(
            "SENS:AVER:COUN 1\n", values
        )  # number of averages
        self.s.write_ascii_values(f"SENS:FREQ:STAR {fstart} HZ\n", values)
        self.s.write_ascii_values(f"SENS:FREQ:STOP {fstop} HZ\n", values)
        self.s.write_ascii_values(f"SENS:SWE:POIN {npoints}\n", values)
        self.s.write_ascii_values(f"SENS:BWID {ifbw} HZ\n", values)
        self.s.write_ascii_values("TRIG:SOUR BUS\n", values)
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
        values = []
        self.s.write_ascii_values("TRIG:SEQ:SING\n", values)
        if self.opc:
            print("Measurement complete")

        # get frequencies
        freq = self.s.query("SENS:FREQ:DATA?\n").split(",")
        freq = np.array([float(f) / 1e6 for f in freq])

        # get s11
        s11 = self.s.query("CALC:TRAC:DATA:FDAT?\n").split(",")
        s11 = np.array([float(s) for s in s11])
        s11 = s11[0::2] + 1j * s11[1::2]  # convert to complex

        return freq, s11
