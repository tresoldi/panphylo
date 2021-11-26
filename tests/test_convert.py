"""
Test results of actual conversion.
"""

# Import Python libraries
from pathlib import Path

# Import the library for testing
import panphylo

RESOURCE_PATH = Path(__file__).parent / "resources"


def test_convert():
    file_source = RESOURCE_PATH / "example.phy"
    file_ref = RESOURCE_PATH / "reference01.csv"
    args = {"from": "phylip", "to": "csv"}

    # Convert
    source = panphylo.fetch_stream_data(file_source)
    converted = panphylo.convert(source, args).strip()

    # Load reference
    with open(file_ref, encoding="utf-8") as handler:
        reference = handler.read().strip()

    # Compare
    assert converted == reference
