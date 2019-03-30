import io
import importlib
import os
import fsx
from fstree import TYPE_FILE, TYPE_DIR

zipfile = importlib.import_module('zipfile')

class FakeZipFile(zipfile.ZipFile):
    def __init__(self, fsx_fake, *a, **kwa):
        zipfile.ZipFile.__init__(self, *a, **kwa)
        self._fsx_fake = fsx_fake

    def write(self, path): #, arcname, compress_type
        if self._fsx_fake._curdir:
            path_abs = self._fsx_fake._curdir + '/' + path
            nodes = self._fsx_fake.find(path_abs, TYPE_FILE)
            if nodes:
                path = path_abs
                filenode = nodes[0]
            else:
                filenode = self._fsx_fake._find_or_raise(path, TYPE_FILE)
        else:
            filenode = self._fsx_fake._find_or_raise(path, TYPE_FILE)
        filename = path

        #filenode = self._fsx_fake._find_or_raise(filename, TYPE_FILE)
        io_obj = filenode.get_exist_io(io.BytesIO)

        if self._fsx_fake._curdir:
            commonprefix = os.path.commonprefix([filename, self._fsx_fake._curdir])
            if filename[len(commonprefix)] == '/':
                zip_filepath = filename[len(commonprefix)+1:]
            else:
                zip_filepath = _cut_drive_or_root_prefix(filename)
        else:
            zip_filepath = _cut_drive_or_root_prefix(filename)
        self.writestr(zip_filepath, io_obj.getvalue())

def _cut_drive_or_root_prefix(path):
    res = path
    res = res.lstrip('/')
    if res[1:2] == ':':
        res = res[3:]
    return res

class Mixin(object):
    def _fake_zipfile_ZipFile(self, file, mode="r", compression=zipfile.ZIP_STORED, allowZip64=False):
        path = file
        if self._flip_backslashes:
            path = path.replace('\\', '/')

        if mode.startswith('r'):
            if self._curdir:
                path_abs = self._curdir + '/' + path
                nodes = self.find(path_abs, TYPE_FILE)
                if nodes:
                    path = path_abs
                    filenode = nodes[0]
                else:
                    filenode = self._find_or_raise(path, TYPE_FILE)
            else:
                filenode = self._find_or_raise(path, TYPE_FILE)

            io_obj = filenode.get_exist_io(io.BytesIO)
            io_obj.seek(0)

            res = FakeZipFile(self, io_obj, mode=mode, compression=compression, allowZip64=allowZip64)
            return res

        elif mode.startswith('a'):
            filenodes = self.find(path, TYPE_FILE)
            if not filenodes:
                # the file doesn't exist yet but the parent directory should.
                dirpath = os.path.dirname(path)
                self._find_or_raise(dirpath, TYPE_DIR)
                filenode = self.add_file(path)
            else:
                filenode = filenodes[0]

            io_obj = filenode.get_exist_io(io.BytesIO)

            res = FakeZipFile(self, io_obj, mode=mode, compression=compression, allowZip64=allowZip64)
            return res

        elif mode.startswith('w'):
            if path.startswith('/') or path[1:2] == ':':
                # HACK: We identify this as an absolute path.
                # We need tests for this.
                nodes = self.find(path, TYPE_FILE)
            elif self._curdir:
                path = self._curdir + '/' + path
                nodes = self.find(path, TYPE_FILE)
            else:
                nodes = self.find(path, TYPE_FILE)

            filenode = nodes[0] if nodes else self.add_file(path)
            io_obj = filenode.create_new_io(io.BytesIO)

            res = FakeZipFile(self, io_obj, mode=mode, compression=compression, allowZip64=allowZip64)
            return res

        else:
            msg = "Mode string must begin with one of 'r', 'w' or 'a', not '{}'.".format(mode)
            raise ValueError(msg)

