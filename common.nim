# TODO: check if really needed
proc padString*(text: string, minLength: int, pad: char = ' '): string =
    var paddedText = text
    for i in countup(len(text)+1, minLength):
        paddedText.add pad

    paddedText

proc readPhyloFile*(filename: string): string =
    let source = readFile(filename)

    source
