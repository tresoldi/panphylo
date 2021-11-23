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
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        default="-",
        help="Read input from *FILE*. If *FILE* is `-`, input will come from *stdin*.",
    )
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
        choices=["auto", "csv", "tsv"],
        help="Specify output format.",
    )

    parser.add_argument(
        "--i-taxa",
        type=str,
        help="Input label, column, or name for taxa. Does not apply to all formats.",
    )
    parser.add_argument(
        "--i-char",
        type=str,
        help="Input label, column, or name for characters. Does not apply to all formats.",
    )
    parser.add_argument(
        "--i-vals",
        type=str,
        help="Input label, column, or name for values. Does not apply to all formats.",
    )

    parser.add_argument(
        "--o-taxa",
        type=str,
        help="Output label, column, or name for taxa. Does not apply to all formats.",
    )
    parser.add_argument(
        "--o-char",
        type=str,
        help="Output label, column, or name for characters. Does not apply to all formats.",
    )
    parser.add_argument(
        "--o-vals",
        type=str,
        help="Output label, column, or name for values. Does not apply to all formats.",
    )

    parser.add_argument(
        "-v",
        "--verbosity",
        type=str,
        default="info",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Set the logging level.",
    )

    args = parser.parse_args().__dict__

    # Make sure we don't allow options that cannot be handled
    if args["input"] == "-":
        # TODO: allow autodetection by buffering?
        if args["from"] in ["auto", "tabular"]:
            raise ValueError(
                "Cannot autodetect format from `stdin`; please specify it with `--from`."
            )
        if args["encoding"] == "auto":
            raise ValueError(
                "Cannot autodetect encoding from `stdin`: please specify it with `--encoding`."
            )

    return args


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
