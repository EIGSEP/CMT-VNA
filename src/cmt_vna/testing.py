import numpy as np
import time

from . import VNA


class DummyResource:
    """
    Dummy PyVisa.Resource class for testing purposes.
    This class does not implement any real functionality.
    It is used to test the VNA class without needing a real connection.
    """

    def __init__(self, *args, **kwargs):
        pass

    def write(self, command):
        pass

    @property
    def mock_query_command(self):
        """
        The command that the mock will respond to when queried.
        This is used to simulate a query response.
        """
        return "CALC:TRAC:DATA:FDAT?"

    def query_ascii_values(self, command, container=None, npoints=1000):
        """
        Simulate querying a value from the VNA. The mock only
        implements the case where the request is for data. Thus
        ``command'' must as specified in the attribute
        `mock_query_command'. The data returned is complex-valued
        where even indices correspond to the real part and odd indices
        correspond to the imaginary part. The number of points returned
        is therefore `2 * npoints'.

        Parameters
        ----------
        command : str
            Must be `mock_query_command'.
        container : None
            Not used in this mock implementation.
        npoints : int
            Half the number of points to return.

        Returns
        -------
        data : np.ndarray
            Simulated data response from the VNA.

        Raises
        -------
        ValueError
            If the command is not `mock_query_command'.
        """
        if command != self.mock_query_command:
            raise ValueError(f"Command {command} not recognized by mock.")
        return np.zeros(2 * npoints)

    def close(self):
        pass


class DummyVNA(VNA):
    """
    Basic Mock VNA for testing purposes. This class passes all methods.
    Basic attributes are still set in the __init__ method.
    """

    def _configure_vna(self):
        """
        Override the _configure_vna method to do nothing, except
        replacing the attribute `s' that communicates with the VNA with
        a dummy resource that does nothng.
        """
        self.s = DummyResource()

    @property
    def id(self):
        """
        Override the id property to return a dummy ID.
        """
        return "DummyVNA"

    @property
    def freqs(self):
        """
        Override the freqs property to calculate the frequencies
        instead of reading from the VNA.

        Returns:
            np.ndarray: Array of frequencies.

        """
        try:
            f = np.linspace(self.fstart, self.fstop, self.npoints)
        except:
            f = None
        return f

    def wait_for_opc(self, wait=0, err=False):
        """
        Override the wait_for_opc method. Sleeps for `wait' seconds
        and optionally raises a TimeoutError if `err' is True.
        This is used to simulate the operation complete check.

        Parameters
        ----------
        wait : float
            Time to wait for the operation to complete in seconds.
        err : bool
            If True, raises an exception to simulate an error.

        Raises
        -------
        TimeoutError
           If `err' is True.

        """
        if wait > 0:
            time.sleep(wait)
        if err:
            raise TimeoutError("Operation timed out")
