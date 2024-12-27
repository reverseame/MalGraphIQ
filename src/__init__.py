"""
MalGraphIQ: Transform your malware sandbox reports and execution traces into behavior and category graphs.
"""

# Package Metadata
__version__ = "1.3.37"
__author__ = "Razvan Raducu, Ricardo J. Rodríguez, and Pedro Álvarez"
__license__ = "GPL 3.0"

# Package Initialization Logic
import logging

# Set up package-wide logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MalGraphIQ")