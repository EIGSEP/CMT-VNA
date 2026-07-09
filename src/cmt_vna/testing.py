import numpy as np

from . import VNA


class DummyResource:
    """
    Dummy PyVisa.Resource class for testing purposes.
    Parses SCPI write commands to track VNA state (npoints, fstart, fstop)
    and responds to query commands with synthetic data.
    """

    _DEFAULT_NPOINTS = 1000
    _DEFAULT_FSTART = 1e6
    _DEFAULT_FSTOP = 250e6

    def __init__(self):
        self.read_termination = None
        self.timeout = None
        self._npoints = self._DEFAULT_NPOINTS
        self._fstart = self._DEFAULT_FSTART
        self._fstop = self._DEFAULT_FSTOP
        # Real instruments default to ASCII transfer until FORM:DATA
        # is written; binary-block queries fail in that state.
        self._form_data = "ASC"

    def write(self, command):
        """Parse SCPI commands to track instrument state."""
        cmd = command.strip()
        if cmd.startswith("SENS1:FREQ:STAR"):
            parts = cmd.split()
            self._fstart = float(parts[1])
        elif cmd.startswith("SENS1:FREQ:STOP"):
            parts = cmd.split()
            self._fstop = float(parts[1])
        elif cmd.startswith("SENS1:SWE:POIN"):
            parts = cmd.split()
            self._npoints = int(float(parts[1]))
        elif cmd.startswith("FORM:DATA "):
            # per the RVNA SCPI manual, only ASCii|REAL|REAL32 are
            # valid; out-of-range values (e.g. Keysight-style
            # "REAL,64") mean "the command is ignored". The query
            # echo set is {ASC|REAL|REAL32}.
            value = cmd.split(maxsplit=1)[1].strip().upper()
            echo = {"ASC": "ASC", "ASCII": "ASC"}.get(value, value)
            if echo in ("ASC", "REAL", "REAL32"):
                self._form_data = echo

    def query(self, command):
        """Respond to simple SCPI queries."""
        cmd = command.strip()
        if cmd == "*IDN?":
            return "DummyVNA"
        if cmd == "*OPC?":
            return "1"
        if cmd == "FORM:DATA?":
            return self._form_data
        raise ValueError(f"Query command {command!r} not recognized by mock.")

    def query_binary_values(
        self, command, datatype="d", is_big_endian=True, container=None
    ):
        """
        Simulate querying binary array data from the VNA.

        Supports:
        - CALC:TRAC:DATA:FDAT? : interleaved real/imag S11 data
          (2 * npoints values, all zeros)
        - SENS1:FREQ:DATA? : frequency array (npoints values)

        Parameters
        ----------
        command : str
            SCPI query command.
        datatype : str
            Data type format character (ignored in mock).
        is_big_endian : bool
            Byte order (ignored in mock).
        container : callable or None
            Container for the returned data (e.g. np.array).

        Returns
        -------
        data : np.ndarray or list
            Simulated data response from the VNA.

        """
        if not self._form_data.startswith("REAL"):
            # mimic pyvisa on hardware: an ASCII reply carries no IEEE
            # block header, so binary parsing fails
            raise ValueError(
                'Could not find hash sign ("#") indicating the start '
                "of the block: instrument data format is "
                f"{self._form_data!r}"
            )
        cmd = command.strip()
        if cmd == "CALC:TRAC:DATA:FDAT?":
            data = np.zeros(2 * self._npoints)
        elif cmd == "SENS1:FREQ:DATA?":
            data = np.linspace(self._fstart, self._fstop, self._npoints)
        else:
            raise ValueError(f"Command {command!r} not recognized by mock.")
        if container is not None:
            data = container(data)
        return data

    def close(self):
        pass


class DummyVNA(VNA):
    """
    Mock VNA for testing purposes. Uses DummyResource instead of a real
    PyVISA connection. All base class methods work through the stateful
    DummyResource, so the code paths match the real VNA as closely as
    possible.
    """

    # Resource class to instantiate; tests override this to model
    # cold-start / never-ready instrument servers.
    _resource_cls = DummyResource

    def _open_resource(self):
        """
        Override _open_resource to use DummyResource instead of real
        PyVISA. The base class _configure_vna still runs, so the SCPI
        config push and the verify loop are exercised for real.
        """
        s = self._resource_cls()
        s.read_termination = "\n"
        s.timeout = self.vna_timeout
        return s
