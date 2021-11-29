"""
Module with functions and methods for PHYLIP files.
"""

import re

# Import from local modules
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
def build_phylip(phyd, args):

    # Obtain the matrix and the maximum taxon length for formatting
    matrix = phyd.matrix
    taxon_length = max([len(entry["taxon"]) for entry in matrix])

    # Build buffer
    buffer = """
%i %i
%s
""" % (
        len(phyd.taxa),
        len(phyd.characters),
        "\n".join(
            [
                "%s    %s" % (entry["taxon"].ljust(taxon_length), entry["vector"])
                for entry in matrix
            ]
        ),
    )

    return buffer
