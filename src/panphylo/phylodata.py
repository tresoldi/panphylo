"""
Module with the class for the internal representation of data.
"""

# Import Python libraries
from collections import defaultdict, Counter
import enum
import string
from typing import *

# Import from local modules
from .common import unique_ids


# TODO: add more automatic checks, such as for IUPAC
class Character:
    """
    Class for a column definition.
    """

    def __init__(self, states: Optional[set[str]] = None):
        """
        Initialize the Character.

        @param states: A sequence of states that the character
            allows, as a set of strings.
        """

        if not states:
            self._states = set()
        else:
            self._states = states

    @property
    def states(self) -> tuple[str]:
        """
        Return a comparable version of the states set.

        @return: A sorted tuple of the internal states set.
        """

        return tuple(sorted(self._states))

    def add_state(self, state: str):
        """
        Add a state to the character, if possible.

        @param state: The identifier for the state.
        """

        self._states.add(state)

    def binary(self) -> bool:
        """
        Checks whether the character is a binary one.

        Binary characters are defined as those that have only "0" and
        "1" as potential states.

        @return: A flag on whether the character is a binary one.
        """
        if self.states == ("0", "1"):
            return True

        return False

    def __len__(self) -> int:
        return len(self._states)

    def __repr__(self) -> str:
        return f"Character with {len(self._states)} states ({self.states})."


class PhyloData:
    """
    Class for the internal representation of phylogenetic data.
    """

    def __init__(self):
        # The list of taxa is store independently for convenience, as it could be drawn
        # from the list of observations
        self._taxa: set[str] = set()
        self._charset: dict[str, dict[str, Character]] = {}

        # Observations are dictionaries with a tuple of strings as keys (taxon, charset, character)
        # and a set of strings as the observed value
        self._obs: dict[tuple[str, str, str], set[str]] = defaultdict(set)

    @property
    def taxa(self) -> tuple[str]:
        """
        Return a comparable version of the taxa set.

        @return: A sorted tuple of the internal taxa set.
        """

        return tuple(sorted(self._taxa))

    @property
    def characters(self):
        # Collect the ordered list of charset_id/char_id to query; this allows to later
        # easily implement different strategies
        # TODO: how to implement different strategies with a property?
        characters = []
        for charset_id, charset in sorted(self._charset.items()):
            for char_id in sorted(charset):
                characters.append((charset_id, char_id))

        return characters

    @property
    def cardinality(self) -> int:
        """
        Return the character cardinality.

        Character cardinality is defined as the number of states in the
        character(s) with the largest number of states.

        @return: An integer with the cardinality of the largest character.
        """

        return max([max([len(char) for char in charset.values()]) for charset in self._charset.values()])

    @property
    def symbols(self) -> tuple[str]:
        """
        Return a collection of unique symbols for representing states.

        The length of the vector will follow the cardinality of the data
        (i.e., `self.cardinality`).

        @return: A list with the characters for representing the states.
        """

        return tuple([ch for ch in string.digits + string.ascii_uppercase][: self.cardinality])

    def __getitem__(self, item: tuple[str, str, str]) -> set[str]:
        """
        Return the observation for a taxon/charset/character tuple.

        @param item: A tuple with taxon, charset_id, and char_id, as stored when
            extending the phylogenetic data.
        @return: The set of values associated with the key, with an empty set if nothing was
            stored.
        """
        return self._obs.get(item, set())

    def extend(self, key: tuple[str, Optional[str], str], value: str):
        # Decompose the key
        taxon, charset, character = key

        # Extend the list of taxa
        self._taxa.add(taxon)

        # If no charset was provided (we are probably dealing with non-binary data),
        # create a "dummy" charset with the same name as the character
        if not charset:
            charset = character

        # Update internal information
        if charset in self._charset:
            # If the character already exist, just try to extend the list of states; otherwise,
            # build a new character
            if character in self._charset[charset]:
                self._charset[charset][character].add_state(value)
            else:
                self._charset[charset][character] = Character(states={value})
        else:
            # If the charset does not exist, create a dummy one and add the current character
            # TODO: check if it does not exist yet
            self._charset[charset] = {character: Character(states={value})}

        # Store information on the actual observed state; note that, as we allow multistates, this is
        # actually a set of values
        self._obs[taxon, charset, character].add(value)

    def matrix(self) -> list[str, str]:
        # Build the matrix representation
        matrix: dict[str, str] = defaultdict(str)
        symbols: tuple[str] = self.symbols  # cache
        for charset_id, char_id in self.characters:
            states = self._charset[charset_id][char_id].states  # TODO: use frequency or something else?
            for taxon in self.taxa:
                obs = self[taxon, charset_id, char_id]
                if obs:
                    obs_repr = [symbols[states.index(o)] for o in obs]
                    if len(obs_repr) == 1:
                        matrix[taxon] += obs_repr[0]
                    else:
                        matrix[taxon] += "(%s)" % ",".join(obs_repr)

        # Build the sorted representation and return
        return sorted(matrix.items())


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


class OldPhyloData:
    """
    Class for the internal representation of phylogenetic data.
    """

    def __init__(self):
        """
        Initialize the class.
        """

        self.taxa: set[str] = set()
        self.characters: set[str] = set()

        self.charset = defaultdict(set)
        self.states = defaultdict(set)
        self._charstates = None

    @property
    def charstates(self) -> dict[str, list[str]]:
        """
        Return a character states structure.

        Note that this method is not caching results; while it might involve
        more and unnecessary computations in some contexts, it does not affect
        our intended usage and makes the code easier to follow.

        @return: A dictionary with the character states for each character. States
            are listed in order of inverse frequency.
        """

        if self._charstates is None:
            # Collect with a counter first
            char_counter = defaultdict(Counter)
            for (_, character), states in self.states.items():
                char_counter[character].update({state for state in states if state != "?"})

            # Sort by frequency
            _charstates = {}
            for character, states in char_counter.items():
                _charstates[character] = [state for state, _ in states.most_common()]

            return _charstates

        return self._charstates

    @property
    def cardinality(self) -> int:
        """
        Return the character cardinality.

        Character cardinality is defined as the number of states in the
        character(s) with the largest number of states.

        @return: An integer with the cardinality of the largest character.
        """

        return max([len(state_set) for state_set in self.charstates.values()])

    @property
    def matrix(self) -> list[dict[str, str]]:
        """
        Build a sorted matrix from the internal representation.

        The matrix is returned as a list and is suitable for formats
        such as NEXUS and PHYLIP.

        @return: A sorted list with dictionaries carrying taxon and
            vector information.
        """

        # Build a sorted list with the matrix
        _matrix = defaultdict(str)
        symbols = self.symbols  # cache
        for character in sorted(self.charstates):
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
    def symbols(self) -> list[str]:
        """
        Return a colloction of unique symbols for representing states.

        The length of the vector will follow the cardinality of the data
        (i.e., `self.char_cardinality`).

        @return: A list with the characters for representing the states.
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

    # TODO: charset should be read from the internal mapping, not provided
    def add_state(self, taxon: str, character: str, state: str, charset: str = None):
        """
        Add a state to a (taxon, character) pair.

        Note that the (taxon, character) pairs can carry more than
        one state, so that states are actually stored in sets

        @param taxon: The taxon for the state being added.
        @param character: The character for the state being added.
        @param state: The state being added.
        @param charset: The character set for the state being added, if any.
        """

        self.states[taxon, character].add(state)
        self.taxa.add(taxon)
        self.characters.add(character)

        if charset:
            self.charset[charset].add(character)

    def __getitem__(self, key: str) -> set[str]:
        return self.states[key]

    # TODO: add total number of values
    def __repr__(self):
        return f"PhyloData with {len(self.taxa)} taxa and {len(self.characters)} characters."


# TODO: collect assumptions?
def binarize(phyd: PhyloData) -> PhyloData:
    """
    Build a binarized version of the provided phylogenetic data.

    @param phyd: The PhyloData to binarize.
    @return: A binarized version of the provided data.
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