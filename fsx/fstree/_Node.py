import copy
from datetime import datetime
from anytree import Node as BaseNode


class Node(BaseNode):
    def __init__(self, *a, **kwa):
        BaseNode.__init__(self, *a, **kwa)

        self.ctime = datetime.now()
        self.mtime = copy.copy(self.ctime)
        self.atime = copy.copy(self.ctime)

    def remove(self):
        if self.children:
            raise EnvironmentError("Cannot remove node '{}' which has children.".format(self.name))

        if self.parent is None:
            # The parent node might have been deleted by now.
            return

        self.parent.children = tuple([child for child in self.parent.children if child != self])

    def as_dict(self):
        res = {}
        for child in self.children:
            res[child.name] = child.as_dict()
        return res

    def get_fspath(self):
        res = '/'.join([node.name for node in self.path[1:]])
        return res

    def get_child(self, name, type_=None):
        if type_ is None:
            type_ = Node
        for c in self.children:
            if c.name == name:
                if isinstance(c, type_):
                    return c
        return None
