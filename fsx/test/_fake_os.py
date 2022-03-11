import sys
from fstree import TYPE_FILE, TYPE_DIR
from ._helpers import env_error_to_os_specific
from . _Stat import Stat

import importlib
os = importlib.import_module('os')

def _is_win_abspath(path):
    res = sys.platform == 'win32' and path[1:2] == ':'
    return res

def _is_win_driveletter_with_trail_slash(path):
    return len(path) == 3 and path[1] == ':'

class Mixin(object):
    _curdir = ''

    def _fake_os_chdir(self, path):
        if self._flip_backslashes:
            path = path.replace('\\', '/')

        if path == '/':
            path = ''

        dirnode = self._find_or_raise(path, TYPE_DIR)

        if _is_win_driveletter_with_trail_slash(path):
            # self._setCurDir(path[:-1])
            self._curdir = path[:-1]
        else:
            # self._setCurDir(path.rstrip('/'))
            self._curdir = path.rstrip('/')

    def _fake_os_getcwd(self):
        if len(self._curdir) == 2 and self._curdir[1] == ':':
            return self._curdir + '/'
        else:
            return self._curdir

    def _get_abspath_from_relative(self, path):
        if self._curdir == '':
            res = path.lstrip('/')
            return res
        else:
            res = self._curdir + '/' + path.lstrip('/')
            return res

    def _fake_os_path_exists(self, path):
        if path == '':
            return False

        if self._flip_backslashes:
            path = path.replace('\\', '/')

        abspath_from_relative = self._get_abspath_from_relative(path)
        found_as_relative = bool(self.find(abspath_from_relative))
        if found_as_relative:
            return True
        else:
            res = bool(self.find(path))
            return res

    def _fake_os_path_getsize(self, path):
        if self._flip_backslashes:
            path = path.replace('\\', '/')

        abspath_from_relative = self._get_abspath_from_relative(path)
        found_as_relative_nodes = self.find(abspath_from_relative, TYPE_FILE)
        if found_as_relative_nodes:
            file_node = found_as_relative_nodes[0]
        else:
            file_node = self._find_or_raise(path, TYPE_FILE)

        file_node_content = file_node.as_dict()
        if file_node_content is None:
            return 0
        else:
            return len(file_node_content)

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

        name = os.path.normpath(name).replace('\\', '/')
        if name[:1].isalnum() and self._curdir:
            # make an absolute path using the current directory
            name = self._curdir + '/' + name

        self.add_dir(name)

    def _fake_os_rmdir(self, path):
        if self._flip_backslashes:
            path = path.replace('\\', '/')

        dirnode = self._find_or_raise(path, TYPE_DIR)
        if dirnode.children:
            if sys.platform == 'win32':
                raise WindowsError(145, "The directory is not empty: '{}'".format(path))
            else:
                raise OSError(66, "Directory not empty: '{}'".format(path))
        dirnode.remove()

    def _fake_os_remove(self, path):
        if self._flip_backslashes:
            path = path.replace('\\', '/')

        filenode = self._find_or_raise(path, TYPE_FILE)
        filenode.remove()

    def _fake_os_stat(self, path):
        if self._flip_backslashes:
            path = path.replace('\\', '/')

        file_node = self._find_or_raise(path, TYPE_FILE)
        res = Stat(file_node)
        return res
