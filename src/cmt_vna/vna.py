from datetime import datetime
from pathlib import Path
import time

import numpy as np
import pyvisa


IP = "127.0.0.1"
PORT = 5025


class VNA:

    def __init__(
        self,
        ip=IP,
        port=PORT,
        timeout=1000,
        save_dir=Path("."),
        switch_network=None,
    ):
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
        save_dir : Path or str
            Directory to save data to. Must be able to instantiate a Path
            object.
        switch_network : switch_network.SwitchNetwork or None
            Instance of SwitchNetwork to automatically switch the DUT or
            standards. If None, assumes switching is done in another way.

        """

        self.rm = pyvisa.ResourceManager("@py")
        self.s = self.rm.open_resource(f"TCPIP::{ip}::{port}::SOCKET")
        self.s.read_termination = "\n"
        self.s.timeout = timeout * 1e3  # convert to milliseconds
        self._clear_data()
        self.save_dir = Path(save_dir)
        self.switch_nw = switch_network

        # attributes
        self._fstart = None
        self._fstop = None
        self._npoints = None
        self._ifbw = None
        self._power_dBm = None

        # settings
        self.s.write("CALC:FORM SCOM\n")  # get s11 as real and imag
        self.s.write("SENS1:AVER:COUN 1\n")  # number of averages
        # linear sweep instead of point by point
        self.s.write("SWE:TYPE LIN\n")
        self.s.write("TRIG:SOUR BUS\n")

    @property
    def id(self):
        return self.s.query("*IDN?\n")

    @property
    def fstart(self):
        return self._fstart

    @fstart.setter
    def fstart(self, value):
        if self._fstart == value:
            return
        self.s.write(f"SENS1:FREQ:STAR {value} HZ\n")
        self._fstart = value

    @property
    def fstop(self):
        return self._fstop

    @fstop.setter
    def fstop(self, value):
        if self._fstop == value:
            return
        self.s.write(f"SENS1:FREQ:STOP {value} HZ\n")
        self._fstop = value

    @property
    def npoints(self):
        return self._npoints

    @npoints.setter
    def npoints(self, value):
        if self._npoints == value:
            return
        self.s.write(f"SENS1:SWE:POIN {value}\n")
        self._npoints = value

    @property
    def ifbw(self):
        return self._ifbw

    @ifbw.setter
    def ifbw(self, value):
        if self._ifbw == value:
            return
        self.s.write(f"SENS1:BWID {value} HZ\n")
        self._ifbw = value

    @property
    def power_dBm(self):
        return self._power_dBm

    @power_dBm.setter
    def power_dBm(self, value):
        if self._power_dBm == value:
            return
        self.s.write(f"SOUR:POW {value}\n")
        self._power_dBm = value

    @property
    def freqs(self):
        freq = self.s.query_ascii_values(
            "SENS1:FREQ:DATA?", container=np.array
        )
        try:
            f_array = np.array([float(i) for i in freq])
        except (TypeError, ValueError):
            f_array = None
        return f_array

    @property
    def header(self):
        """
        Get metadata of the VNA settings.

        Returns
        -------
        dict
            Dictionary with keys 'fstart', 'fstop', 'npoints', 'ifbw',
            'power_dBm', and 'freqs'. The values are the corresponding
            settings of the VNA.

        """
        return {
            "fstart": self.fstart,
            "fstop": self.fstop,
            "npoints": self.npoints,
            "ifbw": self.ifbw,
            "power_dBm": self.power_dBm,
            "freqs": self.freqs,
        }

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

        Returns
        -------
        freq : np.ndarray
            Frequency array in Hz

        """
        self.power_dBm = power_dBm
        self.fstart = fstart
        self.fstop = fstop
        self.npoints = npoints
        self.ifbw = ifbw
        return self.freqs

    def measure_S11(self, verbose=False):
        """
        Get S11 measurement (complex).

        Parameters
        ----------
        verbose : bool
            If True, prints time taken to sweep.

        Returns
        -------
        data : np.ndarray
            Complex-valued array of S11 measurements.

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
        return data

    def measure_OSL(self):
        """
        Iterate through all standards for measurement.

        Returns
        -------
        OSL : dict
            Dictionary of standards measurements. Keys are ``open'',
            ``short'', and ``load''.

        """

        OSL = dict()
        standards = ["VNAO", "VNAS", "VNAL"]  # set osl standard list
        for standard in standards:
            if self.switch_nw is None:  # testing/manual osl measurements
                print(f"connect {standard} and press enter")
                input()
            else:  # automatic osl measurements
                self.switch_nw.switch(standard)
            data = self.measure_S11()
            OSL[standard] = data
        return OSL

    def add_OSL(self, std_key="vna"):
        """
        Call measure_OSL to iterate through standards. Adds standards
        measurement to self.data.

        Parameters
        ----------
        std_key : str
            Key value to assign to the OSL entry in self.stds.

        """
        OSL = self.measure_OSL()
        self.data[std_key] = np.array(list(OSL.values()))
        self.stds_meta[std_key] = list(OSL.keys())

    def measure_ant(self, measure_noise=True):
        """
        Measure S11 of antenna. If measure_noise is True, also measures
        S11 of noise source. This is a convenience function that uses the
        switch network to switch to the right DUT. It therefore requires
        the switch_nw attribute to be set.

        Parameters
        ----------
        measure_noise : bool
            If True, measures S11 of noise source. If False, only measures
            S11 of antenna.

        Returns
        -------
        s11 : dict
            Dictionary with keys 'ant' and 'noise' (if measure_noise is True).

        Raises
        -------
        RuntimeError
            If the attribute switch_nw is None.

        """
        if self.switch_nw is None:
            raise RuntimeError("No switch network set, cannot measure S11.")
        s11 = {}
        self.switch_nw.switch("VNAANT")  # switch to antenna
        s11["ant"] = self.measure_S11()
        if measure_noise:
            self.switch_nw.switch("VNAN")  # switch to noise source
            s11["noise"] = self.measure_S11()
        return s11

    def measure_rec(self):
        """
        Measure S11 of the receiver. This is a convenience function that uses
        the switch network to switch to the right DUT. It therefore requires
        the switch_nw attribute to be set.

        Returns
        -------
        s11 : dict
            Dictionary with key 'rec' containing the S11 measurement of the
            receiver.

        Raises
        -------
        RuntimeError
            If the attribute switch_nw is None.

        """
        if self.switch_nw is None:
            raise RuntimeError("No switch network set, cannot measure S11.")
        s11 = {}
        self.switch_nw.switch("VNARF")  # switch to receiver
        s11["rec"] = self.measure_S11()
        return s11

    def read_data(self, num_data=1):
        """
        Repeatedly call ``measure_S11, and store the results in the ``data''
        attribute.

        Parameters
        ----------
        num_data : int
           Number of measurements to take.

        """
        for _ in range(num_data):
            gamma = self.measure_S11()
            date = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.data[f"{date}_gamma"] = gamma

    def write_data(self, outdir=None):
        """
        Write all the data in vna to an npz. Clear the data out of the vna
        object.

        Parameters
        ----------
        outdir : Path or str
            Directory to save the data to. If None, uses the save_dir
            attribute.

        """
        # adds the frequency array to the gammas dict
        self.data["freqs"] = self.freqs
        # create filename with date and time
        date = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = Path(f"{date}_vna_data.npz")
        base_dir = Path(outdir or self.save_dir)
        fpath = base_dir / fname
        # save data to npz file
        np.savez(fpath, **self.data)
        # reset data
        self._clear_data()
