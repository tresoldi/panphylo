"""
Test results of actual conversion.
"""

# Import Python libraries
from pathlib import Path

import pytest

# Import the library for testing
import panphylo

SOURCES_PATH = Path(__file__).parent / "sources"
TARGETS_PATH = Path(__file__).parent / "targets"

# Write unexpected results to disk
WRITE_DEBUG = True

# TODO: build round-trip examples


# Tests are parametrized for each test source file, making it easier to experiment
# with different input and output options


def _write_debug(converted: str, reference: str, filename: Path):
    """
    Write a debug file with the actual test output.

    This auxiliary function makes it easier to compare expected and computed
    output, and can be shared across all tests conversion tests.

    Note that unexpected results are only written if the global WRITE_DEBUG
    flag is set to `True`.

    @param converted: The output of the conversion test.
    @param reference: The expected output of the conversion test.
    @param filename: The file holding the expected output.
    """

    if WRITE_DEBUG:
        if converted != reference:
            with open(str(filename) + ".debug", "w", encoding="utf-8") as handler:
                handler.write(converted)


# Test "ie_sample.csv", a sample with a small subset of IELEX and no multistate (by selection)
@pytest.mark.parametrize(
    "reference_file,arg_to,binarize",
    [
        ["ie_sample_csv.mst.csv", "csv", False],
        ["ie_sample_csv.bin.csv", "csv", True],
        ["ie_sample_csv.mst.nex", "nexus", False],
        ["ie_sample_csv.bin.nex", "nexus", True],
        ["ie_sample_csv.mst.phy", "phylip", False],
        ["ie_sample_csv.bin.phy", "phylip", True],
    ],
)
def test_convert_ie_sample_csv(reference_file: str, arg_to: str, binarize: bool):
    # Read input and reference
    source = panphylo.fetch_stream_data(str(SOURCES_PATH / "ie_sample.csv"))
    with open(TARGETS_PATH / reference_file, encoding="utf-8") as handler:
        reference = handler.read().strip()

    # Build arguments, convert and assert, writing debug output if so requested
    args = {
        "from": "csv",
        "to": arg_to,
        "input": "-",
        "binarize": binarize,
        "ascertainment": "default",
    }
    converted = panphylo.convert(source, args).strip()

    _write_debug(converted, reference, TARGETS_PATH / reference_file)
    assert converted == reference


# Test "ie_sample.nex", a sample with a small subset of IELEX and no multistate (by selection)
@pytest.mark.parametrize(
    "reference_file,arg_to,binarize",
    [
        ["ie_sample_nex.mst.csv", "csv", False],
        ["ie_sample_nex.bin.csv", "csv", True],
        ["ie_sample_nex.mst.nex", "nexus", False],
        ["ie_sample_nex.bin.nex", "nexus", True],
        ["ie_sample_nex.mst.phy", "phylip", False],
        ["ie_sample_nex.bin.phy", "phylip", True],
    ],
)
def test_convert_ie_sample_nex(reference_file: str, arg_to: str, binarize: bool):
    # Read input and reference
    source = panphylo.fetch_stream_data(str(SOURCES_PATH / "ie_sample.nex"))
    with open(TARGETS_PATH / reference_file, encoding="utf-8") as handler:
        reference = handler.read().strip()

    # Build arguments, convert and assert, writing debug output if so requested
    args = {
        "from": "nexus",
        "to": arg_to,
        "input": "-",
        "binarize": binarize,
        "ascertainment": "default",
    }
    converted = panphylo.convert(source, args).strip()

    _write_debug(converted, reference, TARGETS_PATH / reference_file)
    assert converted == reference


# Test "cpacific.nex", from Greenhill & Hoffmann 2019
@pytest.mark.parametrize(
    "reference_file,arg_to,binarize",
    [
        ["cpacific_nex.mst.csv", "csv", False],
        ["cpacific_nex.bin.csv", "csv", True],
        ["cpacific_nex.mst.nex", "nexus", False],
        ["cpacific_nex.bin.nex", "nexus", True],
        ["cpacific_nex.mst.phy", "phylip", False],
        ["cpacific_nex.bin.phy", "phylip", True],
    ],
)
def test_convert_cpacific_nex(reference_file: str, arg_to: str, binarize: bool):
    # Read input and reference
    source = panphylo.fetch_stream_data(str(SOURCES_PATH / "cpacific.nex"))
    with open(TARGETS_PATH / reference_file, encoding="utf-8") as handler:
        reference = handler.read().strip()

    # Build arguments, convert and assert, writing debug output if so requested
    args = {
        "from": "nexus",
        "to": arg_to,
        "input": "-",
        "binarize": binarize,
        "ascertainment": "default",
    }
    converted = panphylo.convert(source, args).strip()

    _write_debug(converted, reference, TARGETS_PATH / reference_file)
    assert converted == reference


# Test "genetic.phy", with hand-build genetic data
@pytest.mark.parametrize(
    "reference_file,arg_to,binarize",
    [
        ["genetic_phy.mst.csv", "csv", False],
        ["genetic_phy.bin.csv", "csv", True],
        ["genetic_phy.mst.nex", "nexus", False],
        ["genetic_phy.bin.nex", "nexus", True],
        ["genetic_phy.mst.phy", "phylip", False],
        ["genetic_phy.bin.phy", "phylip", True],
    ],
)
def test_convert_genetic_phy(reference_file: str, arg_to: str, binarize: bool):
    # Read input and reference
    source = panphylo.fetch_stream_data(str(SOURCES_PATH / "genetic.phy"))
    with open(TARGETS_PATH / reference_file, encoding="utf-8") as handler:
        reference = handler.read().strip()

    # Build arguments, convert and assert, writing debug output if so requested
    args = {
        "from": "phylip",
        "to": arg_to,
        "input": "-",
        "binarize": binarize,
        "ascertainment": "default",
    }
    converted = panphylo.convert(source, args).strip()

    _write_debug(converted, reference, TARGETS_PATH / reference_file)
    assert converted == reference
