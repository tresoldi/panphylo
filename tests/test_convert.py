"""
Test results of actual conversion.
"""

# Import Python libraries
from pathlib import Path
import pytest

# Import the library for testing
import panphylo

RESOURCE_PATH = Path(__file__).parent / "test_data"

# TODO: add binarization tests
# TODO: add a better (and shorted) nexus source example
# TODO: build round-trip examples
@pytest.mark.parametrize(
    "input,reference,arg_from,arg_to",
    [
        ["example.phy", "example.phy.csv", "phylip", "csv"],
        ["example.phy", "example.phy.nex", "phylip", "nexus"],
        ["example.phy", "example.phy.phy", "phylip", "phylip"],
        ["example.csv", "example.csv.phy", "csv", "phylip"],
        ["example.csv", "example.csv.nex", "csv", "nexus"],
        ["example.csv", "example.csv.csv", "csv", "csv"],
        ["example.nex", "example.nex.csv", "nexus", "csv"],
        #        ["example.nex", "example.nex.phy", "nexus", "phylip"],
        #        ["example.nex", "example.nex.nex", "nexus", "nexus"],
    ],
)
def test_convert(input: str, reference: str, arg_from: str, arg_to: str):
    # Read input and reference
    file_input = RESOURCE_PATH / input
    source = panphylo.fetch_stream_data(file_input)

    file_reference = RESOURCE_PATH / reference
    with open(file_reference, encoding="utf-8") as handler:
        reference = handler.read().strip()

    # Convert and check
    args = {"from": arg_from, "to": arg_to, "input": "-"}
    converted = panphylo.convert(source, args).strip()

    assert converted == reference
