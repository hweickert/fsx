import sys

from fstree import TYPE_FILE, TYPE_DIR, TYPE_SYMLINK, node_matches_type


__all__ = [
    'Stat',
]


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

    @property
    def st_ctime(self): return self._node.ctime.timestamp()

    @property
    def st_mtime(self): return self._node.mtime.timestamp()

    @property
    def st_atime(self): return self._node.atime.timestamp()

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
