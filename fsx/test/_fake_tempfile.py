import os
import weakref
import errno
import io
import importlib
import six
from fstree import TYPE_DIR
from fstree._FileNode import FileNode, FileStringIO
import fsx

tempfile = importlib.import_module('tempfile')


class Mixin(object):
    def _fake_tempfile_NamedTemporaryFile(self, mode='w+b', suffix="", prefix=tempfile.template, dir=None, delete=True):
        if dir is None:
            dir = tempfile.gettempdir()

        path = _get_new_path(dir, prefix, suffix)
        if self._flip_backslashes:
            path = path.replace('\\', '/')

        if mode.startswith('w') or mode.startswith('a'):
            filenode = _add_named_node(self, path, delete)
            res = filenode.create_new_io()
            return res

        else:
            msg = "Mode string must begin with one of 'r', 'w' or 'a', not '{}'.".format(mode)
            raise ValueError(msg)


def _add_named_node(fstree, path, delete):
    dirname, basename = os.path.split(path)
    nodes = fstree.find(dirname, TYPE_DIR)
    dirnode = nodes[0] if nodes else fstree.add_dir(dirname)
    res = NamedTemporaryFileNode(path, delete, dirnode)
    return res

def _get_new_path(dir, prefix, suffix):
    ''' Extracted from `tempfile.py` to build proper temp-paths. '''
    names = tempfile._get_candidate_names()

    for seq in six.moves.xrange(tempfile.TMP_MAX):
        name = next(names)
        res = os.path.join(dir, prefix + name + suffix)
        if fsx.exists(res):
            continue
        return res

    raise IOError(errno.EEXIST, "No usable temporary file name found")

class AutoDeletableFileStringIO(FileStringIO):
    def __init__(self, filenode, path, delete):
        self._filenode = filenode
        self._delete_on_close = delete
        self.name = path
        FileStringIO.__init__(self)

    def close(self):
        if self._delete_on_close:
            self._filenode.remove()
        else:
            value = self.getvalue()
            parent_node = self._filenode.parent
            self._filenode.remove()

            new_filenode = FileNode(
                os.path.basename(self.name),
                parent_node,
            )
            new_filenode.get_exist_io().write(value)

        FileStringIO.close(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_info, exc_tb):
        self.seek(0)
        self.close()
        return False

class NamedTemporaryFileNode(FileNode):
    '''
        Custom `FileNode` class holding a weak reference
        to the IO object.
    '''
    def __init__(self, filepath, delete, parent):
        name = os.path.basename(filepath)
        FileNode.__init__(self, name, parent)
        self._filepath = filepath
        self._delete_on_close = delete
        self._io_ref = None

    def create_new_io(self):
        io = AutoDeletableFileStringIO(
            self,
            self._filepath,
            self._delete_on_close
        )

        # Use a weakref so the file-descriptor can be
        # properly garbage-collected like if the scope changes.
        def cb(ref):
            if ref() is None:
                # there are no more references
                if self._delete_on_close:
                    self.remove()

        self._io_ref = weakref.ref(io, cb)
        return io

    def get_exist_io(self):
        if self._io_ref is None:
            # An io object wasn't created yet.
            self.create_new_io()
            io = self._io_ref()
            return io
        else:
            io = self._io_ref()
            return io

