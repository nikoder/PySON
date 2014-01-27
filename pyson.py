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

def bunchRepr(bunch, *args, **kwargs):
    """Returns a valid PySON representation of the given bunch object.
    
    Since an object usually doesn't know the name it is stored under, a bunch settles for just returning a valid PySON representation of the set of its constituents. For creating a repr of any kind of named PySON bunch use namedBunchRepr(name, bunch)."""
    print "boing"
    if len(bunch...) == 0: return ""
    print "boing"
    lines = []
    maxKeyLen = max([0] + [len(key) for key in bunch if not isinstance(bunch[key], BaseBunch)])
    for key, val in iteritems(bunch...):
        if not isinstance(val, BaseBunch):
            padding = " " * (maxKeyLen + 1 - len(key))
            lines.append(key + padding  + assignmentChar + " " + repr(val, *args, **kwargs))
        else:
            lines.append(namedBunchRepr(key, val, *args, **kwargs))
    return "\n".join(sorted(lines))

def namedBunchRepr(name, bunch, *args, **kwargs):
    return name + blockChar + ("" if len(bunch) == 0 else "\n" + defaultBunchIndent + repr(bunch, *args, **kwargs).replace("\n", "\n" + defaultBunchIndent))

def bunchRepr

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
                else                                     : break
            setattr(res, key, allMergeableDefinitions[0].__mergedDeepCopy__(*allMergeableDefinitions[1:]))
        else:
            setattr(res, key, copy.deepcopy(allDefinitions[-1]))
    return res

def bunchIterItems(self): return iteritems(self)

class BaseBunch(object): pass #FIXME: Base type is misleading. They won't support the same interface (at least for now: no way to "list" the keys in a SimplePysonBunch).
class SimplePysonBunch(BaseBunch):
    """Use this if you *really* want to avoid name collisions between entries in the raw PySON code and names belonging to the bunch object.
    
    WARNINGS:
        * still vulnerable to collisions with anything that is part of a basic python object
        * does not support any convenience, such as using repr(SimplePysonBunch) to get a PySON string representation of the object
    
    Where possible, it is recommended to use PysonBunch and simply avoid the use of the following names in PySON definitions:
        * anything that is a part of basic python objects
        * anything that is a part of python dict objects
        * anything that is listed in PysonBunchConvenienceMethods above"""

#def dictMerged(future_class_name, future_class_parents, future_class_attr):
#    mergedAttrs = future_class_attr.copy()
#    class dum(object): pass
#    sample = dum().__dict__
#    for name in dir(sample):
#        if name not in mergedAttrs:
#            if inspect.isbuiltin(getattr(sample, name)):
#                def dictRedirect(*args, **kwargs): getattr(args[0].__dict__, name)(*args[1:], **kwargs)
#                mergedAttrs[name] = dictRedirect
#    return type(future_class_name, future_class_parents, mergedAttrs)
def attributeAugmentedClass(additionalAttributes):
    def attributeAugmentedClass_inner(futureClsName, futureClsParents, futureClsAttrs):
        mergedAttrs = futureClsAttrs.copy()
        mergedAttrs.update(additionalAttributes)
        return type(futureClsName, futureClsParents, mergedAttrs)
    return attributeAugmentedClass_inner

class PysonBunch(BaseBunch, dict):#SimplePysonBunch, dict):
    __metaclass__ = attributeAugmentedClass(PysonBunchConvenienceMethods)
#    def __repr__(self): pass
#    def __getattribute__(self, name):
#        print name
#        supergetattr = super(PysonBunch, self).__getattribute__ #probably going to effectively map to object.__getattribute__, but may not
#        selfdict = supergetattr("__dict__")
#        if name == "__getattribute__": return supergetattr(name) #faithfully return ourselves, if asked
#        elif name in PysonBunchConvenienceMethods: #bunch convenience methods take priority over any other features
#            unboundMethod = PysonBunchConvenienceMethods[name]
#            def fakeBound(*args, **kwargs): return unboundMethod(self, *args, **kwargs)
#            return fakeBound
#        else:
#            try: return supergetattr(name) #in any other case, fall back to default getattr behaviour
#            except AttributeError as e:
##                if hasattr(selfdict, name): return getattr(selfdict, name)  #if we are trying to use a feature supported by dictionaries, we support this by calling the method on the underlying __dict__, which PySON exclusively uses to store any bunch's members
#                raise e
    def __setattr__(self, name, value):        self[name] = value
    def __getattr__(self, name       ): return self[name]

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

DefaultBunchType = PysonBunch
PysonBunchConvenienceMethods = {"__repr__"       : bunchRepr,
                                "mergedDeepCopy" : bunchMergedDeepCopy,
                                }
