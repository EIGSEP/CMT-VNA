__author__ = "Christian Hellum Bye, Charlie Tolley"
__version__ = "0.0.1"

try:
    from cmt_vna.vna import VNA
except ImportError:
    print(
        "Not importing VNA, as it requires pyvisa and pyvisa-py. Can't connect"
        "to VNA, but can still calibrate and use the calibration kit."
    )
from cmt_vna import calkit
