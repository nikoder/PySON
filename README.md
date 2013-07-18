PySON
=====

A simple parser for the simple Python Sh**ty Object Notation (PySON).

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

PySON Parser
-------------------------

This implementation offers a very simple parser for PySON.
