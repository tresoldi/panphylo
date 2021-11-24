"""
Module with the class for the internal representation of data.
"""

# Import Python libraries
from collections import defaultdict, Counter
import string

from .common import unique_ids


class PhyloData:
    def __init__(self):
        self.values = defaultdict(set)
        self.taxa = set()
        self.characters = set()

    @property
    def charvalues(self):
        """
        Return a sorted character values structure.

        Note that this method is not caching results; while it might involve more and unnecessary computations in
        some contexts, it does not affect our intended usage and makes the code easier to follow.
        """

        # Collect with a counter first
        counter = defaultdict(Counter)
        for (_, character), values in self.values.items():
            counter[character].update({value for value in values if value != "?"})

        # Sort by frequency
        # TODO; add option to sort alphabetically
        # TODO: what if there are equal frequencies? Is it reproducible?
        charvalues = {
            character: [val for val, _ in values.most_common()]
            for character, values in counter.items()
        }

        return charvalues

    # TODO: cache? along with charvalues?
    @property
    def char_cardinality(self):
        """
        Return the character cardinality.

        Character cardinality is defined as the number of values in the character(s) with the largest
        number of values.
        """

        return max([len(value_set) for value_set in self.charvalues.values()])

    @property
    def symbols(self):
        """
        Return a set of unique symbols for representing states.

        The length of the vector will follow the cardinality of the data (i.e., `self.char_cardinality`).
        """

        return [char for char in string.digits + string.ascii_uppercase][
            : self.char_cardinality
        ]

    def slug_taxa(self):
        """
        Slug taxa labels, making sure uniqueness of IDs is preserved.
        """

        # Build map with unique ids, update self.taxa, and update self.values
        slug_map = {
            source: target for source, target in zip(self.taxa, unique_ids(self.taxa))
        }

        self.taxa = set(slug_map.values())

        self.values = {
            (slug_map[taxon], character): values
            for (taxon, character), values in self.values.items()
        }

    def slug_characters(self):
        """
        Slug character labels, making sure uniqueness of IDs is preserved.
        """

        # Build map with unique ids, update self.characters, and update self.values
        slug_map = {
            source: target
            for source, target in zip(self.characters, unique_ids(self.characters))
        }

        self.characters = set(slug_map.values())

        self.values = {
            (taxon, slug_map[character]): values
            for (taxon, character), values in self.values.items()
        }

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
