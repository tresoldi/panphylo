# Imports from the standard library
import std/algorithm
import std/sequtils
import std/sets
import std/tables

# NOTE: these are not sorted, it is up to the output filter to sort (or not)

type PhyloData* = object
  taxa*: HashSet[string]
  chars*: Table[string, HashSet[string]]
  matrix*: Table[(string, string), HashSet[string]]

method getTaxa*(this: PhyloData): seq[string] {.base.} =
  sorted(this.taxa.toSeq)

method getChars*(this: PhyloData): seq[string] {.base.} =
  sorted(this.chars.keys.toSeq)

method numTaxa*(this: PhyloData): int {.base.} =
  len(this.taxa)

method numChars*(this: PhyloData): int {.base.} =
  len(this.chars)

method maxTaxaLength*(this: PhyloData): int {.base.} =
  var maxLength = 0
  for taxon in this.taxa:
    maxLength = max(maxLength, len(taxon))

  maxLength
