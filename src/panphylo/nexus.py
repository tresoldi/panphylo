"""
Module with functions and methods for NEXUS files.

Parsing and writing of NEXUS files is currently done with a very simple,
string manipulation strategy.
"""

# Import Python libraries
import re
from enum import Enum, auto

from panphylo.__main__ import parse_args

# Import from local modules
from .internal import PhyloData


def parse_nexus(source):
    """
    Parse the information in a NEXUS string.

    Parsing is currently done with a manually coded automaton that keeps track of
    state and buffers information until it can be used. It is not as advanced as
    some NEXUS parsing libraries, but this solution requires no additional package
    and can be gradually extended to our needs.
    """

    # Auxiliary state enumeration for the automaton
    class State(Enum):
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
        "charstatelabels": [],
        "matrix": {},
        "charset": [],
    }

    buffer = ""
    block_name = ""
    state = State.NONE
    for idx, char in enumerate(source):
        # Extend buffer first and then process according to automaton state
        buffer += char

        if state == State.NONE:
            # Make sure we have a file that identifies as NEXUS
            if buffer.strip() == "#NEXUS":
                buffer = ""
                state = State.OUT_OF_BLOCK
        elif state == State.OUT_OF_BLOCK:
            # Make sure we have a block
            if char == ";":
                match = re.match(r"BEGIN\s+(.+)\s*;", buffer.upper().strip())
                if match:
                    block_name = match.group(1)
                    buffer = ""
                    state = State.IN_BLOCK
                else:
                    raise ValueError(f"Unable to parse NEXUS block at char {idx}.")
        elif state == State.IN_BLOCK:
            # Read all contents until we hit a semicolon, which will be processed individually
            if char == ";":
                # Check if we are at then of the block, otherwise process
                if re.sub(r"\s", "", buffer.upper().strip()) == "END;":
                    buffer = ""
                    state = State.OUT_OF_BLOCK
                else:
                    # Parse the command inside the block, which can be a single, simple
                    # line or a large subblock (like charstatelabels)
                    command = re.sub("\s+", " ", buffer.strip()).split()[0].upper()
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
                            # TODO: deal with space separated symbols
                            nexus_data["symbols"] = symbols_match.group(1)
                    elif command == "CHARSTATELABELS":
                        # Get each individual charstatelabel and parse it
                        # TODO: use a single parser for binary and multistate?
                        charstate_buffer = re.sub("\s+", " ", buffer.strip())
                        start_idx = charstate_buffer.find(
                            " ", charstate_buffer.find("CHARSTATELABELS")
                        )
                        for charstatelabel in charstate_buffer[start_idx:-1].split(","):
                            charstatelabel = re.sub("\s+", " ", charstatelabel.strip())
                            if "/" in charstatelabel:
                                # TODO: implement
                                raise ValueError("Not implemented")
                            else:
                                idx, charlabel = charstatelabel.split()
                                nexus_data["charstatelabels"].append(
                                    {"idx": idx, "charlabel": charlabel}
                                )
                    elif command == "MATRIX":
                        start_idx = buffer.find("MATRIX") + len("MATRIX")
                        for entry in buffer[start_idx + 1 : -1].strip().split("\n"):
                            entry = re.sub("\s+", " ", entry.strip())
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


def read_data_nexus(source, args):
    # Parse the NEXUS source
    nexus_data = parse_nexus(source)

    # Build internal representation
    # TODO: deal with multistate {}
    # TODO: transform all binary in multistate internal representation
    phyd = PhyloData()
    for taxon, vector in nexus_data["matrix"].items():
        for charstate, value in zip(nexus_data["charstatelabels"], vector):
            # Skip over gaps and make sure we use the default missing symbol
            if value == nexus_data["gap"]:
                continue
            if value == nexus_data["missing"]:
                value = "?"

            phyd.add_value(taxon, charstate["charlabel"], value)

    return phyd
