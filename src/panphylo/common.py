"""
Module with common and reusable functions.
"""

# Import Python libraries
import re
import string
import unidecode
import itertools

import sys
import contextlib


@contextlib.contextmanager
def smart_open(filename: str, mode: str = "r", *args, **kwargs):
    """
    Open files and i/o streams transparently.

    Code originally from https://stackoverflow.com/a/45735618.
    """

    if filename == "-":
        if "r" in mode:
            stream = sys.stdin
        else:
            stream = sys.stdout
        if "b" in mode:
            fh = stream.buffer
        else:
            fh = stream
        close = False
    else:
        fh = open(filename, mode, *args, **kwargs)
        close = True

    try:
        yield fh
    finally:
        if close:
            try:
                fh.close()
            except AttributeError:
                pass


# TODO: allow more configurations
def slug(label):
    """
    Return a slugged version of a label.
    """

    label = unidecode.unidecode(label)
    label = re.sub("\s+", " ", label.strip())
    label = label.lower()

    label = "".join([char for char in label if char in string.ascii_letters])

    return label


# TODO: add different methods of slug, mapping to slug()
def unique_ids(labels):
    def _label_iter():
        """
        Custom internal label iterator.

        -> "a", "b", ..., "aa", "ab", ..., "zz", "aaa", "aab", ...
        """
        for length in itertools.count(1):
            for chars in itertools.product(string.ascii_lowercase, repeat=length):
                yield "-" + "".join(chars)

    # Slugify all labels
    slugged = [slug(label) for label in labels]

    # Build a corresponding list with the count of previous occurrences
    # of the same value
    loc_counts = [slugged[:idx].count(value) for idx, value in enumerate(slugged)]

    # Build a dictionary of suffixes using the maximum count
    # NOTE: This might look as an overkill, but will allow to easily
    #       adapt other models in the future
    label_iter = _label_iter()
    suffix = {count: next(label_iter) for count in range(max(loc_counts) + 1)}

    # Build the new list, adding the suffix if there is more than one
    # occurrence overall, and return
    # TODO: the overall count could be cached with a collections.Counter
    unique_slug_labels = [
        f"{label}{suffix[loc_count]}" if slugged.count(label) > 1 else label
        for label, loc_count in zip(slugged, loc_counts)
    ]

    return unique_slug_labels
