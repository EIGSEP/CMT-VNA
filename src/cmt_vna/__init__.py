from importlib.metadata import version

__author__ = "Christian Hellum Bye, Charlie Tolley"
__version__ = version("eigsep-vna")

from .vna import VNA
from . import calkit, testing
