"""
Module with the class for the internal representation of data.
"""

# Import Python libraries
from collections import defaultdict, Counter
import enum
import string

# Import from local modules
from .common import unique_ids

# TODO; should have a general method for iterating over
#       characters in a sorter order
# TODO: have maximum taxon length here as well

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
    """
    Class for the internal representation of phylogenetic data.
    """

    def __init__(self):
        """
        Initialize the class.
        """

        self.characters = set()
        self.charset = defaultdict(set)
        self.taxa = set()
        self.values = defaultdict(set)

    @property
    def charstates(self):
        """
        Return a sorted character states structure.

        Note that this method is not caching results; while it might involve
        more and unnecessary computations in some contexts, it does not affect
        our intended usage and makes the code easier to follow.

        :return: A dictionary with the character states.
        """

        # Collect with a counter first
        char_counter = defaultdict(Counter)
        for (_, character), states in self.values.items():
            char_counter[character].update({state for state in states if state != "?"})

        # Sort by frequency
        # TODO; add option to sort alphabetically
        # TODO: what if there are equal frequencies? Is it reproducible?
        # NOTE: for some reason the list comprehension is failing in brython
        charstates = {}
        for character, states in char_counter.items():
            charstates[character] = [state for state, _ in states.most_common()]

        return charstates

    @property
    def char_cardinality(self) -> int:
        """
        Return the character cardinality.

        Character cardinality is defined as the number of states in the
        character(s) with the largest number of states.

        :return: An integer with the cardinality of the largest character.
        """

        return max([len(state_set) for state_set in self.charstates.values()])

    @property
    def matrix(self) -> list:
        """
        Build a sorted matrix from the internal representation.

        The matrix is returned as a list and is suitable for formats
        such as NEXUS and PHYLIP.

        :return: A sorted list with dictionaries carrying taxon and
            vector information.
        """

        # Build a sorted list with the matrix
        _matrix = defaultdict(str)
        symbols = self.symbols  # cache
        for character, state_set in self.charstates.items():
            for taxon in self.taxa:
                # TODO: assuming there is only one value per site!!! (value[0]), [None]
                state = self.values.get((taxon, character), [None])
                state = list(state)[0]
                if not state:
                    _matrix[taxon] += "-"
                elif state == "?":
                    _matrix[taxon] += "?"
                else:
                    _matrix[taxon] += symbols[state_set.index(state)]

        ret = [{"taxon": taxon, "vector": vector} for taxon, vector in _matrix.items()]
        ret = sorted(ret, key=lambda e: e["taxon"])

        return ret

    @property
    def symbols(self):
        """
        Return a colloction of unique symbols for representing states.

        The length of the vector will follow the cardinality of the data
        (i.e., `self.char_cardinality`).

        :return: A list with the characters for representing the states.
        """

        return [ch for ch in string.digits + string.ascii_uppercase][
            : self.char_cardinality
        ]

    def slug_taxa(self, level="simple"):
        """
        Slug taxa labels, making sure uniqueness of IDs is preserved.
        """

        # If level is "none", we only make sure the IDs are now unique

        # Build map with unique ids, update self.taxa, and update self.values
        slug_map = {
            source: target
            for source, target in zip(self.taxa, unique_ids(self.taxa, level))
        }

        self.taxa = set(slug_map.values())

        new_values = defaultdict(set)
        for (taxon, character), values in self.values.items():
            new_values[taxon, character].update(values)
        self.values = new_values

    def slug_characters(self, level="simple"):
        """
        Slug character labels, making sure uniqueness of IDs is preserved.
        """

        # Build map with unique ids, update self.characters, and update self.values
        slug_map = {
            source: target
            for source, target in zip(
                self.characters, unique_ids(self.characters, level)
            )
        }

        self.characters = set(slug_map.values())

        new_values = defaultdict(set)
        for (taxon, character), values in self.values.items():
            new_values[taxon, character].update(values)
        self.values = new_values

    def binarize(self):
        # TODO: collect assumptions

        # For each taxon, collect a map of which charvalues are observed; this does not modify the
        # internal properties
        charvalues = self.charstates  # cache
        binary_values = {}
        for taxon in self.taxa:
            for character, values in self.charstates.items():
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
                # Add ascertainment
                # TODO: allow something different from "0"?
                # TODO: should check for the name of the character?
                bin_phyd.add_value(
                    taxon, f"{character}_ASCERTAINMENT", "0", charset=character
                )

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
