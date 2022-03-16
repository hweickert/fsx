from . _Node import Node
from . _FileNode import FileNode, BytesFileStringIO
from . _shared import node_matches_type, TYPE_ALL, TYPE_DIR, TYPE_FILE


class DirNode(Node):
    def find(self, path, type=TYPE_ALL):
        path = path.rstrip('/')
        pat_parts = path.split('/')
        res = _find_nodes_recursive(self, pat_parts, 0, type)
        return res

    def get_fs_filepaths(self):
        res = [desc.get_fspath() for desc in self.descendants if isinstance(desc, FileNode)]
        return res

    def get_fs_dirpaths(self):
        res = [desc.get_fspath() for desc in self.descendants if isinstance(desc, DirNode)]
        return res

    def get_or_add_child_filenode(self, filename, content):
        exist_node = self.get_child(filename)
        if exist_node:
            if isinstance(exist_node, DirNode):
                raise IOError("A directory '{}' already exists.".format(exist_node.get_fspath()))
            return exist_node
        else:
            res = FileNode(filename, parent=self)
            if content is not None:
                res_io = res.create_new_io(BytesFileStringIO if isinstance(content, bytes) else None)
                res_io.write(content)
                res_io.seek(0)
            return res

    def as_list(self):
        ''' Return a list of absolute paths. '''
        res = []
        self._as_list_recursive(self, res, '')
        return res

    def _as_list_recursive(self, parent, res, prefix):
        for child in parent.children:
            if child.children:
                self._as_list_recursive(child, res, prefix + child.name + '/')
            else:
                # leaf node
                if isinstance(child, DirNode):
                    res.append(prefix + child.name + '/')
                else:
                    res.append(prefix + child.name)


    def clear(self):
        ''' Clears all children. '''
        self.children = ()


    def walk(self):
        ''' Very similar to `os.walk` but yields `DirNode` and `FileNode` instances. '''
        # Not yet supported parameters: topdown=True, onerror=None, followlinks=False

        for root, dir_nodes, file_nodes in _walk_recursive(self, self.name):
            dir_names = [dir_node.name for dir_node in dir_nodes]
            file_names = [file_node.name for file_node in file_nodes]
            yield (root, dir_names, file_names)


    def walk_nodes(self):
        ''' Very similar to `os.walk` but yields `DirNode` and `FileNode` instances. '''
        # Not yet supported parameters: topdown=True, onerror=None, followlinks=False

        for elem in _walk_recursive(self):
            yield elem


def _walk_recursive(rootnode, prefix=None):
    sub_rootnode = rootnode
    sub_dir_children = []
    sub_file_children = []
    for sub_child in sub_rootnode.children:
        if node_matches_type(sub_child, TYPE_DIR):
            sub_dir_children.append(sub_child)
        elif node_matches_type(sub_child, TYPE_FILE):
            sub_file_children.append(sub_child)

    yield (prefix, sub_dir_children, sub_file_children)

    for dir_node in sub_dir_children:
        if prefix is None:
            for elem in _walk_recursive(dir_node, dir_node.name):
                yield elem
        else:
            for elem in _walk_recursive(dir_node, prefix+'/'+dir_node.name):
                yield elem


def _find_nodes_recursive(node, pat_parts, level, type_):
    res = []
    islast = level == len(pat_parts) - 1
    for childnode in node.children:
        name_matches = childnode.name == pat_parts[level]
        if not name_matches:
            continue
        if islast:
            if node_matches_type(childnode, type_):
                res.append(childnode)
        else:
            subchild_nodes = _find_nodes_recursive(childnode, pat_parts, level+1, type_)
            res.extend(subchild_nodes)
    return res
