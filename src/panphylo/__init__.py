"""
panphylo __init__.py
"""

# Version of the ngesh package
__version__ = "0.1"  # remember to sync in setup.py
__author__ = "Tiago Tresoldi"
__email__ = "tiago.tresoldi@lingfil.uu.se"

# Import Python libraries
import chardet
import logging

# Import from local modules
from argparse import Namespace
from .common import common_dummy
from .tabular import detect_delimiter, read_data_tabular

# Dispatch the different reading methods
def read_input(args):
    # Detect input encoding if necessary
    if args["encoding"] == "auto":
        with open(args["input"], "rb") as handler:
            logging.debug("Reading contents of `%s` for encoding detection.", args["input"])
            raw_data = handler.read()

        detect = chardet.detect(raw_data)
        logging.debug("Encoding detected as `%s` (confidence: %.2f)", detect["encoding"], detect["confidence"])
        encoding = detect["encoding"]
    else:
        encoding = args["encoding"]

    # Decide on the right input function based on the input format, which might
    # involve auto-detection
    if args["from"] == "tabular":
        read_data_tabular(args, detect_delimiter(args["input"], encoding), encoding)
    elif args["from"] == "csv":
        read_data_tabular(args, ",", encoding)
    elif args["to"] == "tsv":
       read_data_tabular(args, "\t", encoding)
    else: # autodetect
        print("autodetect")

# Build namespace
__all__ = ["common_dummy", "read_input"]
