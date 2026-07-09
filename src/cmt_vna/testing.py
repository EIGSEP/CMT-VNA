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
        # like the Linux cmtvna server, unrecognized writes (notably
        # the whole FORMat subsystem) are silently ignored

    def query(self, command):
        """Respond to simple SCPI queries."""
        cmd = command.strip()
        if cmd == "*IDN?":
            return "DummyVNA"
        if cmd == "*OPC?":
            return "1"
        raise ValueError(f"Query command {command!r} not recognized by mock.")

    def query_ascii_values(self, command, container=list):
        """
        Simulate querying ASCII array data from the VNA — the only
        transfer format the Linux cmtvna server supports (it ignores
        the FORMat subsystem, so binary transfer is unavailable).

        Supports:
        - CALC:DATA:SDAT? : interleaved real/imag S11 data
          (2 * npoints values, all zeros)
        - SENS1:FREQ:DATA? : frequency array (npoints values)

        Parameters
        ----------
        command : str
            SCPI query command.
        container : callable
            Container for the returned data (e.g. np.array).

        Returns
        -------
        data : np.ndarray or list
            Simulated data response from the VNA.

        """
        cmd = command.strip()
        if cmd == "CALC:DATA:SDAT?":
            data = np.zeros(2 * self._npoints)
        elif cmd == "SENS1:FREQ:DATA?":
            data = np.linspace(self._fstart, self._fstop, self._npoints)
        else:
            raise ValueError(f"Command {command!r} not recognized by mock.")
        return container(data)

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
