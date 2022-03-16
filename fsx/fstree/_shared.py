TYPE_ALL = 'all'
TYPE_FILE = 'file'
TYPE_DIR = 'dir'
TYPE_SYMLINK = 'symlink'

def node_matches_type(node, type):
    from . _FileNode import FileNode
    from . _DirNode import DirNode

    # TODO: implement `TYPE_SYMLINK` support

    if type == TYPE_ALL:
        return True
    elif type == TYPE_DIR and isinstance(node, DirNode):
        return True
    elif type == TYPE_FILE and isinstance(node, FileNode):
        return True
    return False

