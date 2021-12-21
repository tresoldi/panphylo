# Imports from the standard library
import algorithm
import sequtils
import sets
import std/enumerate
import strformat
import strutils
import tables

# Import other modules
import common
import phylodata

proc buildTaxaBlock(phdata: PhyloData): string =
    var buf = @["BEGIN TAXA;"]
    buf.add &"\tDIMENSIONS NTAX={phdata.numTaxa};"
    buf.add "\tTAXLABELS"
    for taxon in phdata.getTaxa:
        buf.add &"\t\t{taxon}"
    buf.add "\t;"
    buf.add "END;"

    return join(buf, "\n")

proc buildMatrix(phdata: PhyloData): string =
    var symbols = "0123456789ABCDEFGHIJKLMNOPQRSTUVXWYZ"
    var value_char: char
    var lines = @["MATRIX"]
    var buf: string

    var chars = phdata.getChars # cache
    for taxon in phdata.getTaxa:
        buf = padString(taxon, phdata.maxTaxaLength+4)
        for ch in chars:
            # TODO: currently only working with single values
            var values = phdata.values.getOrDefault((taxon, ch))
            if len(values) == 0:
                value_char = '?'
            else:
                var idx = phdata.chars[ch].find(values.toSeq[0])
                value_char = symbols[idx]

            buf.add value_char

        lines.add buf

    # Add last line and return joined
    lines.add ";"

    join(lines, "\n")

# TODO: build symbols
# TODO: skip over statelabels when binary?
proc buildCharacterBlock(phdata: PhyloData): string =
    var buf = @["BEGIN CHARACTERS;"]
    buf.add &"\tDIMENSIONS NCHAR={phdata.numChars};"
    buf.add "\tFORMAT DATATYPE=STANDARD MISSING=? GAP=- SYMBOLS=\"0 1\";"
    buf.add "\tCHARSTATELABELS"
    for (count, label) in enumerate(1, phdata.getChars):
        var values = sorted(phdata.chars[label].toSeq)
        var valuesString = join(values, " ")
        buf.add &"\t\t{count} {label} /{valuesString},"
    buf.add "\t;"

    # Add separator, matrix, last line, and return
    buf.add ""
    buf.add buildMatrix(phdata)
    buf.add "END;"

    join(buf, "\n")

proc nexusOutput*(phdata: PhyloData): string =
    var blockTaxa = buildTaxaBlock(phdata)
    var blockCharacters = buildCharacterBlock(phdata)

    # Replace tabulations with spaces
    # TODO: allow to set spaces
    blockTaxa = replace(blockTaxa, "\t", "    ")
    blockCharacters = replace(blockCharacters, "\t", "    ")

    join(@[blockTaxa, blockCharacters], "\n")
