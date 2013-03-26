import ast

commentChar = "#"
assignmentChar = "="
blockChar = ":"

def parse(fname):
    result = {}
    curIndex = 0
    with open(fname, "r") as f: lines = f.readlines()
    while curIndex < len(lines):
        item, value, curIndex = _parseItem(lines, "", curIndex)
        if item is not None: result[item] = value
    return result

def _leadingWhitespace(s): return s[:-len(s.lstrip())]
def _multiTokenPartition(s, tokChars):
    minInd = len(s)
    for ch in tokChars:
        ind = s.find(ch)
        if ind >= 0: minInd = min(minInd, ind)
    return (s[:minInd], s[minInd:minInd + 1], s[minInd + 1:])


def _parseItem(lines, curIndent, curIndex):
    # white-space-only lines and comment only lines are ignored
    def isIgnoredLine(curLine): stripped = curLine.strip(); return stripped == "" or stripped.startswith("#")
    def _parseBlock(lines, parentIndent, curIndex):
        class Bunch(object): pass
        obj = Bunch()
        while curIndex < len(lines) and isIgnoredLine(lines[curIndex]): curIndex += 1
        if curIndex != len(lines):
            curIndent = _leadingWhitespace(lines[curIndex]) #found the what must be the first line of the new block; thus, determine the new indent
            while curIndex < len(lines) and ((lines[curIndex].startswith(curIndent) and curIndent != parentIndent) or isIgnoredLine(lines[curIndex])):
                item, value, curIndex = _parseItem(lines, curIndent, curIndex)
                if item is not None: obj.__dict__[item] = value
        return obj, curIndex
    
    curLine = lines[curIndex][len(curIndent):]
    if isIgnoredLine(curLine): return None, None, curIndex + 1

    # other lines must have valid indent...
    if not _leadingWhitespace(curLine) == "": raise IndentationError("Bad indentation at line no. %d:\n%s" % (curIndex, lines[curIndex]))
    
    # ...and must either assign a primitive to a name, or a compound object to a name
    item, sep, tail = _multiTokenPartition(curLine, "=:")
    if   sep == "=": value           = ast.literal_eval(tail.strip()); curIndex += 1
    elif sep == ":": value, curIndex = _parseBlock(lines, curIndent, curIndex + 1)
    else           : raise SyntaxError("Line no. %d is does not contain a valid assignment or block:\n%s" % (curIndex, lines[curIndex]))

    return item.strip(), value, curIndex

parse("base.pyon")
