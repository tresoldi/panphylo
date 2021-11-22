"""
Module with functions and methods for tabular files.
"""

# Import Python libraries
import csv
import logging

# Import from local modules
from .common import slug

# TODO: should really specify a default encoding?
def detect_delimiter(filename, encoding):
    """
    Detect the tabular dialect (e.g. CSV and TSV of a file).

    The detection is extremely simplified, based on frequency
    """

    with open(filename, encoding=encoding) as handler:
        logging.debug("Read header line from `%s`.", filename)
        line = handler.readlines(1)[0]

    commas = line.count(",")
    tabs = line.count("\t")
    logging.debug("Header has %i commas and %i tabs.", commas, tabs)
    if commas >= tabs:
        delimiter = ","
    else:
        delimiter = "\t"

    return delimiter

def _get_column_names(args, data):
    """
    Obtain column names, either provided or inferred.
    """

    # If the column names for taxa, characters, and values was not provided,
    # try to infer it; at the end, we make sure to check that they are all unique
    col_taxa = args.get("l-taxa", None)
    col_char = args.get("l-char", None)
    col_vals = args.get("l-vals", None)
    if not all([col_taxa, col_char, col_vals]):
        logging.debug("Inferring column names.")

        # Get the keys we have and remove and column name already used
        columns = [col for col in data[0].keys() if col not in [col_taxa, col_char, col_vals]]

        # Obtain the taxa column among potential candidates, picking the first one
        for cand in ["taxon", "species", "language", "doculect", "manuscript", "witness"]:
            for column in columns:
                if not col_taxa and cand in slug(column):
                    col_taxa = column

        # Obtain the char column among potential candidates, picking the first one
        for cand in ["character", "feature", "property", "position"]:
            for column in columns:
                if not col_char and cand in slug(column):
                    col_char = column

        # Obtain the value column among potential candidates, picking the first one
        for cand in ["value", "observation", "cognate", "lesson", "reading"]:
            for column in columns:
                if not col_vals and cand in slug(column):
                    col_vals = column

    column_names = [col_taxa, col_char, col_vals]
    if len(set(column_names)) < 3:
        raise AssertionError("Non-unique column names in %s", str(column_names))

    return column_names    

# TODO: allow to prohibit column inference (should even be default?)
def read_data_tabular(args, delimiter, encoding):
    """
    Read data in tabular format.
    """

    # Read all data
    with open(args["input"], encoding=encoding) as handler:
        data = list(csv.DictReader(handler, delimiter=delimiter))
        logging.debug("Read %i entries from `%s`.", len(data), args["input"])
    
    # Infer column names
    col_taxa, col_char, col_vals = _get_column_names(args, data)