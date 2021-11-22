"""
Module with common and reusable functions.
"""

# Import Python libraries
import re
import string
import unidecode

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
