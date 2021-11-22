"""
panphylo __init__.py
"""

# Version of the ngesh package
__version__ = "0.1"  # remember to sync in setup.py
__author__ = "Tiago Tresoldi"
__email__ = "tiago.tresoldi@lingfil.uu.se"

# Import from local modules
from .common import common_dummy

# Build namespace
__all__ = ["common_dummy"]
