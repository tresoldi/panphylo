#!/usr/bin/env python3

"""
__main__.py

Module for command-line execution of `panphylo`.
"""

# Import Python standard libraries
import argparse
import logging

# Import our library
import panphylo

# TODO: allow reading from stdin


def parse_args():
    """
    Parse command-line arguments and return them as a dictionary.
    """

    parser = argparse.ArgumentParser(description="Convert and manipulate phylodata.")
    parser.add_argument("input", type=str, help="Read input from *FILE*.")
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="-",
        help="Write output to *FILE* instead of *stdout*. If *FILE* is `-`, output will go to *stdout* even if a non-textual format is specified.",
    )

    parser.add_argument(
        "-f",
        "--from",
        type=str,
        default="auto",
        choices=["auto", "tabular", "csv", "tsv"],
        help="Specify input format.",
    )
    parser.add_argument(
        "-e",
        "--encoding",
        type=str,
        default="auto",
        help="Character encoding for the input (use `auto` to detect).",
    )
    parser.add_argument(
        "-t",
        "--to",
        type=str,
        default="auto",
        choices=["auto", "tabular", "csv", "tsv"],
        help="Specify output format.",
    )

    parser.add_argument("--l-taxa", type=str, help="Label, column, or name for taxa.")
    parser.add_argument(
        "--l-char", type=str, help="Label, column, or name for characters."
    )
    parser.add_argument(
        "--l-vals", type=str, help="Label, column, or name for values."
    )

    parser.add_argument(
        "-v",
        "--verbosity",
        type=str,
        default="info",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Set the logging level.",
    )

    args = parser.parse_args()

    return args.__dict__


def main():
    """
    Script entry point.
    """

    # Parse command line arguments and set the logger
    args = parse_args()

    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    logging.basicConfig(level=level_map[args["verbosity"]])

    # Read input
    panphylo.read_input(args)


if __name__ == "__main__":
    main()
