import sys
import os

from . _Stat import Stat


if sys.version_info.major > 2:
    import fsx._scandir_module
    GenericDirEntry = fsx._scandir_module.GenericDirEntry
else:
    import scandir
    GenericDirEntry = scandir.GenericDirEntry

from fstree import TYPE_FILE, TYPE_ALL, TYPE_DIR, TYPE_SYMLINK, node_matches_type

__all__ = ['Mixin']


class Mixin(object):
    def _fake_scandir_scandir(self, path):
        if self._flip_backslashes:
            path = path.replace('\\', '/')

        parent_node = self._find_or_raise(path, TYPE_ALL)
        for child_node in parent_node.children:
            dir_entry = FakeDirEntry(child_node)
            yield dir_entry


class FakeDirEntry(GenericDirEntry):
    __slots__ = ('name', '_stat', '_lstat', '_scandir_path', '_path', '_node')

    def __init__(self, node):
        self._node = node
        dirname, basename = os.path.split(node.get_fspath())
        GenericDirEntry.__init__(self, dirname, basename)

    def stat(self, follow_symlinks=True):
        if follow_symlinks:
            if self._stat is None:
                self._stat = _fake_stat(self._node)
            return self._stat
        else:
            if self._lstat is None:
                self._lstat = _fake_lstat(self.path)
            return self._lstat

def _fake_stat(node):
    return Stat(node)

def _fake_lstat(node):
    raise NotImplementedError()

