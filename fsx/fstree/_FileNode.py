from datetime import datetime
try:
    from StringIO import StringIO
except ImportError:
    # py3
    from io import StringIO
import six

from . _Node import Node


__all__ = [
    'FileNode',
    'FileStringIO',
    'BytesFileStringIO',
]


class FileNode(Node):
    def __init__(self, name, parent=None):
        Node.__init__(self, name, parent=parent)
        self.io = None

    def create_new_io(self, cls=None, *args, **kwargs):
        cls = FileStringIO if cls is None else cls
        self.io = cls(*args, **kwargs)
        return self.io

    def get_exist_io(self, cls=None, *args, **kwargs):
        cls = FileStringIO if cls is None else cls
        if self.io is None:
            # An io object wasn't created yet.
            self.create_new_io(cls, *args, **kwargs)
        return self.io

    def get_size(self):
        content = self.as_dict()
        if content is None:
            return 0
        else:
            return len(content)

    def as_dict(self):
        if self.io is None:
            res = None
            return res
        else:
            previousPosition = self.io.tell()
            self.io.seek(0)
            res = self.io.read()
            self.io.seek(previousPosition)
            return res

class FileStringIO(StringIO):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_info, exc_tb):
        self.seek(0)
        return False

class BytesFileStringIO(six.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_info, exc_tb):
        self.seek(0)
        return False
