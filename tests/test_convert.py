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


# TODO: add a better (and shorter) nexus source example
# TODO: build round-trip examples


@pytest.mark.parametrize(
    "input,reference,arg_from,arg_to,binarize",
    [
        # IE sample has a small subset and no multistate (by selection)
        ["ie_sample.csv", "ie_sample_csv.mst.csv", "csv", "csv", False],
        ["ie_sample.csv", "ie_sample_csv.bin.csv", "csv", "csv", True],
        ["ie_sample.csv", "ie_sample_csv.mst.nex", "csv", "nexus", False],
        ["ie_sample.csv", "ie_sample_csv.bin.nex", "csv", "nexus", True],
        ["ie_sample.csv", "ie_sample_csv.mst.phy", "csv", "phylip", False],
        ["ie_sample.csv", "ie_sample_csv.bin.phy", "csv", "phylip", True],

    #    ["ie_sample.nex", "ie_sample_nex.mst.csv", "nexus", "csv", False],
    #    ["ie_sample.nex", "ie_sample_nex.bin.csv", "nexus", "csv", True],
        ["ie_sample.nex", "ie_sample_nex.mst.nex", "nexus", "nexus", False],
    #    ["ie_sample.nex", "ie_sample_nex.bin.nex", "nexus", "nexus", True],
    #    ["ie_sample.nex", "ie_sample_nex.mst.phy", "nexus", "phylip", False],
    #    ["ie_sample.nex", "ie_sample_nex.bin.phy", "nexus", "phylip", True],

    #    ["example.phy", "example.phy.csv", "phylip", "csv", False],
    #    ["example.phy", "example.phy.bin.csv", "phylip", "csv", True],
    #    ["example.phy", "example.phy.nex", "phylip", "nexus", False],
    #    ["example.phy", "example.phy.bin.nex", "phylip", "nexus", True],
    #    ["example.phy", "example.phy.phy", "phylip", "phylip", False],
    #    ["example.phy", "example.phy.bin.phy", "phylip", "phylip", True],
       # ["example.csv", "example.csv.phy", "csv", "phylip", False],
       # ["example.csv", "example.csv.bin.phy", "csv", "phylip", True],
       # ["example.csv", "example.csv.nex", "csv", "nexus", False],
       # ["example.csv", "example.csv.bin.nex", "csv", "nexus", True],
       # ["example.csv", "example.csv.csv", "csv", "csv", False],
       # ["example.csv", "example.csv.bin.csv", "csv", "csv", True],
    #    ["example.nex", "example.nex.csv", "nexus", "csv", False],
    #    ["example.nex", "example.nex.phy", "nexus", "phylip", False],
    #    ["example.nex", "example.nex.nex", "nexus", "nexus", False],

        ## The example below fails due to charstatelabel parsing
        # ["example_s.nex", "example_s.nex", "nexus", "csv", True],
        # ["example_s.nex", "example.nex.bin.phy", "nexus", "phylip", True],
        # ["example_s.nex", "example.nex.bin.nex", "nexus", "nexus", True],
    ],
)
def test_convert(
        input: str, reference: str, arg_from: str, arg_to: str, binarize: bool
):
    # Read input and reference
    file_input = SOURCES_PATH / input
    source = panphylo.fetch_stream_data(file_input)

    file_reference = TARGETS_PATH / reference
    with open(file_reference, encoding="utf-8") as handler:
        reference = handler.read().strip()

    args = {"from": arg_from, "to": arg_to, "input": "-", "binarize": binarize}

    # Temporary file for generating and checking results manually
    converted = panphylo.convert(source, args).strip()
    if converted != reference:
        with open("temp.tiago", "w", encoding="utf-8") as handler:
           handler.write(converted)

    # Convert and check; we run the same test multiple times, to make
    # sure there is full reproducibility and no issues related to sorting
    for i in range(3):
        converted = panphylo.convert(source, args).strip()
        assert converted == reference
