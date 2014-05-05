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

import sys, os

from .pyson import parseDir, parseFile, iteritems

try:
    from importlib.abc import MetaPathFinder, Loader
    class _NameTreeImporterParent(MetaPathFinder, Loader): pass
except ImportError:
    class _NameTreeImporterParent(object):
        def module_repr(self, module): raise NotImplementError("This method is only provided for python 2/3 compatibility.")

class NameTreeImporter(_NameTreeImporterParent):
    """NameTreeImporter acts as a generic importer, for importing arbitrary existing names as modules."""
    def __init__(self, rootModName, rootPath = None):
        self.rootMod     = rootModName
        self.rootPath    = rootPath
    
    def _getRootPath(self): return self.rootPath
    def _getRootMod (self): return self.rootMod
    
    def find_module(self, fullname, path = None):
        if not fullname.startswith(self._getRootMod()): return None
        if     fullname ==         self._getRootMod() : return None # We do not import the root object itself
        try: # needed to avoid non-PySON imports breaking for code located within a PySON tree and running on python 2
            self.load_module(fullname)
            return self
        except ImportError:
            return None
    
    def load_module(self, fullname):
        parentPkgName, dummy, modName = fullname.rpartition(".")
        if parentPkgName not in sys.modules: raise ImportError("Parent '%s' of '%s' not properly imported." % (parentPkgName, modName))
        parentPkg = sys.modules[parentPkgName]
        if not hasattr(parentPkg, modName): raise ImportError("Name '%s' does not exist at PySON path '%s'." % (modName, parentPkgName))
        return self._modulise(getattr(parentPkg, modName), fullname, parentPkgName)

    def _modulise(self, obj, fullname, parentPkgName):
        import imp
        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        mod.__file__   = None if self._getRootPath() is None else "<somewhere in %s>" % self._getRootPath()
        mod.__loader__ = self
        
        ispkg = False
        for name, item in iteritems(obj.__dict__):
            setattr(mod, name, item)
            if hasattr(item, "__dict__"): ispkg = True # If the object has any non-primitive members, we consider this a package, since we could further import those members as modules.
        
        if ispkg:
            mod.__path__ = []
            mod.__package__ = fullname
        else:
            mod.__package__ = parentPkgName
        return mod
    
    def module_repr(self, module): return super(self.__class__, self).module_repr(module)
    
    def __eq__(self, other): return isinstance(other, self.__class__) and self._getRootPath() == other._getRootPath() and self._getRootMod() == other._getRootMod()

class PysonImporter(NameTreeImporter):
    def __init__(self, rootModName, rootPath, includeRoot = True):
        """Make an importer which maps the PySON file or directory tree located at rootPath to the fully qualified module name rootModName. includeRoot controls whether the rootModName (and thus path) are included in this importer's responsibility."""
        super(self.__class__, self).__init__(rootModName, rootPath)
        self.includeRoot = includeRoot
    
    def find_module(self, fullname, path = None):
        if self.includeRoot and fullname == self._getRootMod(): return self
        return super(self.__class__, self).find_module(fullname, path)
    
    def load_module(self, fullname):
        if self.includeRoot and fullname == self._getRootMod():
            if os.path.isdir(self._getRootPath()): return self._modulise(parseDir (self._getRootPath()), fullname)
            else                                 : return self._modulise(parseFile(self._getRootPath()), fullname)
        else: return super(self.__class__, self).load_module(fullname)

def registerPysonImportRoot(rootPath, rootName, includeRoot = True):
    """Make the given rootPath (a PySON file, or a directory tree of PySON data) directly importable (including all names within the tree of PySON itself), under the fully qualified module name rootName. rootName itself is only included if includeRoot is True."""
    importer = PysonImporter(rootName, rootPath, includeRoot)
    if importer in sys.meta_path: sys.meta_path.remove(importer)
    sys.meta_path.append(importer)

def convertToPysonRootPackage(pkgGlobals, delname = None):
    """This is intended for making a directory tree of PySON data directly importable, e.g. by placing __init__.py at the root level, containing the line:
    
    import PySON; PySON.convertToPysonRootPackage(globals(), delname = "PySON")"""
    if delname is not None: del pkgGlobals[delname]
    
    rootDir  = os.path.dirname(os.path.realpath(pkgGlobals["__file__"]))
    rootName = pkgGlobals["__name__"]
    
    registerPysonImportRoot(rootDir, rootName, includeRoot = False)
    
    for name, item in iteritems(parseDir(rootDir).__dict__): pkgGlobals[name] = item
