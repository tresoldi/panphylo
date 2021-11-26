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

# TODO: default output format to CSV, when stdout?
# TODO: add the ascertainment option

# TODO: remember to sync with README
def parse_args():
    """
    Parse command-line arguments and return them as a dictionary.
    """

    parser = argparse.ArgumentParser(description="Convert and manipulate phylodata.")
    parser.add_argument(
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
        "-b",
        "--binarize",
        action="store_true",
        help="Binarizes the output. The specification on whether and how to add ascertainment correction is specified by the `--ascertainment` option.",
    )

    parser.add_argument(
        "-f",
        "--from",
        type=str,
        default="auto",
        choices=["auto", "tabular", "csv", "tsv", "nexus", "phylip"],
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
        choices=["auto", "csv", "tsv", "nexus", "phylip"],
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
        "--i-state",
        type=str,
        help="Input label, column, or name for states. Does not apply to all formats.",
    )

    parser.add_argument(
        "--o-taxa",
        type=str,
        default="Taxon",
        help="Output label, column, or name for taxa. Does not apply to all formats.",
    )
    parser.add_argument(
        "--o-char",
        type=str,
        default="Character",
        help="Output label, column, or name for characters. Does not apply to all formats.",
    )
    parser.add_argument(
        "--o-state",
        type=str,
        default="State",
        help="Output label, column, or name for states. Does not apply to all formats.",
    )

    parser.add_argument(
        "--slug_taxa",
        type=str,
        default="simple",
        choices=["none", "simple", "full"],
        help="Level of slugging for taxa names.",
    )
    parser.add_argument(
        "--slug_chars",
        type=str,
        default="simple",
        choices=["none", "simple", "full"],
        help="Level of slugging for character names.",
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

    # Decide on the right output function based on the output format or, if not
    # provided, on the extension
    if args["to"] == "auto":
        if not "." in args["to"]:
            raise ValueError(
                "Unable to detect output format; please specify it with `--to`."
            )

        extension = args["to"].split(".")[-1]
        if extension == "csv":
            args["to"] = "csv"
        elif extension == "tsv":
            args["to"] = "tsv"
        elif extension in ["nex", "nexus"]:
            args["to"] = "nexus"
        elif extension in ["phy", "phylip"]:
            args["to"] = "phylip"
        else:
            raise ValueError(
                "Unable to detect output format; please specify it with `--to`."
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

    # Read source data and detect the format if necessary
    source = panphylo.fetch_stream_data(args["input"], args["encoding"])
    if args["from"] == "auto":
        if source.strip().startswith("#NEXUS"):
            args["from"] = "nexus"
        elif re.search("$\s*\d+\s*\d+", source):
            args["from"] = "phylip"
        else:
            args["from"] = "tabular"

    # Convert to a string
    converted = panphylo.convert(source, args)

    # Write to the stream
    with panphylo.smart_open(args["output"], "w", encoding="utf-8") as handler:
        handler.write(converted.strip())
        handler.write("\n")


if __name__ == "__main__":
    main()
