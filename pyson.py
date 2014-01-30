#
#    Copyright (C) 2013  Nikolaus Lieb
#
#    This file is part of PySON, a parser for a simple Python object literal language.
#
#    PySON is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PySON is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with PySON.  If not, see <http://www.gnu.org/licenses/>.
#

import ast, copy, itertools, inspect

# python 2/3 compatibility helper
def iteritems(dictionary): return getattr(dictionary, "iteritems", dictionary.items)()

defaultBunchIndent = " " * 4

commentChar      = "#"
assignmentChar   = "="
blockChar        = ":"
pysonExtension   = ".pyson"
DefaultBunchType = "PysonBunch"

def _bunchRepr(bunchDict, *args, **kwargs): # not in the class hierarchy, just to avoid name pollution
    lines = []
    maxKeyLen = max([0] + [len(key) for key in bunchDict if not isinstance(bunchDict[key], BaseBunch)])
    for key, val in iteritems(bunchDict):
        if not isinstance(val, BaseBunch):
            padding = " " * (maxKeyLen + 1 - len(key))
            lines.append(key + padding  + assignmentChar + " " + repr(val, *args, **kwargs))
        else:
            lines.append(namedBunchRepr(val, key, *args, **kwargs))
    return "\n".join(sorted(lines))

def namedBunchRepr(bunch, name, *args, **kwargs):
    return "\n".join([name + blockChar] + [defaultBunchIndent + line for line in repr(bunch, *args, **kwargs).split("\n")])

def bunchMergedDeepCopy(*allBunches):
    """return a deep copy of the first given bunch, which has been updated (overwriting any existing contents) with deep copies of any further given bunches. Returned bunch type is determined by the first argument."""
    res     = type(allBunches[0])()
    allKeys = set(itertools.chain(*(getattr(bunch, "keys", bunch.__dict__.keys)() for bunch in allBunches)))
    for key in allKeys:
        allDefinitions = tuple(getattr(bunch, key) for bunch in allBunches if hasattr(bunch, key))
        if isinstance(allDefinitions[-1], BaseBunch): # if the final (dominating) definition is a bunch, we want to merge it with any relevant preceding bunch definitions (i.e. ones which would not have been overriden by a non-bunch object)
            allMergeableDefinitions = []
            for definition in reversed(allDefinitions):
                if isinstance(definition, BaseBunch): allMergeableDefinitions.insert(0, definition)
                else                                : break
            setattr(res, key, allMergeableDefinitions[0].__mergedDeepCopy__(*allMergeableDefinitions[1:]))
        else:
            setattr(res, key, copy.deepcopy(allDefinitions[-1]))
    return res

PysonBunchConvenienceMethods = {"mergedDeepCopy" : bunchMergedDeepCopy,
                                "namedRepr"      : namedBunchRepr,
                                }

class BaseBunch(object):
    """Use this if you *really* want to avoid name collisions between entries in the raw PySON code and names belonging to the bunch object.
    
    The advantage of BaseBunch over PysonBunch is that there are fewer name collisions possible. The disadvantage is that, besides offering less convenience, these objects may *break* if there is a name collision.
    
    Note that it is recommended to just use PysonBunch and access colliding names via dict-style [] indexing instead of object-style . lookup.
    
    Run "dir(type("test", (object,), {})())" to get a list of these names, in your python version.
    
    WARNING: vulnerable to collisions with anything that is part of a basic python object"""
    def __repr__(self, *args, **kwargs): return _bunchRepr(self.__dict__, *args, **kwargs)

class SimplePysonBunch(BaseBunch, dict):
    """A safe PySON bunch type. Supports a dict interface, as well as object style "." lookup. Simply use the dict interface to access anything that would collide with built-in object or dict attributes.
    
    Run "dir(type("test", (dict), {})())" to get a list of these names, in your python version."""
    def __repr__(self, *args, **kwargs): return _bunchRepr(self, *args, **kwargs)
    def __setattr__(self, name, value):        self[name] = value
    def __getattr__(self, name       ): return self[name]

def attributeAugmentedClass(additionalAttrDict):
    def attributeAugmentedClass_inner(clsName, clsParents, clsAttrs):
        mergedAttrs = clsAttrs.copy()
        mergedAttrs.update(additionalAttrDict)
        return type(clsName, clsParents, mergedAttrs)
    return attributeAugmentedClass_inner

class PysonBunch(BaseBunch, dict):#SimplePysonBunch, dict):
    __metaclass__ = attributeAugmentedClass(PysonBunchConvenienceMethods)

def parseDir(dirp, useBunchType = None):
    import os
    pysonExt  = pysonExtension.lower()
    bunch = useBunchType() if useBunchType is not None else DefaultBunchType()
    for name in os.listdir(dirp):
        path = os.path.join(dirp, name)
        if   os.path.isdir        (path    ): bunch.__dict__[name                 ] = parseDir (path)
        elif name.lower().endswith(pysonExt): bunch.__dict__[name[:-len(pysonExt)]] = parseFile(path)
    return bunch

def parseFile(fname, useBunchType = None):
    with open(fname, "r") as f: return parse(f.read(), useBunchType)

def parse(string, useBunchType = None):
    """Parses the given PySON string and returns its contents as a single PysonBunch representing the whole string."""
    result = useBunchType() if useBunchType is not None else DefaultBunchType()
    lines = string.split("\n")
    curIndex = 0
    while curIndex < len(lines):
        item, value, curIndex = _parseItem(lines, "", curIndex, type(result))
        if item is not None: result[item] = value
    return result

def _leadingWhitespace(s): return s[:-len(s.lstrip())]
def _multiTokenPartition(s, tokChars):
    minInd = len(s)
    for ch in tokChars:
        ind = s.find(ch)
        if ind >= 0: minInd = min(minInd, ind)
    return (s[:minInd], s[minInd:minInd + 1], s[minInd + 1:])


def _parseItem(lines, curIndent, curIndex, bunchType):
    # white-space-only lines and comment only lines are ignored
    def isIgnoredLine(curLine): stripped = curLine.strip(); return stripped == "" or stripped.startswith("#")
    def _parseBlock(lines, parentIndent, curIndex):
        obj = bunchType()
        while curIndex < len(lines) and isIgnoredLine(lines[curIndex]): curIndex += 1
        if curIndex != len(lines):
            curIndent = _leadingWhitespace(lines[curIndex]) #found what must be the first line of the new block; thus, determine the new indent
            if curIndent != parentIndent:                   #if they are the same, this block was empty
                while curIndex < len(lines) and (lines[curIndex].startswith(curIndent) or isIgnoredLine(lines[curIndex])): #the block ends when it doesn't start with the current indentation level on a line which wouldn't be ignored anyway
                    item, value, curIndex = _parseItem(lines, curIndent, curIndex)
                    if item is not None: obj.__dict__[item] = value
        return obj, curIndex
    
    curLine = lines[curIndex]
    if isIgnoredLine(curLine): return None, None, curIndex + 1
    curLine = curLine[len(curIndent):]

    # other lines must have valid indent...
    if not _leadingWhitespace(curLine) == "": raise IndentationError("Bad indentation at line no. %d:\n%s" % (curIndex + 1, lines[curIndex]))
    
    # ...and must either assign a primitive to a name, or a compound object to a name
    item, sep, tail = _multiTokenPartition(curLine, "=:")
    if   sep == "=": value           = ast.literal_eval(tail.strip()); curIndex += 1
    elif sep == ":": value, curIndex = _parseBlock(lines, curIndent, curIndex + 1)
    else           : raise SyntaxError("Line no. %d does not contain a valid assignment or block:\n%s" % (curIndex + 1, lines[curIndex]))

    return item.strip(), value, curIndex

DefaultBunchType = globals()[DefaultBunchType]
