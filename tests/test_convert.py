"""
Test results of actual conversion.
"""

# Import Python libraries
from pathlib import path

# Import the library for testing
import panphylo

RESOURCE_PATH = Path(__file__).parent / "resources"

def test_convert():
    filename = RESOURCE_PATH / "example.phy"

    
