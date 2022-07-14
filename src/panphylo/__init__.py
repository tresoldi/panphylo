"""
panphylo __init__.py
"""

# Version of the panphylo package
__version__ = "0.3"  # remember to sync in setup.py and biblioref
__author__ = "Tiago Tresoldi"
__email__ = "tiago.tresoldi@lingfil.uu.se"

# Import from Python standard libraries
from typing import *

# Import from local modules
from .common import indexes2ranges, unique_ids  # For testing purposes
from .common_io import smart_open, fetch_stream_data
from .nexus import read_data_nexus, build_nexus
from .phylip import read_data_phylip, build_phylip
from .phylodata import binarize
from .tabular import detect_delimiter, read_data_tabular, build_tabular


def convert(source: str, args: Dict[str, str]) -> str:
    """
    Main function for data conversion.

    @param source: The entire source of the file to be converted.
    @param args: A dictionary with the full configuration, as built from
        command-line arguments.
    @return: The source converted to the requested format.
    """

    # Dispatch to the right reading method
    if args["from"] == "tabular":
        phylodata = read_data_tabular(source, detect_delimiter(source), args)
    elif args["from"] == "csv":
        phylodata = read_data_tabular(source, ",", args)
    elif args["from"] == "tsv":
        phylodata = read_data_tabular(source, "\t", args)
    elif args["from"] == "nexus":
        phylodata = read_data_nexus(source, args)
    elif args["from"] == "phylip":
        phylodata = read_data_phylip(source, args)
    else:
        raise ValueError("Invalid input format `%s`.", args["from"])

    # Perform all requested data manipulations
    phylodata.slug_taxa(args.get("slug_taxa", "none"))
    if args.get("binarize", False):
        phylodata = binarize(phylodata, args["ascertainment"])

    # Write converted data in the requested format; note that the command-line
    # handling should have taken care of replacing the "auto" value for
    # auto-detecting the output
    if args["to"] == "csv":
        converted = build_tabular(phylodata, ",", args)
    elif args["to"] == "tsv":
        converted = build_tabular(phylodata, "\t", args)
    elif args["to"] == "nexus":
        converted = build_nexus(phylodata, args)
    elif args["to"] == "phylip":
        converted = build_phylip(phylodata, args)
    else:
        raise ValueError("Invalid output format `%s`.", args["to"])

    return converted


# TODO: implement upon release
# Build namespace
# __all__ = ["convert", "indexes2ranges"]
