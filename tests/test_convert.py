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
        ["ie_sample.nex", "ie_sample_nex.mst.csv", "nexus", "csv", False],
        ["ie_sample.nex", "ie_sample_nex.bin.csv", "nexus", "csv", True],
        ["ie_sample.nex", "ie_sample_nex.mst.nex", "nexus", "nexus", False],
        ["ie_sample.nex", "ie_sample_nex.bin.nex", "nexus", "nexus", True],
        ["ie_sample.nex", "ie_sample_nex.mst.phy", "nexus", "phylip", False],
        ["ie_sample.nex", "ie_sample_nex.bin.phy", "nexus", "phylip", True],
        # Central pacific, from Greenhill & Hoffmann 2019
        ["cpacific.nex", "cpacific_nex.mst.csv", "nexus", "csv", False],
        ["cpacific.nex", "cpacific_nex.bin.csv", "nexus", "csv", True],
        ["cpacific.nex", "cpacific_nex.mst.nex", "nexus", "nexus", False],
        ["cpacific.nex", "cpacific_nex.bin.nex", "nexus", "nexus", True],
        ["cpacific.nex", "cpacific_nex.mst.phy", "nexus", "phylip", False],
        ["cpacific.nex", "cpacific_nex.bin.phy", "nexus", "phylip", True],
        # Hand-picked example with genetic data
        ["genetic.phy", "genetic_phy.mst.csv", "phylip", "csv", False],
        ["genetic.phy", "genetic_phy.bin.csv", "phylip", "csv", True],
        ["genetic.phy", "genetic_phy.mst.nex", "phylip", "nexus", False],
        ["genetic.phy", "genetic_phy.bin.nex", "phylip", "nexus", True],
        ["genetic.phy", "genetic_phy.mst.phy", "phylip", "phylip", False],
        ["genetic.phy", "genetic_phy.bin.phy", "phylip", "phylip", True],
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
        reference_source = handler.read().strip()

    args = {
        "from": arg_from,
        "to": arg_to,
        "input": "-",
        "binarize": binarize,
        "ascertainment": "default",
    }

    # Convert and check
    converted = panphylo.convert(source, args).strip()
    if converted != reference_source:
        with open(f"{reference}.tiago", "w", encoding="utf-8") as handler:
            handler.write(converted)
    assert converted == reference_source
