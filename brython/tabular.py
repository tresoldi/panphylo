"""
Module with functions and methods for tabular files.
"""

# Import Python libraries
import logging

# Import from local modules
from common import slug
from internal import PhyloData


def detect_delimiter(source):
    """
    Detect the tabular dialect (e.g. CSV and TSV of a file).

    The detection is extremely simplified, based on frequency
    """

    lines = source.split("\n")
    commas = lines[0].count(",")
    tabs = lines[0].count("\t")
    logging.debug("Header has %i commas and %i tabs.", commas, tabs)
    if commas >= tabs:
        delimiter = ","
    else:
        delimiter = "\t"

    return delimiter


def _get_input_column_names(args, data):
    """
    Obtain column names, either provided or inferred.
    """

    # If the column names for taxa, characters, and values was not provided,
    # try to infer it; at the end, we make sure to check that they are all unique
    col_taxa = args.get("i_taxa", None)
    col_char = args.get("i_char", None)
    col_state = args.get("i_state", None)

    if not all([col_taxa, col_char, col_state]):
        logging.debug("Inferring column names.")

        # Get the keys we have and remove and column name already used
        columns = [
            col for col in data[0].keys() if col not in [col_taxa, col_char, col_state]
        ]

        # Obtain the taxa column among potential candidates, picking the first one
        for cand in [
            "taxon",
            "species",
            "language",
            "doculect",
            "manuscript",
            "witness",
        ]:
            for column in columns:
                if not col_taxa and cand in slug(column, "full"):
                    col_taxa = column

        # Obtain the char column among potential candidates, picking the first one
        for cand in ["character", "feature", "property", "position"]:
            for column in columns:
                if not col_char and cand in slug(column, "full"):
                    col_char = column

        # Obtain the value column among potential candidates, picking the first one
        for cand in ["state", "value", "observation", "cognate", "lesson", "reading"]:
            for column in columns:
                if not col_state and cand in slug(column, "full"):
                    col_state = column

    column_names = [col_taxa, col_char, col_state]
    if len(set(column_names)) < 3:
        raise AssertionError("Non-unique column names in %s", str(column_names))

    return column_names


# TODO: allow to prohibit column inference (should even be default?)
def read_data_tabular(source_str, delimiter, args):
    """
    Read data in tabular format.
    """

    # Read all data
    rows = source_str.split("\n")
    rows = [row for row in rows if row.strip()]
    header = rows[0].split(delimiter)
    source = [
        {key: value for key, value in zip(header, row.split(delimiter))}
        for row in rows[1:]
    ]
    logging.debug("Read %i entries from `%s`.", len(source), args["input"])

    # Infer column names
    col_taxa, col_char, col_vals = _get_input_column_names(args, source)

    # Build internal representation
    phyd = PhyloData()
    for entry in source:
        phyd.add_value(entry[col_taxa], entry[col_char], entry[col_vals])

    return phyd


def build_tabular(phyd, delimiter, args):
    # If the column names for taxa, characters, and states was not provided,
    # try to infer it; at the end, we make sure to check that they are all unique
    col_taxa = args.get("o-taxa", "Taxon")
    col_char = args.get("o-char", "Character")
    col_state = args.get("o-state", "State")

    # Build output data
    output = []
    for character in sorted(phyd.characters):
        for taxon in sorted(phyd.taxa):
            for value in sorted(phyd[taxon, character]):  # TODO: deal with missing
                output.append({col_taxa: taxon, col_char: character, col_state: value})

    # Build buffer
    # TODO: deal with escapes, etc. (csv library is missing in JS)
    fieldnames = [col_taxa, col_char, col_state]
    buffer = [delimiter.join([row[field] for field in fieldnames]) for row in output]
    buffer = [delimiter.join(fieldnames)] + buffer
    buffer = "\n".join(buffer)

    return buffer
