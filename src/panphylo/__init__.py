"""
panphylo __init__.py
"""

# Version of the panphylo package
__version__ = "0.3"  # remember to sync in setup.py and biblioref
__author__ = "Tiago Tresoldi"
__email__ = "tiago.tresoldi@lingfil.uu.se"

from typing import *

# Import from local modules
from .common import indexes2ranges, unique_ids  # For testing purposes
from .common_io import smart_open, fetch_stream_data
from .nexus import read_data_nexus, build_nexus
from .phylip import read_data_phylip, build_phylip
from .phylodata import binarize
from .tabular import detect_delimiter, read_data_tabular, build_tabular


# Dispatch the different reading methods
def convert(source: str, args: Dict[str, str]) -> str:
    """
    Main function for conversion.

    @param source: The entire source of the file to be converted.
    @param args: A dictionary with all configuration, as built from
        command-line arguments.
    @return: The source converted to the requested format.
    """

    # Dispatch to the right reading method
    if args["from"] == "tabular":
        phyd = read_data_tabular(source, detect_delimiter(source), args)
    elif args["from"] == "csv":
        phyd = read_data_tabular(source, ",", args)
    elif args["from"] == "tsv":
        phyd = read_data_tabular(source, "\t", args)
    elif args["from"] == "nexus":
        phyd = read_data_nexus(source, args)
    elif args["from"] == "phylip":
        phyd = read_data_phylip(source, args)
    else:
        raise ValueError("Invalid reading format `%s`.", args["from"])

    # Perform all requested data manipulations
    phyd.slug_taxa(args.get("slug_taxa", "none"))
    if args.get("binarize", False):
        phyd = binarize(phyd)

    # Write converted data in the requested format; note that the command-line
    # handling should have taken care of replacing the "auto" value for
    # auto-detecting the output
    if args["to"] == "csv":
        converted = build_tabular(phyd, ",", args)
    elif args["to"] == "tsv":
        converted = build_tabular(phyd, "\t", args)
    elif args["to"] == "nexus":
        converted = build_nexus(phyd, args)
    elif args["to"] == "phylip":
        converted = build_phylip(phyd, args)
    else:
        raise ValueError("Invalid output format `%s`.", args["to"])

    return converted

# Build namespace
# __all__ = ["convert", "indexes2ranges"]
