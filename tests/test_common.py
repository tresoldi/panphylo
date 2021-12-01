"""
Test methods in the `common` module.
"""

# Import the library for testing
import panphylo

# TODO: add empty, add single, add out of order
def test_indexes2ranges():
    indexes = [1, 2, 3, 5, 8, 9]
    assert panphylo.indexes2ranges(indexes) == "1-3, 5, 8-9"
