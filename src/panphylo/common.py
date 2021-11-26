"""
Module with common and reusable functions.
"""

# Import Python libraries
import re
import string
import unidecode
import itertools
import logging
import chardet

import sys
import contextlib

# TODO: for slug, consider that The following symbols/caracters are not allowed in taxa names to ensure Newick
#       compatibility: (space), (semicolon), (colon), (comma), (parentheses), (single quote)


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


def fetch_stream_data(input, encoding="auto") -> str:
    """
    Read the input data as a string.

    The function takes care of handling input from both stdin and
    files, decoding the stream of bytes according to the user-specified
    character encoding (including automatic detection if necessary).

    :param args: The arguments carrying all options, either converted
        from command-line arguments, built from an interface, or
        as a dictionary.
    :return: A string with the full source for the data, encoded
        according to the specified charset encoding.
    """

    # Fetch all input as a sequence of bytes, so that we don't consume stdout
    # and can still run autodetection on format and encoding
    with smart_open(input, "rb") as handler:
        logging.debug("Reading contents from `%s`.", input)
        raw_source = handler.read()

        # Detect encoding if necessary, building a string
        if encoding != "auto":
            logging.debug("Using `%s` character encoding.", encoding)
        else:
            detect = chardet.detect(raw_source)
            encoding = detect["encoding"]
            logging.debug(
                "Encoding detected as `%s` (confidence: %.2f)",
                detect["encoding"],
                detect["confidence"],
            )

        source = raw_source.decode(encoding)

    return source


# TODO: allow more configurations
# TODO: document levels
def slug(label, level):
    """
    Return a slugged version of a label.
    """

    if level == "none":
        pass
    elif level == "simple":
        label = unidecode.unidecode(label)
        label = re.sub("\s+", "_", label.strip())
        label = "".join(
            [
                char
                for char in label
                if char in string.ascii_letters + string.digits + "-_"
            ]
        )
    elif level == "full":
        label = unidecode.unidecode(label)
        label = re.sub("\s+", " ", label.strip())
        label = label.lower()
        label = "".join([char for char in label if char in string.ascii_letters])

    return label


# TODO: add different methods of slug, mapping to slug()
def unique_ids(labels, level):
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


def indexes2ranges(indexes, string=True):
    """
    Transforms a list of indexes into a range representation.

    This function is used for building NEXUS-like assumption blocks,
    especially for binarized data. Given a list such as `[1, 2, 3, 5, 8, 9]`
    it will return either a structural or a string representation of
    the ranges involved, such as `"1-3, 5, 8-9"`.
    """

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
    if not string:
        ret = tuple(ranges)
    else:
        ret = ", ".join(
            [
                "%i-%i" % (start, end) if start != end else str(start)
                for (start, end) in ranges
            ]
        )

    return ret
