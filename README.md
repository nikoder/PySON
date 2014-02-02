PySON
=====

A simple parser for the simple Python Sh**ty Object Notation (PySON). (Tested on both Python 2.7 and Python 3.3.)

About The PySON Syntax
----------------------

The intent of PySON is to provide a simple way of writing literals of Python objects.

Of course, it is possible to create Python objects in Python itself, but PySON has 3 advantages (in the eyes of the author):

 * PySON is less verbose (making it easier to write)
 * PySON is more easily readable
 * Since PySON is not an executable format it is slightly safer.

The main application of PySON is seen in writing simple Pythonic config files.

PySON files are expected to use the extension ".pyson"

### PySON Rules

 * Comments and whitespace work like they do in Python
 * All standard Python literals for primitive values are supported (based on Python's `ast`)
 * Objects are defined by specifying the objects name, followed by a colon
 * Indentation is used to create a block of values belonging to an object

### Example PySON File

```python
# I have something worthwhile to say

object1:                       # I just wanted to make a note about this object
    int1    = 1                # Well, *I* have something to say about this variable
    float1  = 1.0
    string1 = "I am a string."
    list1   = [1, 1.0, "I am a string inside a list", [0, (1,2,3)]]
    
    subObject1:
        int1     = 1
        float1   = 1.0
#       disabled = "I am a disabled variable"
        string1  = "I am another string belonging to subObject1."

rootLvlObj = {"a" : 1, "b" : [(1,2),(3,4)]} # Primitives can live on the root level as well, of course.
```

If this file is parsed into the name `pysonData`, you can access the values, such as:

```python
>>> pysonData.object1.int1
1
>>> pysonData.object1.subObject1.float1
1.0
>>> pysonData.rootLvlObj
{'a': 1, 'b': [(1, 2), (3, 4)]}
```

PySON Parser and Importer
-------------------------

This implementation offers a simple parser for PySON. You can use it to parse PySON from strings, files, or whole directory trees.

The parser returns instances of `PysonBunch` for every object defined in PySON. [See below](#bunchinfo) for details on `PysonBunch` objects.

When parsing from a directory tree, the file and directory structure becomes a corresponding tree of PySON bunch objects. Only *.pyson files are parsed.

This implementation also offers a PySON importer, which allows you to import any name from within a tree of PySON objects.

This is particularly useful if you just want to turn a directory structure of PySON data into something you can freely import from. To achieve this, you can make the root of the tree a Python package, with the following contents in the `__init__.py`:

```python
import PySON; PySON.convertToPysonRootPackage(globals(), delname = "PySON")
```

The optional `delname` argument can be used to remove unwanted name polution (such as the import of PySON) from the tree, before populating it with the parsed PySON data.

### <a name="bunchinfo"></a> `PysonBunch` Objects

`PysonBunch` objects behave very much like dicts and support most of their built-in operations (such as indexing and `in` tests), but the names stored in them are, of course, also accessible via `getattr()` and the `.` operator.

`PysonBunch` objects support conversion back to valid PySON strings, via `__repr__`. Calling `repr` on a `PysonBunch` will only produce a representation of the values contained **within** the bunch, since the bunch does not know its own name. To get a full representation of the named bunch, you can use the helper method `namedBunchRepr(name, bunch)`.

#### Limitations

Almost any valid PySON object can be represented by a `PysonBunch`. The only exception are names which match special Python magic functions (such as `__getattr__`). Interestingly, due to cpython optisations, it appears that such name collisions do not affect the interpreter, while still providing any user values to user code. This may not be true for all cases, and, especially for other execution platforms besides cpython, however. Yet all "better" solutions increase code complexity and verbosity to such an extent, that they are not currently deemed worthwhile. If you do run into problems due to this decision, please feel free to raise an issue on github.

Comments are not presently preserved, when parsing PySON into `PysonBunch`es. So, while `repr` on a bunch produces pretty formatted output, it is not yet suitable for re-writing user files, as their comments would be lost.
