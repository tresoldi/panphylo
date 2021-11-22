"""
Module with the class for the internal representation of data.
"""

# Import Python libraries
from collections import defaultdict


class PhyloData:
    def __init__(self):
        self.values = defaultdict(set)
        self.taxa = set()
        self.characters = set()

    # TODO: move to __setitem__? it is actually an "add"
    def add_value(self, taxon, character, value):
        """
        Add a value to a taxon, character pair.

        Nota the (taxon, character) pairs can carry more than
        one value, so that values are actually stored in sets
        """

        self.values[taxon, character].add(value)
        self.taxa.add(taxon)
        self.characters.add(character)

    def __getitem__(self, key):
        return self.values[key]

    # TODO: add total number of values
    def __repr__(self):
        return f"PhyloData with {len(self.taxa)} taxa and {len(self.characters)} characters."
