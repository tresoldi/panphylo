"""
Module with common and reusable functions.
"""

# Import Python libraries
import re
import string
import unidecode

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
            fh = stream.buffer  # type: IO
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
