import numpy as np
import pyvisa
import time
from datetime import datetime


IP = "127.0.0.1"
PORT = 5025


class VNA:

    def __init__(self, ip=IP, port=PORT, timeout=1000):
        """
        Class controlling Copper Mountain VNA.

        Parameters
        ----------
        ip : str
            IP address of VNA.
        port : int
            Port to connect to VNA.
        timeout : float or None
            Timeout in seconds for VNA communication. Needs to be long enough
            to complete the measurement. If None, no timeout is set and we
            wait indefinitely for a response.

        """

        self.rm = pyvisa.ResourceManager("@py")
        self.s = self.rm.open_resource(f"TCPIP::{ip}::{port}::SOCKET")
        self.s.read_termination = "\n"
        self.s.timeout = timeout * 1e3  # convert to milliseconds
        self._clear_data()

    @property
    def id(self):
        return self.s.query("*IDN?\n")

    def wait_for_opc(self):
        """
        Query operation complete status. Blocks until complete.

        Raises
        -------
        TimeoutError
            If the operation does not complete within the timeout period. See
            the attribute timeout in the constructor.

        """
        try:
            _ = self.s.query("*OPC?\n")
        except pyvisa.VisaIOError as e:
            if e.error_code == pyvisa.constants.StausCode.error_timeout:
                raise TimeoutError(
                    "Operation did not complete within the timeout period."
                ) from e
            raise

    def _clear_data(self):
        self.data = dict()
        self.stds_meta = dict()

    def setup(
        self, fstart=1e6, fstop=250e6, npoints=1000, ifbw=100, power_dBm=0
    ):
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
        self.s.write("CALC:FORM SCOM\n")  # get s11 as real and imag
        self.s.write(f"SOUR:POW {power_dBm}\n")  # power level
        self.s.write("SENS1:AVER:COUN 1\n")  # number of averages
        self.s.write(
            "SWE:TYPE LIN\n"
        )  # linear sweep instead of point by point
        self.s.write(f"SENS1:FREQ:STAR {fstart} HZ\n")
        self.s.write(f"SENS1:FREQ:STOP {fstop} HZ\n")
        self.s.write(f"SENS1:SWE:POIN {npoints}\n")
        self.s.write(f"SENS1:BWID {ifbw} HZ\n")
        self.s.write("TRIG:SOUR BUS\n")
        freq = self.s.query_ascii_values(
            "SENS1:FREQ:DATA?", container=np.array
        )
        freq = [float(i) for i in freq]
        self.freqs = np.array(freq)
        return np.array(freq)

    def measure_S11(self, verbose=False):
        """
        Get S11 measurement (complex). Can be used for standards and antenna
        measurements.

        Parameters
        ----------
        verbose : bool
            If True, prints time taken to sweep.

        """
        t0 = time.time()
        self.s.write("TRIG:SEQ:SING")  # sweep
        self.wait_for_opc()  # wait for operation complete
        if verbose:
            print("swept")
        data = self.s.query_ascii_values(
            "CALC:TRAC:DATA:FDAT?", container=np.array
        )
        self.wait_for_opc()  # wait for operation complete
        if verbose:
            sweep_time = time.time() - t0
            print(f"{sweep_time:.2f} seconds to sweep.")
        data = np.array([float(i) for i in data])  # change to complex floats
        data = data[0::2] + 1j * data[1::2]
        return data  # returns complex data

    def measure_OSL(self, snw=None):
        """
        Iterate through all standards for measurement.

        Parameters
        ----------
        snw : switch_network.SwitchNetwork
            Instance of SwitchNetwork to automatically switch between
            standard. If None, you will have to manually attach standards.

        Returns
        -------
        OSL : dict
            Dictionary of standards measurements. Keys are ``open'',
            ``short'', and ``load''.

        """

        OSL = dict()
        standards = ["VNAO", "VNAS", "VNAL"]  # set osl standard list
        for standard in standards:
            if snw is None:  # testing/manual osl measurements
                print(f"connect {standard} and press enter")
                input()
            else:  # automatic osl measurements
                snw.switch(standard)
            data = self.measure_S11()
            OSL[standard] = data
        return OSL

    def add_OSL(self, snw=None, std_key="vna"):
        """
        Call measure_OSL to iterate through standards. Adds standards
        measurement to self.data.

        Parameters
        ----------
        snw : switch_network.SwitchNetwork
            Instance of SwitchNetwork to automatically switch between
            standards. If None, you will have to manually attach standards.
        std_key : str
            Key value to assign to the OSL entry in self.stds.

        """
        OSL = self.measure_OSL(snw=snw)
        self.data[std_key] = np.array(list(OSL.values()))
        self.stds_meta[std_key] = list(OSL.keys())

    def read_data(self, num_data=1):
        """
        reads num_data s11s, adds them to self.data.
        IN
        num_data : number of measurements to take in a sitting.
        """
        i = 0
        while i < num_data:
            i += 1
            gamma = self.measure_S11()
            date = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.data[f"{date}_gamma"] = gamma

    def write_data(self, outdir, save_stds=True):
        """
        Write all the data in vna to an npz. Clear the data out of the vna
        object.

        Parameters
        ----------
        outdir : str
            Directory to save the data to.
        save_stds : bool
            If True, saves the standards data to the npz file. If False,
            does not save the standards data.

        """
        date = datetime.now().strftime("%Y%m%d_%H%M%S")

        # adds the frequency array to the gammas dict
        self.data["freqs"] = self.freqs
        np.savez(f"{outdir}/{date}_data.npz", **self.data)
        self._clear_data()
