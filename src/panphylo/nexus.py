"""
Module with functions and methods for NEXUS files.

Parsing and writing of NEXUS files is currently done with a simple
string manipulation strategy. The usage of actual parsers, or libraries
with that purpose, would make transpilation too hard.
"""

# TODO: allow to output taxa and character names between quotes, if necessary
# TODO: sort using assumptions (charset) if provided
# TODO: support comments (will need changes to the parser)

# Import Python standard libraries
import re
from collections import defaultdict
from enum import Enum, auto

# Import from local modules
from .common import indexes2ranges
from .phylodata import PhyloData


def parse_nexus(source: str) -> dict:
    """
    Parse the information in a NEXUS string.

    Parsing is currently done with a manually coded automaton that keeps track of
    state and buffers information until it can be used. It is not as advanced as
    some NEXUS parsing libraries, but this solution requires no additional package
    and can be gradually extended to our needs.

    :param source: The full NEXUS source code.
    :return: A dictionary with all the block information in the source.
    """

    # Auxiliary state enumeration for the automaton
    class ParserState(Enum):
        NONE = auto()
        OUT_OF_BLOCK = auto()
        IN_BLOCK = auto()

    # Data that will be filled during parsing; in the future, this could be expanded
    # to an actual class, with sanity checks etc.
    nexus_data = {
        "ntax": None,
        "nchar": None,
        "datatype": None,
        "missing": None,
        "gap": None,
        "symbols": None,
        "charstate_labels": {},
        "charstate_states": {},
        "matrix": {},
        "charset": [],
    }

    # TODO: keep track of line numbers by counting newline chars, using them in debug
    buffer = ""
    block_name = ""
    parser_state = ParserState.NONE
    for idx, char in enumerate(source):
        # Extend buffer first and then process according to automaton state
        buffer += char

        if parser_state == ParserState.NONE:
            # Make sure we have a file that identifies as NEXUS
            if buffer.strip() == "#NEXUS":
                buffer = ""
                parser_state = ParserState.OUT_OF_BLOCK
        elif parser_state == ParserState.OUT_OF_BLOCK:
            # Make sure we have a block
            if char == ";":
                match = re.match(r"BEGIN\s+(.+)\s*;", buffer.upper().strip())
                if match:
                    block_name = match.group(1)
                    buffer = ""
                    parser_state = ParserState.IN_BLOCK
                else:
                    raise ValueError(f"Unable to parse NEXUS block at char {idx}.")
        elif parser_state == ParserState.IN_BLOCK:
            # Read all contents until we hit a semicolon, which will be processed individually
            if char == ";":
                # Check if we are at then of the block, otherwise process
                if re.sub(r"\s", "", buffer.upper().strip()) == "END;":
                    buffer = ""
                    parser_state = ParserState.OUT_OF_BLOCK
                else:
                    # Parse the command inside the block, which can be a single, simple
                    # line or a large subblock (like charstatelabels)
                    command = re.sub(r"\s+", " ", buffer.strip()).split()[0].upper()
                    if command == "DIMENSIONS":
                        ntax_match = re.search(r"NTAX\s*=\s*(\d+)", buffer.upper())
                        nchar_match = re.search(r"NCHAR\s*=\s*(\d+)", buffer.upper())
                        if ntax_match:
                            nexus_data["ntax"] = int(ntax_match.group(1))
                        if nchar_match:
                            nexus_data["nchar"] = int(nchar_match.group(1))
                    elif command == "FORMAT":
                        datatype_match = re.search(
                            r"DATATYPE\s*=\s*(\w+)", buffer.upper()
                        )
                        missing_match = re.search(r"MISSING\s*=\s*(.)", buffer.upper())
                        gap_match = re.search(r"GAP\s*=\s*(.)", buffer.upper())
                        symbols_match = re.search(
                            r"SYMBOLS\s*=\s*\"([^\"]+)\"", buffer.upper()
                        )
                        if datatype_match:
                            nexus_data["datatype"] = datatype_match.group(1)
                        if missing_match:
                            nexus_data["missing"] = missing_match.group(1)
                        if gap_match:
                            nexus_data["gap"] = gap_match.group(1)
                        if symbols_match:
                            # We need to deal with space separated symbols
                            nexus_data["symbols"] = symbols_match.group(1).replace(
                                " ", ""
                            )
                    elif command == "CHARSTATELABELS":
                        # Get each individual charstatelabel and parse it
                        # TODO: use a single parser for binary and multistate?
                        charstate_buffer = re.sub(r"\s+", " ", buffer.strip())
                        start_idx = charstate_buffer.find(
                            " ", charstate_buffer.find("CHARSTATELABELS")
                        )
                        for charstatelabel in charstate_buffer[start_idx:-1].split(","):
                            charstatelabel = re.sub(r"\s+", " ", charstatelabel.strip())
                            if not charstatelabel:
                                continue
                            if "/" in charstatelabel:
                                match = re.search(
                                    r"(\d+)\s+(\S+)\s*/(.+)", charstatelabel
                                )
                                idx = match.group(1)
                                charlabel = match.group(2)
                                states = match.group(3).split()

                                nexus_data["charstate_labels"][int(idx)] = charlabel
                                nexus_data["charstate_states"][charlabel] = states
                            else:
                                idx, charlabel = charstatelabel.split()
                                nexus_data["charstate_labels"][int(idx)] = charlabel
                    elif command == "MATRIX":
                        start_idx = buffer.find("MATRIX") + len("MATRIX")
                        for entry in buffer[start_idx + 1 : -1].strip().split("\n"):
                            entry = re.sub(r"\s+", " ", entry.strip())
                            taxon, vector = entry.split()
                            nexus_data["matrix"][taxon] = vector
                    elif command == "CHARSET":
                        # TODO: implement other syntaxes
                        # TODO: make sure it is performed only under the "assumption" block
                        match = re.search(
                            r"charset\s*(\w+)\s*=\s*(\d+)\s*-\s*(\d+)", buffer
                        )
                        if match:
                            charset_label, start, end = match.groups()
                            nexus_data["charset"].append(
                                {
                                    "charset": charset_label,
                                    "start": int(start),
                                    "end": int(end),
                                }
                            )

                    # Clean the buffer and continue
                    buffer = ""

    return nexus_data


def read_data_nexus(source: str, args) -> PhyloData:
    """
    Parse a NEXUS source into an internal representation.

    :param source: A string with the source data representation.
    :param args:
    :return: An object with the internal representation of the data.
    """

    # Parse the NEXUS source
    nexus_data = parse_nexus(source)

    # Build internal representation
    # TODO: deal with multistate {}
    # TODO: transform all binary in multistate internal representation
    # TODO: this is currently handling only binary and needs charsets

    # Build inverse map from position in the alignment to the charset,
    # collecting states; if no charset is provided, each character
    # will be its own charset
    states = defaultdict(set)
    if nexus_data["charset"]:
        alm2charset = {}
        for charset in nexus_data["charset"]:
            for idx in range(charset["start"], charset["end"] + 1):
                alm2charset[idx] = charset["charset"]

        for taxon, vector in nexus_data["matrix"].items():
            for idx, state in enumerate(vector):
                if state == nexus_data["missing"]:
                    states[taxon, alm2charset[idx + 1]].add("?")
                elif state == nexus_data["gap"]:
                    pass
                elif state != "0":  # TODO: why this? still needed? only for binary?
                    states[taxon, alm2charset[idx + 1]].add(
                        nexus_data["charstate_labels"][idx + 1]
                    )
    else:
        for taxon, vector in nexus_data["matrix"].items():
            for character, state in zip(nexus_data["charstate_states"], vector):
                if state == nexus_data["missing"]:
                    states[taxon, character].add("?")
                elif state == nexus_data["gap"]:
                    pass
                else:
                    states[taxon, character].add(state)

    # Build the PhyloData object and return
    # TODO: deal with charstates when available
    phyd = PhyloData()
    for (taxon, character), state_set in states.items():
        for state in state_set:
            phyd.extend((taxon, character), state)

    return phyd


def build_taxa_block(phyd: PhyloData) -> str:
    """
    Build a NEXUS TAXA block.

    :param phyd: The PhyloData object used as source of the taxa block.
    :return: A textual representation of the NEXUS taxa block.
    """

    buffer = """
BEGIN TAXA;
    DIMENSIONS NTAX=%i;
    TAXLABELS
%s
    ;
END;""" % (
        len(phyd.taxa),
        "\n".join(["        %s" % taxon for taxon in sorted(phyd.taxa)]),
    )

    return buffer.strip()


def build_character_block(phyd: PhyloData) -> str:
    """
    Build a NEXUS CHARACTER block.

    :param phyd: The PhyloData object used as source of the character block.
    :return: A textual representation of the NEXUS character block.
    """

    # Express the actual labels only we have any state which is not a binary "0" or "1"
    # TODO: what about mixed, binary and non-binary, data?
    # TODO: should carry the original state names, if available

    is_genetic = all([charinfo.is_genetic() for charinfo in phyd.charset.values()])
    if is_genetic:
        is_binary = False
        symbols = "ACGT"  # TODO: iupac support
    else:
        is_binary = True
        symbols = "".join(phyd.symbols)
        for charinfo in phyd.charset.values():
            if charinfo.states not in [("0",), ("1",), ("0", "1")]:
                is_binary = False
                break

    charstatelabels = []
    for character, charinfo in sorted(phyd.charset.items()):
        if is_genetic or is_binary:
            charstatelabels.append(character)
        else:
            states_str = ["%s_%s" % (character, state) for state in charinfo.states]
            charstatelabels.append("%s /%s" % (character, " ".join(states_str)))

    charstatelabels_str = ",\n".join(
        [
            "        %i %s" % (idx + 1, label)
            for idx, label in enumerate(charstatelabels)
        ]
    )

    buffer = """
BEGIN CHARACTERS;
    DIMENSIONS NCHAR=%i;
    FORMAT DATATYPE=STANDARD MISSING=? GAP=- SYMBOLS="%s";
    CHARSTATELABELS
%s
    ;

%s

END;""" % (
        len(charstatelabels),
        symbols,
        charstatelabels_str,
        build_matrix_command(phyd),
    )

    return buffer.strip()


def build_matrix_command(phyd: PhyloData) -> str:
    """
    Build a NEXUS MATRIX command.

    :param phyd: The PhyloData object used as source of the matrix command.
    :return: A textual representation of the NEXUS matrix command.
    """

    # Obtain the matrix and the maximum taxon length for formatting
    matrix = phyd.matrix
    taxon_length = max([len(entry[0]) for entry in matrix])

    # Build buffer
    buffer = """
MATRIX
%s
;""" % (
        "\n".join(
            [
                "%s    %s" % (taxon.ljust(taxon_length), vector)
                for (taxon, vector) in matrix
            ]
        )
    )

    return buffer.strip()


# TODO: incorporate to the processing from other parts (e.g. BEGIN DATA)
# TODO: this is probably failing right now with jumps, when indexes2ranges is needed
def build_assumption_block(phyd: PhyloData) -> str:
    """
    Build a NEXUS ASSUMPTION block.

    :param phyd: The PhyloData object used as source of the assumption block.
    :return: A textual representation of the NEXUS assumption block.
    """

    # TODO: geting the list of characters with a workaround for genetic data...
    chars = []
    for char in phyd.characters:
        if char.startswith("CHAR_"):
            tokens = char.split("_")
            chars.append("_".join(tokens[:-1]))
        else:
            chars.append(char.split("_")[0])

    indexes = defaultdict(list)
    for idx, label in enumerate(chars):
        indexes[label].append(idx + 1)

    buffer = """
BEGIN ASSUMPTIONS;
%s
END;
    """ % (
        "\n".join(
            [
                "    CHARSET %s = %s;" % (charset, indexes2ranges(indexes[charset]))
                for charset in sorted(indexes)
            ]
        )
    )

    return buffer


def build_nexus(phyd: PhyloData, args) -> str:
    """
    Build a NEXUS data representation.

    :param phyd: The PhyloData object used as source of the data representation.
    :param args:
    :return: A textual representation of the NEXUS data representation.
    """

    # TODO: not rendering polymorphy

    components = [
        "#NEXUS",
        build_taxa_block(phyd),
        build_character_block(phyd),
    ]

    # Assumption are only there if the data is binary
    is_binary = [c.is_binary() for c in phyd.charset.values()]
    if all(is_binary):
        components.append(build_assumption_block(phyd))

    buffer = "\n\n".join([comp for comp in components if comp])

    return buffer
