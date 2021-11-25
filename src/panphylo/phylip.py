"""
Module with functions and methods for PHYLIP files.
"""

import re
from collections import defaultdict

# Import from local modules
from .common import smart_open
from .internal import PhyloData

# TODO: implement https://www.bioinformatics.org/sms/iupac.html
# TODO: currently only supporting non interleaved


def read_data_phylip(source, args):

    # Read raw data
    data = {}
    lines = source.strip().split("\n")

    match = re.search(r"(\d+) (\d+)", lines[0])
    ntax, nchar = int(match.group(1)), int(match.group(2))

    alms = [line.strip() for line in lines[1:] if line.strip()]
    for alm in alms:
        match = re.search(r"(\S+)\s+(.+)", alm)
        vector = match.group(2).replace(" ", "").upper()
        data[match.group(1)] = vector

    # Validate
    if len(data) != ntax:
        raise ValueError("Mismatch in number of taxa.")

    vector_lens = set([len(vector) for vector in data.values()])
    if len(vector_lens) != 1:
        raise ValueError("Mismatch in alignment lengths.")
    if list(vector_lens)[0] != nchar:
        raise ValueError("Alignment lengths differs from the one in the header.")

    # Add to PhyloData
    # TODO: add padding in the character names
    phyd = PhyloData()
    for taxon, vector in data.items():
        for char_idx, char_state in enumerate(vector):
            if char_state != "-":
                phyd.add_value(taxon, f"CHAR_{char_idx}", char_state)

    return phyd


# TODO: sharing matrix code in common with NEXUS, should move to PhyloData
def write_data_phylip(phyd, args):

    # Build a sorted list with the matrix
    matrix_dict = defaultdict(str)
    symbols = phyd.symbols
    for character, value_set in phyd.charvalues.items():
        for taxon in phyd.taxa:
            # TODO: assuming there is only one value per site!!! (value[0]), [None]
            value = phyd.values.get((taxon, character), [None])
            value = list(value)[0]
            if not value:
                matrix_dict[taxon] += "-"
            elif value == "?":
                matrix_dict[taxon] += "?"
            else:
                # TODO: note the sorted
                symbol_idx = value_set.index(value)
                matrix_dict[taxon] += symbols[symbol_idx]

    matrix_list = sorted([(taxon, vector) for taxon, vector in matrix_dict.items()])

    # Build buffer
    taxon_length = max([len(taxon) for taxon in matrix_dict])
    buffer = """
%i %i

%s
""" % (
        len(phyd.taxa),
        len(phyd.characters),
        "\n".join(
            [
                "%s    %s" % (taxon.ljust(taxon_length), vector)
                for taxon, vector in matrix_list
            ]
        ),
    )

    # Write to the stream
    with smart_open(args["output"], "w", encoding="utf-8") as handler:
        handler.write(buffer)
