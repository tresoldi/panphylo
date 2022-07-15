"""
Test methods in the `tabular` module.
"""

# Import the library for testing
import panphylo


def test_comma_detect_delimiter():
    source = """
COL1,COL2,COL3
a,b,c
d,e,f
    """
    assert panphylo.detect_delimiter(source) == ","


def test_tab_detect_delimiter():
    source = "COL1\tCOL2\tCOL3\n"
    source += "a\tb\tc\n"
    source += "d\te\tf\n"
    assert panphylo.detect_delimiter(source) == "\t"
