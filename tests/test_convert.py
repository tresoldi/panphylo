"""
Test results of actual conversion.
"""

# Import Python libraries
from pathlib import Path

# Import the library for testing
import panphylo

RESOURCE_PATH = Path(__file__).parent / "resources"


def test_convert():
    # Read source
    file_source = RESOURCE_PATH / "example.phy"
    source = panphylo.fetch_stream_data(file_source)

    # Load reference, convert, and check
    file_csv_ref = RESOURCE_PATH / "example.phy.csv"
    args = {"from": "phylip", "to": "csv"}
    with open(file_csv_ref, encoding="utf-8") as handler:
        csv_reference = handler.read().strip()

    csv_converted = panphylo.convert(source, args).strip()
    assert csv_converted == csv_reference

    file_nexus_ref = RESOURCE_PATH / "example.phy.nexus"
    args = {"from": "phylip", "to": "nexus"}
    with open(file_nexus_ref, encoding="utf-8") as handler:
        nexus_reference = handler.read().strip()

    nexus_converted = panphylo.convert(source, args).strip()
    assert nexus_converted == nexus_reference
