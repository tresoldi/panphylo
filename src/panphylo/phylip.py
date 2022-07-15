"""
Module with functions and methods for PHYLIP files.
"""

# Import Python standard libraries
import math
import re

# Import from local modules
from .phylodata import PhyloData


# TODO: implement https://www.bioinformatics.org/sms/iupac.html
# TODO: currently only supporting non interleaved


def read_data_phylip(source: str, args: dict) -> PhyloData:
    """
    Parse a PHYLIP source into an internal representation.

    :param source: A string with the source data representation.
    :param args:
    :return: An object with the internal representation of the data.
    """

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
    phyd = PhyloData()
    digits = math.ceil(math.log(len(vector)) / math.log(10))
    for taxon, vector in data.items():
        for char_idx, char_state in enumerate(vector):
            if char_state != "-":
                phyd.extend((taxon, f"CHAR_{str(char_idx).zfill(digits)}"), char_state)

    return phyd


# Note: even though this shares code in common with the NEXUS output, for matters
# of organization it is better to keep them separate, as combining them into a single
# method (possibly residing in PhyloData) would introduce unnecessary overhead
def build_phylip(phyd: PhyloData, args: dict) -> str:
    """
    Build a PHYLIP data representation.

    @param phyd The PhyloData object used as source of the data representation.
    @return A textual representation of the PHYLIP data representation.
    """

    # Obtain the matrix and the maximum taxon length for formatting
    matrix = phyd.matrix
    taxon_length = max([len(taxon) for taxon, _ in matrix])

    # Build buffer
    buffer = """
%i %i
%s
""" % (
        len(phyd.taxa),
        len(phyd.characters),
        "\n".join(
            [
                "%s    %s" % (taxon.ljust(taxon_length), vector)
                for taxon, vector in matrix
            ]
        ),
    )

    return buffer
