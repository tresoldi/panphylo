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
        self.states = defaultdict(set)
        self.taxa = set()
        self._charstates = None

    @property
    def charstates(self) -> dict:
        """
        Return a character states structure.

        Note that this method is not caching results; while it might involve
        more and unnecessary computations in some contexts, it does not affect
        our intended usage and makes the code easier to follow.

        :return: A dictionary with the character states.
        """

        if self._charstates is None:
            # Collect with a counter first
            char_counter = defaultdict(Counter)
            for (_, character), states in self.states.items():
                char_counter[character].update({state for state in states if state != "?"})

            # Sort by frequency
            self._charstates = {}
            for character, states in char_counter.items():
                self._charstates[character] = [state for state, _ in states.most_common()]

        return self._charstates

    @property
    def cardinality(self) -> int:
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
        for character in sorted(self.charstates):
            # TODO: sort state_set by frequency? not necessary if done by .charstates
            state_set = sorted(self.charstates[character])
            for taxon in self.taxa:
                state = self.states.get((taxon, character), [None])

                # TODO: assuming there is only one value per site!!! (value[0]), [None]
                if len(state) > 1:
                    state = sorted(state)[0]
                else:
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

        return [ch for ch in string.digits + string.ascii_uppercase][: self.cardinality]

    def slug_taxa(self, level="simple"):
        """
        Slug taxa labels, making sure uniqueness of IDs is preserved.
        """

        # Build map with unique ids, update self.taxa, and update self.values
        slug_map = {
            source: target
            for source, target in zip(self.taxa, unique_ids(self.taxa, level))
        }

        self.taxa = set(slug_map.values())

        new_values = defaultdict(set)
        for (taxon, character), values in self.states.items():
            new_values[taxon, character].update(values)
        self.states = new_values

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
        for (taxon, character), values in self.states.items():
            new_values[taxon, character].update(values)
        self.states = new_values

    def add_state(self, taxon: str, character: str, state: str, charset: str = None):
        """
        Add a state to a taxon, character pair.

        Note that the (taxon, character) pairs can carry more than
        one state, so that states are actually stored in sets
        """

        self.states[taxon, character].add(state)
        self.taxa.add(taxon)
        self.characters.add(character)

        if charset:
            self.charset[charset].add(character)

    # TODO: Decide on returing a sorted list
    def __getitem__(self, key: str) -> set:
        return self.states[key]

    # TODO: add total number of values
    def __repr__(self):
        return f"PhyloData with {len(self.taxa)} taxa and {len(self.characters)} characters."


# TODO: collect assumptions?
def binarize(phyd):
    """
    Build a binarized version of the current phylogenetic data.

    :param phyd: The PhyloData to binarize.
    :return: A binarized version of the current data.
    """

    # For each taxon, collect a map of which charstates are observed; this does not modify the
    # internal properties
    charstates = phyd.charstates  # cache
    binary_states = {}
    for taxon in phyd.taxa:
        for character, states in charstates.items():
            obs = phyd.states.get((taxon, character), None)

            if not obs:
                binary_states[taxon, character] = [BinaryObs.GAP for _ in states]
            else:
                if tuple(obs) == ("?",):
                    binary_states[taxon, character] = [
                        BinaryObs.MISSING for _ in states
                    ]
                else:
                    binary_states[taxon, character] = [
                        BinaryObs.TRUE if state in obs else BinaryObs.FALSE
                        for state in states
                    ]

    # Build a new phylogenetic data structure, adding the new characters one by one
    bin_phyd = PhyloData()
    for (taxon, character), states in binary_states.items():
        for obs, state_label in zip(states, charstates[character]):
            # Add ascertainment
            bin_phyd.add_state(
                taxon, f"{character}_ASCERTAINMENT", "0", charset=character
            )

            # TODO: confirm if it is right to skip over gaps
            if obs != BinaryObs.GAP:
                bin_phyd.add_state(
                    taxon,
                    f"{character}_{state_label}",
                    BINARY_OPS_MAP[obs],
                    charset=character,
                )

    return bin_phyd
