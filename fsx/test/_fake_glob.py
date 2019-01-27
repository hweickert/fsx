import os
from fnmatch import fnmatch
from fstree import FsTree, TYPE_FILE, TYPE_DIR, node_matches_type
import fsx


class Mixin(object):
    def _fake_glob_glob(self, pattern):
        if self._flip_backslashes:
            pattern = pattern.replace('\\', '/')

        res = list(self._fake_glob_iglob(pattern))
        return res

    def _fake_glob_iglob(self, pattern):
        if self._flip_backslashes:
            pattern = pattern.replace('\\', '/')

        pat_parts = pattern.split('/')
        res = _getMatchingNodePaths(self, pat_parts, 0)
        return res

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

