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
        Add a state to the character, if applicable.

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

    def matrix(self) -> tuple[str, str]:
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

        # Build the representation and return; we don't sort here, as different slug
        # levels might be applied by the output functions
        return tuple(matrix.items())

    def slug_taxa(self, level: str):
        """
        Slug taxa labels, making sure uniqueness of IDs is preserved.

        The method also takes care of updating all references and observations.

        @param level: The level of slugging, as accepted by the `slug()` function.
        """

        # Build map with unique ids, update self.taxa, and update self.values
        slug_map = {
            source: target
            for source, target in zip(self._taxa, unique_ids(self._taxa, level))
        }

        self._taxa = set(slug_map.values())
        self._obs = {
            (slug_map[taxon], charset, character): value_set for
            (taxon, charset, character), value_set in self._obs.items()
        }

# TODO: collect assumptions?
# def binarize(phyd: PhyloData) -> PhyloData:
#    """
#    Build a binarized version of the provided phylogenetic data.
#
#    @param phyd: The PhyloData to binarize.
#    @return: A binarized version of the provided data.
#    """
#
#    # For each taxon, collect a map of which charstates are observed; this does not modify the
#    # internal properties
#    charstates = phyd.charstates  # cache
#    binary_states = {}
#    for taxon in phyd.taxa:
#        for character, states in charstates.items():
#            obs = phyd.states.get((taxon, character), None)
#
#            if not obs:
#                binary_states[taxon, character] = [BinaryObs.GAP for _ in states]
#            else:
#                if tuple(obs) == ("?",):
#                    binary_states[taxon, character] = [
#                        BinaryObs.MISSING for _ in states
#                    ]
#                else:
#                    binary_states[taxon, character] = [
#                        BinaryObs.TRUE if state in obs else BinaryObs.FALSE
#                        for state in states
#                   ]
#
#    # Build a new phylogenetic data structure, adding the new characters one by one
#    bin_phyd = PhyloData()
#    for (taxon, character), states in binary_states.items():
#        for obs, state_label in zip(states, charstates[character]):
#            # Add ascertainment
#            bin_phyd.add_state(
#                taxon, f"{character}_ASCERTAINMENT", "0", charset=character
#            )
#
#            # TODO: confirm if it is right to skip over gaps
#            if obs != BinaryObs.GAP:
#                bin_phyd.add_state(
#                    taxon,
#                    f"{character}_{state_label}",
#                    BINARY_OPS_MAP[obs],
#                    charset=character,
#                )
#
#    return bin_phyd
