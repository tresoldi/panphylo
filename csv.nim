# Imports from the standard library
import algorithm
import parsecsv
import sequtils
import sets
import streams
import strformat
import strutils
import tables

# Import other modules
import phylodata

# Define types used in this module
type phyloCSVRow = tuple[taxon: string, character: string, value: string]

proc readData(source: string, separator: char = ','): seq[phyloCSVRow] =
    var stream = newStringStream(source)

    # Instantiate csv parser, open file, and read columns
    var parser: CsvParser
    parser.open(stream, "stream.csv", separator = separator)
    parser.readHeaderRow()

    # Infer column names if not provided
    # TODO: implement using Python example
    var colTaxon = "Language_ID"
    var colChar = "Feature_ID"
    var colValue = "Value"

    # Read rows as named tuple
    var rows: seq[phyloCSVRow]
    while parser.readRow():
        var row: phyloCSVRow = (taxon: parser.rowEntry(colTaxon),
        character: parser.rowEntry(colChar),
        value: parser.rowEntry(colValue),
        )

        rows.add row

    # Close the parser and the stream, and return
    close parser
    close stream

    return rows

proc csvInput*(source: string): PhyloData =
    # Read data
    var rows = readData(source)

    # Collect all taxa, all characters and their values
    var taxa = initHashSet[string]()
    var chars = initTable[string, HashSet[string]]()
    var values = initTable[(string, string), HashSet[string]]()
    for row in rows:
        # Extend set of taxa
        taxa.incl row.taxon

        # If the value is not missing, add it to the character and to the matrix
        if row.value != "?":
            # Add the value to the character values set
            if not chars.hasKey(row.character):
                chars[row.character] = initHashSet[string]()

            chars[row.character].incl row.value

            # Add the value to the matrix set
            if not values.hasKey((row.taxon, row.character)):
                values[(row.taxon, row.character)] = initHashSet[string]()

            values[(row.taxon, row.character)].incl row.value

    # Build model and return
    var phdata = PhyloData(taxa: taxa, chars: chars, matrix: values)

    return phdata

proc csvOutput*(phdata: PhyloData, delimiter: char = ','): string =
    # Iterate over sorted keys and write
    var lines = @[&"Taxon{delimiter}Character{delimiter}Value"]

    var taxa = phdata.getTaxa # cache
    for ch in phdata.getChars:
        for taxon in taxa:
            var values = phdata.values.getOrDefault((taxon, ch))
            if len(values) > 0: # TODO: how to idiomatically test?
                for value in sorted(values.toSeq):
                    lines.add &"{taxon}{delimiter}{ch}{delimiter}{value}"

    join(lines, "\n")
