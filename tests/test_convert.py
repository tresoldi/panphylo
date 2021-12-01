"""
Test results of actual conversion.
"""

# Import Python libraries
from pathlib import Path
import pytest

# Import the library for testing
import panphylo

RESOURCE_PATH = Path(__file__).parent / "resources"


@pytest.mark.parametrize(
    "input,reference,arg_from,arg_to",
    [
        ["example.phy", "example.phy.csv", "phylip", "csv"],
        ["example.phy", "example.phy.nexus", "phylip", "nexus"],
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
    args = {"from": arg_from, "to": arg_to}
    converted = panphylo.convert(source, args).strip()

    assert converted == reference
