# panphylo

[![PyPI](https://img.shields.io/pypi/v/panphylo.svg)](https://pypi.org/project/panphylo)
[![CI](https://github.com/tresoldi/panphylo/actions/workflows/CI.yml/badge.svg)](https://github.com/tresoldi/panphylo/actions/workflows/CI.yml)

`panphylo` is a free and open-source tool for converting and manipulating phylogenetic data, especially for
non-biological datasets.

![Panfilo, from Boccaccio's *Decameron*, as pictured in Bodleian Library MS. Holkham 49, fol. 148r](panfilo_small.png)

There are a wide variety of similar tools for both local and remote execution. panphylo is distinguished by its
focus on phylogenetic data of non-biological origin, especially in the fields of historical linguistics and
stemmatology. The standard data type is the standard with attention to multistate characters and one of the most
supported formats is textual tabular (e.g. CSV), allowing an easier integration with the tools used in these areas.
Likewise, our library offers off-the-shelf support for data manipulation, such as automatic binarization (with
or without addition of ascertainment characters), label adaptation to the restrictions of many programs (for
example, remapping Unicode sequences to ASCII but keeping the uniqueness of the identifiers), removal of constant
features, addition of characters for ascertainment correction, and more.

The library is organized following a structure inspired by the well known [pandoc](https://pandoc.org) tool for converting between textual document formats, that is, in "filters" that convert different formats to an internal representation with multistates. Other "filters" allow you to convert this internal representation into different formats and dialects, carrying out the manipulations requested by the user. Since the same data format can be indicated as input and output, the tool can also be used to tidy up existing files.

The library's name is an homage and reference to "pandoc". It is also a reminder of its origins in the field of stemmatology, referring to Panfilo ("the lover of all"), one of the protagonists of Boccaccio's [Decameron](https://en.wikipedia.org/wiki/The_Decameron). The picture used in this documentatio is taken from a manuscript of the work, the beautiful Bodleian Library MS. Holkham 49 (fol. 148r).

## Installation

In any standard Python environment, `panphylo` can be installed with:

```bash
pip install panphylo
```

## Using `panphylo` 

If no input file is specified, input is read from *stdin*. Output goes to *stdout* by default. For output to a file, use the `-o` option:

```bash
panphylo -o data.nex data.csv
```

The format of the input and output can be specified explicitly using command-line options. The input format can be specified using the `-f`/`--from` option, the output format using the `-t`/`--to` option. Thus, to convert `data.nex` from
NEXUS to PHYLIP, you could type:

```bash
panphylo -f nexus -t phylip data.nex
```

Supported input and output formats are listed below under "Options" (see `-f` for input formats and `-t` for output formats). If the input format is not specified explicitly, `panphylo` will attempt to guess it from the contents of
the file. If the output format is not specified, it will attempt to guess it
from the extension of the filename, defaulting to CSV.

As for character encoding, `panphylo` uses the UTF-8 character encoding for
output, which in most cases will be restricted to ASCII characters. If your
local character encoding is not UTF-8, you should pipe the output through
tools such as `iconv`. The input encoding can be specified with the `-e`
option, and will be autodetected (with the `chardet` library) if not
provided.

The internal representation used by `panphylo` is exclusively multistate,
even when converting from and to binary data, and defaults
to multistate output. To binarize the data (or to "rebinarize" it
allowing to perform the implemented manipulations), the `b` option
can be used.

### Options

| Option                      | Help          |
| --------------------------- | ------------- |
| `--input` FILE              | Read input from *FILE*. If *FILE* is `-`, input will come from *stdin*.  |
| `-o`, `--output` FILE       | Write output to *FILE* instead of *stdout*. If *FILE* is `-`, output will go to *stdout*.   |
| `-b`, `--binarize`          | Binarizes the output. The specification on whether and how to add ascertainment correction is specified by the `--ascertainment` option. |
| `-f`, `--from` FORMAT       | Specify the input format. Valid FORMAT choices are `auto`, `tabular`, `csv`, `tsv`, `nexus`, and `phylip`; `auto` will attempt to autodetect the format from the contents of the file, while `tabular` will attempt to detected the delimiter (comma or tabulation) in tabular textual files. Defaults to `auto`. |
| `-t`, `--to` FORMAT         | Specify the output format. Valid FORMAT choices are `auto`, `csv`, `tsv`, `nexus`, and `phylip`; `auto` will decide on the format based ont he file extension. Defaults to `csv`. |
| `-e`, `--encoding` ENCODING | Specify the character encoding for the input, using the [standard character encoding names](https://docs.python.org/3/library/codecs.html#standard-encodings) in Python. Defaults to autodetection with the `chardet` library. |
| `--i-taxa` LABEL            | Input label, column, or name for taxa. If not provided, the library will attempt to autodetect it. Does not apply to all formats. |
| `--i-char` LABEL            | Input label, column, or name for characters. If not provided, the library will attempt to autodetect it. Does not apply to all formats. |
| `--i-state` LABEL           | Input label, column, or name for states. If not provided, the library will attempt to autodetect it. Does not apply to all formats. |
| `--o-taxa` LABEL            | Output label, column, or name for taxa. If not provided, defaults to `"Taxon"`. Does not apply to all formats. |
| `--o-char` LABEL            | Output label, column, or name for characters. If not provided, defaults to `"Character"`. Does not apply to all formats. |
| `--o-state` LABEL           | Output label, column, or name for states. If not provided, defaults to `"State"`. Does not apply to all formats. |
| `--slug_taxa` LEVEL         | Level of "slugging" (simplification) of taxa names. Valid LEVEL options are `none`, `simple`, and `full`. |
| `--slug_chars` LEVEL        | Level of "slugging" (simplification) of character names. Valid LEVEL options are `none`, `simple`, and `full`. |
| `-v`, `--verbosity` LEVEL   | Set the logging level. Valid LEVEL options, following the Python `logging` library, are `"debug"`, `"info"`, `"warning"`, `"error"`, `"critical"`. |

## Alternatives

As mentioned, there are many tools available for both local and remote
execution that somehow overlap with `panphylo`. They usually support more
formats and provide better support for genetic data, but don't always
offer methods for data manipulation such as binarization and debinarization,
or label conversion. Among the most used tools are:

  - The most used tool, `readseq`, available at a number of online interfaces
    such as [https://mafft.cbrc.jp/alignment/server/cgi-bin/readseq.txt]
    and [http://avermitilis.ls.kitasato-u.ac.jp/readseq.cgi]

  - The EMBOSS `seqret` tool, partly derived from `readseq`, with an
    online interface at [https://www.ebi.ac.uk/Tools/sfc/emboss_seqret/]

  - The web interface at LIRMM [http://phylogeny.lirmm.fr/phylo_cgi/data_converter.cgi]

  - The `phyDat` methods in the `phangorn` R library, at
    [https://rdrr.io/cran/phangorn/man/phyDat.html]

## Changelog

Version 0.2:
  - Add Brython support for running locally in a browser and in the web interface
  - Corrections to output generation, mostly related to multistate data (note that
    it is not recommended to run on multistate data yet)

Version 0.1:
  - First public release

## Community guidelines

While the author can be contacted directly for support, it is recommended that
third parties use GitHub standard features, such as issues and pull requests, to
contribute, report problems, or seek support.

Contributing guidelines, including a code of conduct, can be found in the
`CONTRIBUTING.md` file.

## Author and citation

The library is developed by Tiago Tresoldi (tiago.tresoldi@lingfil.uu.se). The library is developed in the context of
the [Cultural Evolution of Texts](https://github.com/evotext/) project, with funding from the
[Riksbankens Jubileumsfond](https://www.rj.se/) (grant agreement ID:
[MXM19-1087:1](https://www.rj.se/en/anslag/2019/cultural-evolution-of-texts/)).

If you use `panphylo`, please cite it as:

> Tresoldi, T., (2022). panphylo: a tool for converting and manipulating phylogenetic data. Version 0.3. Uppsala: Uppsala Universitet

In BibTeX:

```
@misc{Tresoldi2021panphylo,
  url = {https://github.com/tresoldi/panphylo},
  year = {2022},
  author = {Tiago Tresoldi},
  title = {panphylo: a tool for converting and manipulating phylogenetic data. Version 0.3.},
  address = {Uppsala},
  publisher = {Uppsala Universitet}
}
```
