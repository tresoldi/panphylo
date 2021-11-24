"""
Module with the class for the internal representation of data.
"""

# Import Python libraries
from collections import defaultdict, Counter
import string
import enum

from .common import unique_ids

# TODO: should have one for non-binary as well?
class BinaryObs(enum.Enum):
    """
    Auxiliary class for binary observations.

    The class allows to easily deal with missing data and gaps.
    """

    FALSE = enum.auto()
    TRUE = enum.auto()
    MISSING = enum.auto()
    GAP = enum.auto()


BINARY_OPS_MAP = {
    BinaryObs.FALSE: "0",
    BinaryObs.TRUE: "1",
    BinaryObs.MISSING: "?",
    BinaryObs.GAP: "-",
}


class PhyloData:
    def __init__(self):
        self.values = defaultdict(set)
        self.taxa = set()
        self.characters = set()
        self.charset = defaultdict(set)

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

    def binarize(self):
        # TODO: missing ascertainment!
        # TODO: collect assumptions

        # For each taxon, collect a map of which charvalues are observed; this does not modify the
        # internal properties
        charvalues = self.charvalues  # cache
        binary_values = {}
        for taxon in self.taxa:
            for character, values in self.charvalues.items():
                obs = self.values.get((taxon, character), None)

                if not obs:
                    binary_values[taxon, character] = [
                        BinaryObs.GAP for val in charvalues[character]
                    ]
                else:
                    if tuple(obs) == "?":
                        binary_values[taxon, character] = [
                            BinaryObs.MISSING for val in charvalues[character]
                        ]
                    else:
                        binary_values[taxon, character] = [
                            BinaryObs.TRUE if val in obs else BinaryObs.FALSE
                            for val in charvalues[character]
                        ]

        # Build a new phylogenetic data structure, adding the new characters one by one
        bin_phyd = PhyloData()
        for (taxon, character), value in binary_values.items():
            for obs, value_name in zip(value, charvalues[character]):
                # TODO: confirm if it is right to skip over gaps and all
                if obs != BinaryObs.GAP:
                    bin_phyd.add_value(
                        taxon,
                        f"{character}_{value_name}",
                        BINARY_OPS_MAP[obs],
                        charset=character,
                    )

        return bin_phyd

    # TODO: move to __setitem__? it is actually an "add"
    def add_value(self, taxon, character, value, charset=None):
        """
        Add a value to a taxon, character pair.

        Nota the (taxon, character) pairs can carry more than
        one value, so that values are actually stored in sets
        """

        self.values[taxon, character].add(value)
        self.taxa.add(taxon)
        self.characters.add(character)

        if charset:
            self.charset[charset].add(character)

    def __getitem__(self, key):
        return self.values[key]

    # TODO: add total number of values
    def __repr__(self):
        return f"PhyloData with {len(self.taxa)} taxa and {len(self.characters)} characters."
