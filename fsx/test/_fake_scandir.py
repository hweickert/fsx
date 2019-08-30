import sys
import os


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

class Stat(object):
    def __init__(self, node):
        self._node = node

        self.st_mode = self._get_st_mode()

        self.st_ino = property(self._not_implemented)  # inode number,
        self.st_dev = property(self._not_implemented)  # device,
        self.st_nlink = property(self._not_implemented)  # number of hard links,
        self.st_uid = property(self._not_implemented)  # user id of owner,
        self.st_gid = property(self._not_implemented)  # group id of owner,
        self.st_size = property(self._not_implemented) # size of file, in bytes,
        self.st_atime = property(self._not_implemented)  # time of most recent access,
        self.st_mtime = property(self._not_implemented)  # time of most recent content modification,
        self.st_ctime = property(self._not_implemented)  # platform dependent; time of most recent metadata change on Unix, or the time of creation on Windows)

    def _not_implemented(self):
        raise NotImplementedError

    def _get_st_mode(self):
        if node_matches_type(self._node, TYPE_DIR):
            return 0o40777
        elif node_matches_type(self._node, TYPE_FILE):
            return 0o100666
        elif node_matches_type(self._node, TYPE_SYMLINK):
            import sys
            return eval('0o40777L')
        else:
            raise ValueError('Unknown file type: {}'.format(self._node.get_fspath()))
