import os
from fstree import TYPE_FILE, TYPE_DIR
from fstree import BytesFileStringIO
from fstree import FileStringIO



class Mixin(object):
    # TODO: implement `newline`
    # TODO: `pathlib.Path` support for python3
    def _fake_builtins_open(self, path, mode='r', encoding=None, newline=None):
        if self._flip_backslashes:
            path = path.replace('\\', '/')

        if mode.startswith('r'):
            filenode = self._find_or_raise(path, TYPE_FILE)
            res = filenode.get_exist_io()
            if mode.endswith('b'):
                if res.__class__ == FileStringIO:
                    value = res.getvalue()
                    if value is not None:
                        value = value.encode()
                    res = BytesFileStringIO(value)
            else:
                if res.__class__ == BytesFileStringIO:
                    value = res.getvalue()
                    if value is not None:
                        value = value.decode(encoding or 'utf-8')
                    res = FileStringIO(value)

            res.seek(0)
            return res
        elif mode.startswith('a'):
            filenode = self._find_or_create_writable_filenode(path)
            res = filenode.get_exist_io()
            # Jump to end of stream so one can append to it.
            res.seek(0, 2)
            return res
        elif mode.startswith('w'):
            filenode = self._find_or_create_writable_filenode(path)
            cls = BytesFileStringIO if mode.endswith('b') else None
            res = filenode.create_new_io(cls)
            return res
        else:
            msg = "Mode string must begin with one of 'r', 'w' or 'a', not '{}'.".format(mode)
            raise ValueError(msg)

    def _find_or_create_writable_filenode(self, path):
        filenodes = self.find(path, TYPE_FILE)
        if not filenodes:
            # the file doesn't exist yet but the parent directory should.
            dirpath = os.path.dirname(path)
            if dirpath == '':
                # there is no parent directory, just create the file
                filenode = self.add_file(path)
            else:
                # the parent directory should exist
                self._find_or_raise(dirpath, TYPE_DIR)
                filenode = self.add_file(path)
        else:
            filenode = filenodes[0]
        return filenode

