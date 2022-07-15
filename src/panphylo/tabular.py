"""
Module with functions and methods for tabular files.
"""

# Import Python standard libraries
import logging

# Import from local modules
from .common import slug, unique_ids
from .phylodata import PhyloData


def detect_delimiter(source: str) -> str:
    """
    Detect the tabular dialect (e.g. CSV and TSV of a file).

    The detection is extremely simplified, based on frequency in the first line.

    @param source: The tabular source for the data.
    @return: The character detected as field separator.
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


# TODO: return `column_names` as a dictionary
def _get_input_column_names(args: dict, data):
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
def read_data_tabular(source_str: str, delimiter: str, args: dict) -> PhyloData:
    """
    Parse a TABULAR source into an internal representation.

    :param source_str: A string with the source data representation.
    :param delimiter: A string with the character to be used as field delimiter.
    :param args:
    :return: An object with the internal representation of the data.
    """

    # Read all data, dealing with Windows "\r"
    rows = source_str.replace("\r", "").split("\n")
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
        phyd.extend((entry[col_taxa], entry[col_char]), entry[col_vals])

    return phyd


def build_tabular(phyd: PhyloData, delimiter: str, args: dict) -> str:
    """
    Build a TABULAR data representation.

    :param phyd: The PhyloData object used as source of the data representation.
    :param delimiter: The character to be used as field delimiter.
    :param args:
    :return: A textual representation of the NEXUS data representation.
    """

    # If the column names for taxa, characters, and states was not provided,
    # try to infer it; at the end, we make sure to check that they are all unique
    # TODO: default to i-taxa, i-char, and i-state (needs returning)
    col_taxa = args.get("o-taxa", "Taxon")
    col_char = args.get("o-char", "Character")
    col_state = args.get("o-state", "State")

    # Build output data, slugging identifiers as needed
    taxa_map = {
        source: target
        for source, target in zip(
            phyd.taxa, unique_ids(phyd.taxa, args.get("slug_taxa", "none"))
        )
    }
    char_map = {
        source: target
        for source, target in zip(
            phyd.characters, unique_ids(phyd.characters, args.get("slug_chars", "none"))
        )
    }

    # Build sorted output
    output = []
    for character in phyd.characters:
        for taxon in phyd.taxa:
            for state in phyd[taxon, character]:  # TODO: deal with missing; sort
                output.append(
                    {
                        col_taxa: taxa_map[taxon],
                        col_char: char_map[character],
                        col_state: state,
                    }
                )

    # Sort, taking care of placing ascertained features first (computationally
    # quite expensive)
    output = sorted(
        output,
        key=lambda e: (
            e[col_char].replace("_ASCERTAINMENT", ""),
            "_ASCERTAINMENT" in e[col_char],
            e[col_taxa],
            e[col_state],
        ),
    )

    # Build buffer
    fieldnames = [col_taxa, col_char, col_state]
    buffer = [delimiter.join([row[field] for field in fieldnames]) for row in output]
    buffer = [delimiter.join(fieldnames)] + buffer
    buffer = "\n".join(buffer)

    return buffer
