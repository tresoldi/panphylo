"""
Module with the class for the internal representation of data.
"""

# Import Python libraries
from collections import defaultdict
import copy
from typing import *
import string

# Import from local modules
from .common import unique_ids


# TODO: add more automatic checks, such as for IUPAC (should be independent from genetic?)
#       should ACTG be a "strict" one with IUPAC as default?
class Character:
    """
    Class for a column definition.
    """

    def __init__(
        self, states: Optional[Set[str]] = None, missing: str = "?", gap: str = "-"
    ):
        """
        Initialize the Character.

        @param states: A sequence of states that the character
            allows, as a set of strings.
        @param missing: A string for representing missing values.
            Defaults to `"?"`.
        @param missing: A string for representing gap values.
            Defaults to `"-"`.
        """

        if not states:
            self._states = set()
        else:
            self._states = states

        self.missing = missing
        self.gap = gap

    @property
    def states(self) -> Tuple[str]:
        """
        Return a comparable version of the states set.

        Note that this will not include unknown states (i.e., missing
        and gap), whose handling will depend on the output function.

        @return: A sorted tuple of the internal states set.
        """

        return tuple(
            sorted(
                [
                    state
                    for state in self._states
                    if state not in [self.missing, self.gap]
                ]
            )
        )

    def add_state(self, state: str):
        """
        Add a state to the character, if applicable.

        Note that this will add missing and gap states to the
        internal list, but they will not be included in
        the `.states` property.

        @param state: The identifier for the state.
        """

        self._states.add(state)

    def is_binary(self) -> bool:
        """
        Checks whether the character is a binary one.

        Binary characters are defined as those that have only "0" and/or
        "1" as potential states.

        @return: A flag on whether the character is a binary one.
        """

        if self.states in [("0",), ("1",), ("0", "1")]:
            return True

        return False

    # TODO: add full iupac support
    def is_genetic(self, iupac: bool = False) -> bool:
        """
        Checks whether the character is a genetic one.

        Genetic characters are defined as those that have only "A", "C",
        "G", and/or "T" as potential states.  If the `iupac` flag is
        set to true, the full IUPAC (IUB) set of nucleic acid code
        (ACGTUMBDH) can be used.

        @param iupac: A flag indicating that the full IUPAC set should
            be used. Defaults to `False`.

        @return: A flag on whether the character is a genetic one.
        """

        if iupac:
            charset = "ACGTUMBDH"
        else:
            charset = "ACGT"

        if all([state.upper() in charset for state in self.states]):
            return True

        return False

    def is_aminoacid(self) -> bool:
        """
        Checks whether the character is an aminoacid one.

        @return: A flag on whether the character is an aminoacid one.
        """

        if all(
            [state.upper() in "ABCDEFGHIJKLMNOPQRSTUVWYZX*" for state in self.states]
        ):
            return True

        return False

    def __len__(self) -> int:
        return len(self.states)

    def __repr__(self) -> str:
        return f"Character with {len(self)} states ({self.states})."


class PhyloData:
    """
    Class for the internal representation of phylogenetic data.
    """

    def __init__(self):
        # The list of taxa is store independently for convenience, as it could be drawn
        # from the list of observations
        self._taxa: Set[str] = set()
        self._charset: Dict[str, Character] = {}

        # Observations are dictionaries with a tuple of strings as keys (taxon, character)
        # and a set of strings as the observed value
        self._obs: Dict[Tuple[str, str], Set[str]] = defaultdict(set)

    @property
    def taxa(self) -> Tuple[str]:
        """
        Return a comparable version of the taxa set.

        @return: A sorted tuple of the internal taxa set.
        """

        return tuple(sorted(self._taxa))

    @property
    def characters(self) -> Tuple[str]:
        """
        Return a comparable version of the character set.

        Note how this is different from the .charset property, which just
        relays the value of the internal private ._charset.

        @return: A sorted tuple of the internal character set.
        """
        return tuple(sorted(list(self._charset)))

    # TODO: confirm that .deepcopy() is not needed
    @property
    def charset(self) -> Dict[str, Character]:
        """
        Return a copy of the internal .charset.

        This property is intended for the exclusive usage of the intenral
        conversion methods.
        """
        return copy.copy(self._charset)

    @property
    def cardinality(self) -> int:
        """
        Return the character cardinality.

        Character cardinality is defined as the number of states in the
        character(s) with the largest number of states.

        @return: An integer with the cardinality of the largest character.
        """

        # Note that we call .states, so that it takes care of special
        # cases like missing data
        return max([len(charvals.states) for charvals in self._charset.values()])

    @property
    def symbols(self) -> Tuple[str]:
        """
        Return a collection of unique symbols for representing generic states.

        The length of the vector will follow the cardinality of the data
        (i.e., `self.cardinality`).

        @return: A list with the characters for representing the states.
        """

        return tuple(
            [ch for ch in string.digits + string.ascii_uppercase][: self.cardinality]
        )

    def __getitem__(self, item: Tuple[str, str]) -> Set[str]:
        """
        Return the observation for a taxon/charset/character tuple.

        @param item: A tuple with taxon and charachter_id, as stored when
            extending the phylogenetic data.
        @return: The set of values associated with the key, with an empty set if nothing was
            stored.
        """

        return self._obs.get(item, set())

    # TODO: have a call (key, character, [charset])
    def extend(self, key: Union[Tuple[str, str], Tuple[str, str, str]], value: str):
        # The key can be either in format (taxon, character) or (taxon, character, charset);
        # if `charset` is not provided (usually in cases of non-binary data) we create a
        # "dummy" one with the same name as the character.
        if len(key) < 2 or len(key) > 3:
            raise ValueError(f"Invalid number of key parameters for extension `{key}`")
        elif len(key) == 2:
            taxon, character, charset = key[0], key[1], key[1]
        else:
            # Decompose the key
            taxon, character, charset = key

        # Extend the list of taxa
        self._taxa.add(taxon)

        # Update internal information
        # TODO: write proper code once update to new system is done
        if charset in self._charset:
            # If the character already exist, just try to extend the list of states; otherwise,
            # build a new character
            self._charset[charset].add_state(value)
        else:
            # If the charset does not exist, create a new one and add the current character
            self._charset[charset] = Character(states={value})

        # Store information on the actual observed state; note that, as we allow multistates, this is
        # actually a set of values
        self._obs[taxon, character].add(value)

    @property
    def matrix(self) -> Tuple[str, str]:
        # Build the matrix representation
        matrix: Dict[str, str] = defaultdict(str)

        is_genetic = all([charinfo.is_genetic() for charinfo in self._charset.values()])
        if is_genetic:
            # TODO: check missing, multiple, etc.
            for char_id, charinfo in sorted(self._charset.items()):
                for taxon in self.taxa:
                    obs = self[taxon, char_id]
                    if not obs:
                        matrix[taxon] += "-"
                    else:
                        # todo: check multiple
                        matrix[taxon] += list(obs)[0]
        else:
            symbols: Tuple[str] = self.symbols  # cache
            for char_id, charinfo in sorted(self._charset.items()):
                states = charinfo.states
                for taxon in self.taxa:
                    obs = self[taxon, char_id]
                    if not obs:
                        matrix[taxon] += "-"
                    else:
                        # TODO: check partial missing data, as in beastling
                        if "?" in obs:
                            matrix[taxon] += "?"
                        else:
                            obs_repr = [symbols[states.index(o)] for o in obs]
                            if len(obs_repr) == 1:
                                matrix[taxon] += obs_repr[0]
                            else:
                                matrix[taxon] += "(%s)" % ",".join(sorted(obs_repr))

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
            (slug_map[taxon], character): value_set
            for (taxon, character), value_set in self._obs.items()
        }


# TODO: collect assumptions?
def binarize(phyd: PhyloData, ascertainment: str) -> PhyloData:
    """
    Build a binarized version of the provided phylogenetic data.

    @param phyd: The PhyloData to binarize.
    @param ascertainment: The type of ascertainment correction to be
        performed.
    @return: A binarized version of the provided data.
    """

    # For each taxon/character, collect the list of observed states in binary
    binary_states = {}
    for character, charinfo in phyd._charset.items():
        states = [state for state in charinfo._states if state != "?"]
        for taxon in phyd.taxa:
            obs = phyd[taxon, character]
            if not obs:
                binary_states[taxon, character] = ["-" for _ in states]
            elif tuple(obs) == ("?",):
                binary_states[taxon, character] = ["?" for _ in states]
            else:
                binary_states[taxon, character] = [
                    "1" if state in obs else "0" for state in states
                ]

    # Build a new phylogenetic data structure, adding the new characters one by one;
    # this also checks whether to perform ascertainment correction
    bin_phyd = PhyloData()
    if ascertainment == "default":
        if all([character.is_genetic() for character in phyd._charset.values()]):
            ascertainment = "false"
        else:
            ascertainment = "true"

    for (taxon, character), states in binary_states.items():
        charstates = [
            state for state in phyd._charset[character]._states if state != "?"
        ]
        for obs, state_label in zip(states, charstates):
            # Add ascertainment
            # TODO: review ascertainment
            if ascertainment == "true":  # TODO: use actual boolean
                bin_phyd.extend((taxon, f"{character}_ASCERTAINMENT"), "0")

            # TODO: confirm if it is right to skip over gaps
            if obs != "-":
                bin_phyd.extend((taxon, f"{character}_{state_label}"), obs)

    return bin_phyd
