---
title: "Panphylo: a tool for converting and manipulating phylogenetic data"
tags:
  - Python
  - phylogenetics
  - file format conversion
  - nexus
  - phylip
authors:
  - name: Tiago Tresoldi
    orcid: 0000-0002-2863-1467
    affiliation: "1, 2" # (Multiple affiliations must be quoted)
affiliations:
 - name: Department of Linguistics and Philology, Uppsala University
   index: 1
date: 01 August 2022
bibliography: paper.bib
---

# Summary

This work presents the [`panphylo`](https://pypi.org/project/panphylo/) package, a command-line tool and
Python library for converting and manipulating phylogenetic data, especially for
non-biological datasets such as those of computational historical linguistics and
stemmatology.
The package is organized in a structure inspired by the well-known [`pandoc`] tool for converting
between textual document formats, that is, in "input filters" which convert different phylogenetic
formats to an internal representation with multistates. Other "filters" allow to convert such
internal representation into different formats and dialects, carrying out manipulations
requested by the user such as automatic binarization (with or without the addition of
ascertainment characters), taxa and character label adaptation to the restrictions of different
software, removal of constant features, and more. Since the same data format can be indicated
as input and output, the package can be used to tidy up existing files.

# Background

The main formats used by phylogenetic software are PHYLIP, NEXUS, and FASTA, each with different
"dialects" depending on the software to be used. Phylogenetic data in non-biological domains,
however, tends to be stored in single tabular or relational formats. It is frequent
for researchers to write ad hoc tools for converting their data, addressing the different
requests of the software they use (such as for taxa names),

The [`panphylo`](https://pypi.org/project/panphylo/) package is

# Statement of need

The package addresses the need for off-the-shelf tools to convert between phylogenetic
data formats [@Bouckaert:2012], 
It is developed so it can be integrated into reproducible pipelines of analysis, 
While the package is not computationally complex or innovative,
with alternatives such as XXX, it compares favorably by providing a
common tool that can address all the minutiae of format conversion.

plethora of user-friendly scripts ; bioinformatics
formats don't tend to be formalized with grammars and examples, and many dialects exist

# Installation, Usage, & Examples

Users can install the package with the standard `pip` tool for managing Python packages. The
package provides a full Python library that can be integrated into other tools, besides
a command-line tool wrapping it.

If no input is specified, data will be read from *stdin*. Output goes to *stdout* by default.

```bash
$ panphylo -o data.nex data.csv
```

The formats for input and output can be specified explicitly using command-line options. The
input format can be specified using the `-f/--from` option, and the output format using the
`-t/--to` option. Thus, to convert a file `data.nex` from NEXUS to PHYLIP, you could type:

```bash
$ panphylo -f nexus -t phylip data.nex
```

If the input format is not specified explicitly, the tool will attempt to detect it from
the file contents (including character encoding and field delimiter in tabular files). If the
output format is not specified, it will be detected from the output file extension.

The internal representation used by panphylo is exclusively multistate, even when converting from
and to binary data, and defaults to multistate output. To binarize the data (or to "rebinarize"
it, allowing to perform the implemented manipulations), the `-b` option can be used.

Full documentation is available online.


# Code and Documentation Availability

The `panphylo` source code is available on GitHub at [https://github.com/tresoldi/panphylo](https://github.com/tresoldi/panphylo).

User documentation is available at [https://panphylo.readthedocs.io/](https://panphylo.readthedocs.io/).

# Acknowledgements

The author has received funding from the Riksbankens Jubileumsfond
(ID: MXM19-1087:1, ["Cultural Evolution of Texts"](https://www.rj.se/en/anslag/2019/cultural-evolution-of-texts/)).

# References
