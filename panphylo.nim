# Import other modules
import common
import csv
import nexus

var
    source: string
    target: string

source = readPhyloFile("tests/test_data/example.csv")
var phdata = csvInput(source)

target = csvOutput(phdata)
target = nexusOutput(phdata)

#echo target
