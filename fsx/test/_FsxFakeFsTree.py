import sys
import os
from fnmatch import fnmatch
from fstree import FsTree, TYPE_FILE, TYPE_DIR, node_matches_type
import fsx
import fsx.glob


class FsxFakeFsTree(FsTree):
    ''' A virtual file system tree supporting some common file system functions. '''
    def __init__(self, monkeypatch, flip_backslashes=None):
        FsTree.__init__(self, flip_backslashes=flip_backslashes)

        monkeypatch.setattr(fsx,      'exists',  self._fake_exists)
        monkeypatch.setattr(fsx,      'isfile',  self._fake_isfile)
        monkeypatch.setattr(fsx,      'isdir',   self._fake_isdir)
        monkeypatch.setattr(fsx,      'listdir', self._fake_listdir)
        monkeypatch.setattr(fsx.glob, 'iglob',   self._fake_iglob)
        monkeypatch.setattr(fsx.glob, 'glob',    self._fake_glob)
        monkeypatch.setattr(fsx,      'makedirs',self._fake_makedirs)
        monkeypatch.setattr(fsx,      'open',    self._fake_open)
        monkeypatch.setattr(fsx,      'walk',    self._fake_walk)

    def _fake_exists(self, path):
        if self._flip_backslashes:
            path = path.replace('\\', '/')
        res = bool(self.find(path))
        return res

    def _fake_isfile(self, path):
        if self._flip_backslashes:
            path = path.replace('\\', '/')
        nodes = self.find(path, TYPE_FILE)
        if nodes:
            return True
        return False

    def _fake_isdir(self, path):
        if self._flip_backslashes:
            path = path.replace('\\', '/')
        nodes = self.find(path, TYPE_DIR)
        if nodes:
            return True
        return False

    def _fake_listdir(self, path):
        if self._flip_backslashes:
            path = path.replace('\\', '/')

        res = []
        path = path.rstrip('/')
        dirnode = self._find_or_raise(path, TYPE_DIR)
        res = [child.name for child in dirnode.children]
        return res

    def _fake_walk(self, top):
        # Not yet supported parameters: topdown=True, onerror=None, followlinks=False

        if self._flip_backslashes:
            top = top.replace('\\', '/')
        node = self._find_or_raise(top, TYPE_DIR)

        if top.count('/'):
            prefix = top.rsplit('/', 1)[0] + '/'
        else:
            prefix = ''

        for root, dirname, filenames in node.walk():
            if root is None:
                root = top
            root = prefix + root
            yield root, dirname, filenames

    def _fake_glob(self, pattern):
        if self._flip_backslashes:
            pattern = pattern.replace('\\', '/')

        res = list(self._fake_iglob(pattern))
        return res

    def _fake_iglob(self, pattern):
        if self._flip_backslashes:
            pattern = pattern.replace('\\', '/')

        pat_parts = pattern.split('/')
        res = _getMatchingNodePaths(self, pat_parts, 0)
        return res

    def _fake_makedirs(self, name):
        if self._fake_exists(name):
            if sys.platform == 'win32':
                raise WindowsError("Cannot create a file when that file already exists: '{}'".format(name))
            else:
                raise IOError("Cannot create a file when that file already exists: '{}'".format(name))
        self.add_dir(name)

    def _fake_open(self, path, mode='r', encoding=None):
        if self._flip_backslashes:
            path = path.replace('\\', '/')

        if mode.startswith('r'):
            filenode = self._find_or_raise(path, TYPE_FILE)
            res = filenode.get_exist_io()
            res.seek(0)
            return res
        elif mode.startswith('a'):
            filenodes = self.find(path, TYPE_FILE)
            if not filenodes:
                # the file doesn't exist yet but the parent directory should.
                dirpath = os.path.dirname(path)
                self._find_or_raise(dirpath, TYPE_DIR)
                filenode = self.add_file(path)
            else:
                filenode = filenodes[0]
            res = filenode.get_exist_io()
            # Jump to end of stream so one can append to it.
            res.seek(0, 2)
            return res
        elif mode.startswith('w'):
            nodes = self.find(path, TYPE_FILE)
            filenode = nodes[0] if nodes else self.add_file(path)
            res = filenode.create_new_io()
            return res
        else:
            msg = "Mode string must begin with one of 'r', 'w' or 'a', not '{}'.".format(mode)
            raise ValueError(msg)

def _getMatchingNodePaths(node, pat_parts, level):
    res = []
    islast = level == len(pat_parts) - 1
    for childnode in node.children:
        matches = fnmatch(childnode.name, pat_parts[level])
        if matches and islast:
            res.append(childnode.get_fspath())
        elif matches:
            res += _getMatchingNodePaths(childnode, pat_parts, level+1)
    return res

