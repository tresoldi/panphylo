"""
Test results of actual conversion.
"""

# Import Python libraries
from pathlib import Path
import pytest

# Import the library for testing
import panphylo

RESOURCE_PATH = Path(__file__).parent / "test_data"


# TODO: add a better (and shorter) nexus source example
# TODO: build round-trip examples


@pytest.mark.parametrize(
    "input,reference,arg_from,arg_to,binarize",
    [
        # ["example.phy", "example.phy.csv", "phylip", "csv", False],
        # ["example.phy", "example.phy.bin.csv", "phylip", "csv", True],
        # ["example.phy", "example.phy.nex", "phylip", "nexus", False],
        # ["example.phy", "example.phy.bin.nex", "phylip", "nexus", True],
        # ["example.phy", "example.phy.phy", "phylip", "phylip", False],
        # ["example.phy", "example.phy.bin.phy", "phylip", "phylip", True],
        # ["example.csv", "example.csv.phy", "csv", "phylip", False],
        # ["example.csv", "example.csv.bin.phy", "csv", "phylip", True],
        # ["example.csv", "example.csv.nex", "csv", "nexus", False],
        # ["example.csv", "example.csv.bin.nex", "csv", "nexus", True],
        ["example.csv", "example.csv.csv", "csv", "csv", False],
        # ["example.csv", "example.csv.bin.csv", "csv", "csv", True],
        # ["example.nex", "example.nex.csv", "nexus", "csv", False],
        ## The example below fails due to charstatelabel parsing
        # ["example_s.nex", "example_s.nex", "nexus", "csv", True],
        # ["example.nex", "example.nex.phy", "nexus", "phylip", False],
        ## The example below fails due to charstatelabel parsing
        ##["example_s.nex", "example.nex.bin.phy", "nexus", "phylip", True],
        # ["example.nex", "example.nex.nex", "nexus", "nexus", False],
        ## The example below fails due to charstatelabel parsing
        ##["example_s.nex", "example.nex.bin.nex", "nexus", "nexus", True],
    ],
)
def test_convert(
        input: str, reference: str, arg_from: str, arg_to: str, binarize: bool
):
    # Read input and reference
    file_input = RESOURCE_PATH / input
    source = panphylo.fetch_stream_data(file_input)

    file_reference = RESOURCE_PATH / reference
    with open(file_reference, encoding="utf-8") as handler:
        reference = handler.read().strip()

    # Convert and check; we run the same test multiple times, to make
    # sure there is full reproducibility and no issues related to sorting
    args = {"from": arg_from, "to": arg_to, "input": "-", "binarize": binarize}
    for i in range(3):
        converted = panphylo.convert(source, args).strip()
        assert converted == reference

    # converted = panphylo.convert(source, args).strip()
    # if converted != reference:
    #    with open("temp.tiago", "w", encoding="utf-8") as handler:
    #        handler.write(converted)
