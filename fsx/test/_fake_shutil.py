import os
import sys
from fstree import TYPE_DIR


class Mixin(object):
    _curdir = ''

    def _fake_shutil_rmtree(self, path, ignore_errors=False, onerror=None):
        if self._flip_backslashes:
            path = path.replace('\\', '/')

        res = []
        path = path.rstrip('/')

        try:
            dirnode = self._find_or_raise(path, TYPE_DIR)
        except Exception:
            if ignore_errors:
                return
            if onerror is not None:
                fn = self._find_or_raise
                exc_info = sys.exc_info()
                onerror(fn, path, exc_info)
            else:
                raise

        try:
            _remove_node_recursive(dirnode)
        except Exception:
            if ignore_errors:
                return
            if onerror is not None:
                fn = _remove_node_recursive
                exc_info = sys.exc_info()
                onerror(fn, path, exc_info)
            else:
                raise


def _remove_node_recursive(node):
    for childnode in node.children:
        _remove_node_recursive(childnode)
    node.remove()
