# panphylo

`panphylo` is a free and open-source tool for converting and manipulating phylogenetic data, especially for non-biological datasets.

![Panfilo, from Boccaccio's *Decameron*, as pictured in Bodleian Library MS. Holkham 49, fol. 148r](panfilo_small.png)

There are a wide variety of similar tools for both local and remote execution. panphylo is distinguished by its focus on phylogenetic data of non-biological origin, especially in the fields of historical linguistics and stematology. The standard data type is the standard with attention to multistate characters and one of the most supported formats is textual tabular (e.g. CSV), allowing an easier integration with the tools used in these areas. Likewise, our library offers off-the-shelf support for data manipulation, such as automatic binarization (with or without addition of ascertainment characters), label adaptation to the restrictions of many programs (for example, remapping Unicode sequences to ASCII but keeping the uniqueness of the identifiers), removal of constant features,
addition of characters for ascertainment correction, and more.

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

(lorem ipsum)

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

> Tresoldi, T., (2021). panphylo: a tool for converting and manipulating phylogenetic data. Version 0.1. Uppsala: Uppsala Universitet

In BibTeX:

```
@misc{Tresoldi2021panphylo,
  url = {https://github.com/tresoldi/panphylo},
  year = {2021},
  author = {Tiago Tresoldi},
  title = {panphylo: a tool for converting and manipulating phylogenetic data. Version 0.1.},
  address = {Uppsala},
  publisher = {Uppsala Universitet}
}
```
