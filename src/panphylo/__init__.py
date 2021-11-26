"""
panphylo __init__.py
"""

# Version of the panphylo package
__version__ = "0.1"  # remember to sync in setup.py
__author__ = "Tiago Tresoldi"
__email__ = "tiago.tresoldi@lingfil.uu.se"

# Import from local modules
from .common import indexes2ranges, smart_open, fetch_stream_data
from .nexus import read_data_nexus, build_nexus
from .phylip import read_data_phylip, build_phylip
from .tabular import detect_delimiter, read_data_tabular, build_tabular


# Dispatch the different reading methods
def convert(source, args):

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

    # Perform all requested data manipulations
    phyd.slug_taxa(args.get("slug_taxa", "none"))
    phyd.slug_characters(args.get("slug_chars", "none"))
    if args.get("binarize", False):
        phyd = phyd.binarize()

    # Write converted data in the requested format; note that the command-line
    # handling should have taken care of replacing the "auto" value for
    # autodetecting the output
    # TODO: adapt to have them returning strings, and writing with a separate function
    if args["to"] == "csv":
        converted = build_tabular(phyd, ",", args)
    elif args["to"] == "tsv":
        converted = build_tabular(phyd, "\t", args)
    elif args["to"] == "nexus":
        converted = build_nexus(phyd, args)
    elif args["to"] == "phylip":
        converted = build_phylip(phyd, args)

    return converted


# Build namespace
__all__ = ["convert", "indexes2ranges", "smart_open", "fetch_stream_data"]
