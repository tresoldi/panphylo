"""
Module with common and reusable functions.
"""

# Import Python libraries
import itertools
import logging
import re
import string
from typing import *

# Import local modules
from unidecode import unidecode


def slug(label: str, level: str) -> str:
    """
    Return a slugged version of a label.

    @param label: The text to be slugged. Note that, as this operates on
        a single string, there is no guarantee of non-collision.
    @param level: Define the level of slugging to be applied. Currently,
        accepted levels are "none", "simple", and "full".
    @return: The slugged version of the label.
    """

    if level not in ["none", "simple", "full"]:
        raise ValueError(f"Unknown level of slugging `{level}`.")

    logging.debug("Slugging label `%s` with level `%s`.", label, level)

    # This implementation of the different levels of slugging seems a
    # bit cumbersome at first, but makes it easy for us to explore alternatives
    if level in ["simple", "full"]:
        label = unidecode(label)
    if level in ["full"]:
        label = label.lower()
    if level in ["simple"]:
        label = "".join(
            [
                char
                for char in label
                if char in string.ascii_letters + string.digits + "-_"
            ]
        )
    if level in ["full"]:
        label = "".join([char for char in label if char in string.ascii_letters])
    if level in ["simple", "full"]:
        label = re.sub(r"\s+", "_", label.strip())

    logging.debug("Label slugged to `%s`.", label)

    return label


def unique_ids(labels: Collection[str], level: str) -> List[str]:
    """
    Map a sequence of identifiers to a slugged version with unique identifiers.

    @param labels: The sequence of labels to be slugged. Note that, by design,
        we accept non-unique labels as input, but they will be unique
        in the output.
    @param level:  Define the level of slugging to be applied. The levels are
        defined by the `slug()` function.
    @return: The list of unique, slugged identifiers. The order follows
        the one in `labels`.
    """

    def _label_iter():
        """
        Custom internal label iterator.

        -> "a", "b", ..., "aa", "ab", ..., "zz", "aaa", "aab", ...
        """
        for length in itertools.count(1):
            for chars in itertools.product(string.ascii_lowercase, repeat=length):
                yield "-" + "".join(chars)

    # Slugify all labels
    slugged = [slug(label, level) for label in labels]

    # Build a corresponding list with the count of previous occurrences of the same value
    loc_counts = [slugged[:idx].count(value) for idx, value in enumerate(slugged)]

    # Build a dictionary of suffixes using the maximum count
    # NOTE: This might look as an overkill, but will allow to easily
    #       adapt other models in the future
    label_iter = _label_iter()
    suffix = {count: next(label_iter) for count in range(max(loc_counts) + 1)}

    # Build the new list, adding the suffix if there is more than one
    # occurrence overall, and return
    unique_slug_labels = [
        f"{label}{suffix[loc_count]}" if slugged.count(label) > 1 else label
        for label, loc_count in zip(slugged, loc_counts)
    ]

    return unique_slug_labels


def indexes2ranges(indexes: Sequence[int]) -> str:
    """
    Transforms a sequence of indexes into a textual range representation.

    This function is used for building NEXUS-like assumption blocks,
    especially for binarized data. Given a list such as `[1, 2, 3, 5, 8, 9]`
    it will return a string representation of the ranges involved, such as
    `"1-3, 5, 8-9"`.

    @param indexes: The sequence of indexes related to a character.
    @return: A textual representation of the range.
    """

    # We need to operate on sorted indexes
    indexes = sorted(indexes)

    # Collect ranges as a list of tuples
    ranges = []
    start, end = None, None
    for idx in indexes:
        if not start:
            start = idx
        elif not end:
            if idx > start + 1:
                ranges.append((start, start))
                start = idx
            else:
                end = idx
        else:
            if idx == end + 1:
                end = idx
            else:
                ranges.append((start, end))
                start, end = idx, None

    # We finish with whatever is in the pile; note that we add `indexes[-1]`
    # and not `end`, dealing with single sites
    ranges.append((start, indexes[-1]))

    # Build output
    ret = ", ".join(
        [
            "%i-%i" % (start, end) if start != end else str(start)
            for (start, end) in ranges
        ]
    )

    return ret
