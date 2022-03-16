import sys
import textwrap
import six
from . _DirNode import DirNode
from . _FileNode import FileNode
from . _shared import TYPE_FILE, TYPE_DIR, TYPE_ALL


class FsTree(DirNode):
    def __init__(self, flip_backslashes=None):
        DirNode.__init__(self, 'root')

        if flip_backslashes is None:
            self._flip_backslashes = sys.platform == 'win32'
        else:
            self._flip_backslashes = flip_backslashes

    def add(self, data, content=None):
        '''
            Convenience wrapper to add a file OR directory.
            If `data` endswith a backslash, consider this a directory, otherwise a file.
        '''
        if isinstance(data, dict):
            self.add_dict(data)
        elif isinstance(data, six.string_types):
            if data.count('\n'):
                self.add_yaml(data)
            else:
                data = textwrap.dedent(data)
                if data.endswith('/'):
                    self.add_dir(data)
                else:
                    self.add_file(data, content)
        else:
            raise ValueError(data)

    def add_file(self, file_path, content=None):
        if self._flip_backslashes:
            file_path = file_path.replace('\\', '/')
        parts = file_path.rsplit('/', 1)

        if len(parts) == 1:
            res = self.get_or_add_child_filenode(parts[0], content)
            return res
        else:
            dirpath, filename = parts
            dirnode = self.add_dir(dirpath)
            if dirnode is None:
                dirnode = self
            else:
                filenode = dirnode.get_or_add_child_filenode(filename, content)
                return filenode

    def add_dir(self, dirpath):
        if self._flip_backslashes:
            dirpath = dirpath.replace('\\', '/')
        dirpath = dirpath.rstrip('/')

        res = None
        cur_dirnode = self
        for part in dirpath.split('/'):
            exist_child = cur_dirnode.get_child(part)
            if exist_child:
                if isinstance(exist_child, FileNode):
                    raise IOError("A file '{}' already exists.".format(exist_child.get_fspath()))
                cur_dirnode = exist_child
            else:
                cur_dirnode = DirNode(part, parent=cur_dirnode)
            res = cur_dirnode
        return res

    def add_dict(self, dictionary, root_parent_dir=None):
        # TODO: Move onto `DirNode`
        for parent_dirname, child in dictionary.items():
            if root_parent_dir is None:
                parent_path = parent_dirname
            else:
                parent_path = '/'.join([root_parent_dir, parent_dirname])

            if isinstance(child, dict):
                if child == {}:
                    self.add_dir(parent_path)
                else:
                    self.add_dict(child, root_parent_dir=parent_path)
            else:
                self.add_file(parent_path, content=child)

    def add_yaml(self, yaml_string_dict, root_parent_dir=None):
        import oyaml as yaml
        yaml_string_dict = textwrap.dedent(yaml_string_dict)
        dictionary = yaml.safe_load(yaml_string_dict)
        self.add_dict(dictionary, root_parent_dir=root_parent_dir)

    def walk(self, top=None):
        if top is None:
            node = self.children[0]
        else:
            node = self._find_or_raise(top, TYPE_DIR)
        return node.walk()

    def open(self, file_path, mode='r'):
        if 'w' in mode:
            filenode = self.add_file(file_path)
            res = filenode.create_new_io()
            return res

        elif 'a' in mode:
            filenode = self.add_file(file_path)
            if filenode.io is None:
                res = filenode.create_new_io()
            else:
                res = filenode.get_exist_io()
                # Move cursor to the end so
                # we can append to it.
                res.seek(0, 2)
            return res

        elif 'r' in mode:
            filenode = self._get_exist_filenode(file_path)
            res = filenode.get_exist_io()
            res.seek(0)
            return res

    def _get_exist_filenode(self, file_path):
        curnode = self
        parts = file_path.split('/')
        for part in parts[:-1]:
            if curnode is None:
                self._raise_not_found(file_path)
            curnode = curnode.get_child(part, DirNode)

        if curnode is None:
            self._raise_not_found(file_path)

        filenode = curnode.get_child(parts[-1], FileNode)
        if not filenode:
            self._raise_not_found(file_path)

        return filenode

    def _find_or_raise(self, path, type_):
        nodes = self.find(path, type_)

        if not nodes:
            if type_ == TYPE_FILE:
                raise EnvironmentError("File not found: '{}'".format(path))
            elif type_ == TYPE_DIR:
                raise EnvironmentError("Directory not found: '{}'".format(path))
            elif type_ == TYPE_ALL:
                self._raise_not_found(path)

        res = nodes[0]

        return res

    def _raise_not_found(self, file_path):
        raise EnvironmentError("No such file or directory: '{}'".format(file_path))

