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
from .common import smart_open
from .tabular import detect_delimiter, read_data_tabular, write_data_tabular


def fetch_stream_data(args):
    """
    Read the input data as a string.

    The function takes care of handling input from both stdin and
    files, decoding the stream of bytes according to the user-specified
    character encoding (including automatic detection if necessary).
    """

    # Fetch all input as a sequence of bytes, so that we don't consume stdout
    # and can still run autodetection on format and encoding
    with smart_open(args["input"], "rb") as handler:
        raw_source = handler.read()

        # Detect encoding if necessary, building a string
        if args["encoding"] != "auto":
            encoding = args["encoding"]
        else:
            detect = chardet.detect(raw_source)
            encoding = detect["encoding"]
            logging.debug(
                "Encoding detected as `%s` (confidence: %.2f)",
                detect["encoding"],
                detect["confidence"],
            )

        source = raw_source.decode("utf-8")

    return source


# Dispatch the different reading methods
def read_input(args):
    # Read source data
    source = fetch_stream_data(args)

    # Decide on the right input function based on the input format, which might
    # involve auto-detection
    if args["from"] == "tabular":
        phyd = read_data_tabular(source, detect_delimiter(source), args)
    elif args["from"] == "csv":
        phyd = read_data_tabular(source, ",", args)
    elif args["from"] == "tsv":
        phyd = read_data_tabular(source, "\t", args)
    else:
        # Fallback, autodetect the format
        print("autodetect")

    # Write converted data in the requested format; note that the command-line
    # handling should have taken care of replacing the "auto" value for
    # autodetecting the output
    if args["to"] == "csv":
        write_data_tabular(args, phyd, delimiter=",")
    elif args["to"] == "tsv":
        write_data_tabular(args, phyd, delimiter="\t")


# Build namespace
__all__ = ["read_input"]
