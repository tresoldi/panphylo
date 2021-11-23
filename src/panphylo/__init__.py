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

# Dispatch the different reading methods
def read_input(args):
    # Detect input encoding if necessary
    if args["encoding"] == "auto":
        with smart_open(args["input"], "rb") as handler:
            logging.debug(
                "Reading contents of `%s` for encoding detection.", args["input"]
            )
            raw_data = handler.read()

        detect = chardet.detect(raw_data)
        logging.debug(
            "Encoding detected as `%s` (confidence: %.2f)",
            detect["encoding"],
            detect["confidence"],
        )
        encoding = detect["encoding"]
    else:
        encoding = args["encoding"]

    # Decide on the right input function based on the input format, which might
    # involve auto-detection
    if args["from"] == "tabular":
        phyd = read_data_tabular(
            args, detect_delimiter(args["input"], encoding), encoding
        )
    elif args["from"] == "csv":
        phyd = read_data_tabular(args, ",", encoding)
    elif args["from"] == "tsv":
        phyd = read_data_tabular(args, "\t", encoding)
    else:  # autodetect
        print("autodetect")

    print(repr(phyd))

    # Decide on the right output function based on the output format or, if not
    # provided, on the extension
    # TODO: move to argument parsing?
    if args["to"] != "auto":
        args_to = args["to"]
    else:
        if not "." in args["to"]:
            raise ValueError(
                "Unable to detect output format; please specify it with `--to`."
            )

        extension = args["to"].split(".")[-1]
        if extension == "csv":
            args_to = "csv"
        elif extension == "tsv":
            args_to = "tsv"
        else:
            raise ValueError(
                "Unable to detect output format; please specify it with `--to`."
            )

    if args_to == "csv":
        write_data_tabular(args, phyd, delimiter=",")
    elif args_to == "tsv":
        write_data_tabular(args, phyd, delimiter="\t")


# Build namespace
__all__ = ["read_input"]
