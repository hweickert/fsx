import sys
from fstree import TYPE_FILE, TYPE_DIR
from ._helpers import env_error_to_os_specific


class Mixin(object):
    def _fake_os_path_exists(self, path):
        if self._flip_backslashes:
            path = path.replace('\\', '/')
        res = bool(self.find(path))
        return res

    def _fake_os_path_isfile(self, path):
        if self._flip_backslashes:
            path = path.replace('\\', '/')
        nodes = self.find(path, TYPE_FILE)
        if nodes:
            return True
        return False

    def _fake_os_path_isdir(self, path):
        if self._flip_backslashes:
            path = path.replace('\\', '/')
        nodes = self.find(path, TYPE_DIR)
        if nodes:
            return True
        return False

    def _fake_os_listdir(self, path):
        if self._flip_backslashes:
            path = path.replace('\\', '/')

        res = []
        path = path.rstrip('/')
        dirnode = self._find_or_raise(path, TYPE_DIR)
        res = [child.name for child in dirnode.children]
        return res

    def _fake_os_walk(self, top):
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

    def _fake_os_makedirs(self, name):
        if self._fake_os_path_exists(name):
            if sys.platform == 'win32':
                raise WindowsError(183, "Cannot create a file when that file already exists: '{}'".format(name))
            else:
                raise OSError(17, "File exists: '{}'".format(name))
        self.add_dir(name)

    def _fake_os_rmdir(self, path):
        dirnode = self._find_or_raise(path, TYPE_DIR)
        if dirnode.children:
            if sys.platform == 'win32':
                raise WindowsError(145, "The directory is not empty: '{}'".format(path))
            else:
                raise OSError(66, "Directory not empty: '{}'".format(path))
        dirnode.remove()

