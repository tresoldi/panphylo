"""
Test methods in the `common` module.
"""

# Import the library for testing
import panphylo


# TODO: add empty, add single, add out of order
def test_indexes2ranges():
    indexes = [1, 2, 3, 5, 8, 9]
    assert panphylo.indexes2ranges(indexes) == "1-3, 5, 8-9"


def test_uniqueids():
    # Unique labels
    assert tuple(panphylo.unique_ids(["a", "'a", "e", "é", "è"], "full")) == ("a-a", "a-b", "e-a", "e-b", "e-c")

    # Non-unique labels
    assert tuple(panphylo.unique_ids(["a", "a", "e", "e", "e"], "full")) == ("a-a", "a-b", "e-a", "e-b", "e-c")