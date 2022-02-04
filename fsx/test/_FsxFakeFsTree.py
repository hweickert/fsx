import sys
from fstree import FsTree
import fsx
import fsx.zipfile
import fsx.tempfile
import fsx.scandir
import fsx.shutil
import fsx.glob
import fsx.ftplib
from . import _fake_os
from . import _fake_builtins
from . import _fake_glob
from . import _fake_shutil
from . import _fake_tempfile
from . import _fake_zipfile
from . import _fake_ftplib
from . _helpers import env_error_to_os_specific


class FsxFakeFsTree(
    FsTree,
    _fake_builtins.Mixin,
    _fake_os.Mixin,
    _fake_glob.Mixin,
    _fake_shutil.Mixin,
    _fake_tempfile.Mixin,
    _fake_zipfile.Mixin,
    _fake_ftplib.Mixin,
):
    pass

# if sys.version_info.major < 3:
from . import _fake_scandir
class FsxFakeFsTree(
    FsxFakeFsTree,
    _fake_scandir.Mixin
):
    pass

class FsxFakeFsTree(FsxFakeFsTree):
    ''' A virtual file system tree supporting some common file system functions. '''

    def __init__(self, monkeypatch, flip_backslashes=None):
        FsTree.__init__(self, flip_backslashes=flip_backslashes)

        monkeypatch.setattr(fsx,          'open',               self._fake_builtins_open)
        monkeypatch.setattr(fsx.glob,     'iglob',              self._fake_glob_iglob)
        monkeypatch.setattr(fsx.glob,     'glob',               self._fake_glob_glob)
        monkeypatch.setattr(fsx.tempfile, 'NamedTemporaryFile', self._fake_tempfile_NamedTemporaryFile)
        monkeypatch.setattr(fsx.zipfile,  'ZipFile',            self._fake_zipfile_ZipFile)
        # if sys.version_info.major < 3:
        monkeypatch.setattr(fsx.scandir,  'scandir',            self._fake_scandir_scandir)
        monkeypatch.setattr(fsx.ftplib,   'FTP',                self._fake_ftplib_FTP)

        monkeypatch.setattr(fsx.os,       'listdir',            self._fake_os_listdir)
        monkeypatch.setattr(fsx.os,       'makedirs',           self._fake_os_makedirs)
        monkeypatch.setattr(fsx.os,       'rmdir',              self._fake_os_rmdir)
        monkeypatch.setattr(fsx.os,       'walk',               self._fake_os_walk)
        monkeypatch.setattr(fsx.os.path,  'exists',             self._fake_os_path_exists)
        monkeypatch.setattr(fsx.os.path,  'isfile',             self._fake_os_path_isfile)
        monkeypatch.setattr(fsx.os.path,  'isdir',              self._fake_os_path_isdir)
        monkeypatch.setattr(fsx.os,       'chdir',              self._fake_os_chdir)
        monkeypatch.setattr(fsx.os,       'getcwd',             self._fake_os_getcwd)
        monkeypatch.setattr(fsx.os,       'remove',             self._fake_os_remove)

        monkeypatch.setattr(fsx.shutil,   'rmtree',            self._fake_shutil_rmtree)

        # Legacy root-namespace functions, do not add new ones.
        monkeypatch.setattr(fsx,          'listdir',            self._fake_os_listdir)
        monkeypatch.setattr(fsx,          'makedirs',           self._fake_os_makedirs)
        monkeypatch.setattr(fsx,          'rmdir',              self._fake_os_rmdir)
        monkeypatch.setattr(fsx,          'walk',               self._fake_os_walk)
        monkeypatch.setattr(fsx,          'exists',             self._fake_os_path_exists)
        monkeypatch.setattr(fsx,          'isfile',             self._fake_os_path_isfile)
        monkeypatch.setattr(fsx,          'isdir',              self._fake_os_path_isdir)

    @env_error_to_os_specific
    def _find_or_raise(self, path, type_):
        return FsTree._find_or_raise(self, path, type_)

    @env_error_to_os_specific
    def _raise_not_found(self, file_path):
        return FsTree._raise_not_found(self, file_path)

