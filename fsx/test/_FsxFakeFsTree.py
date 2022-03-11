import contextlib
import functools
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
from . _TrackCallsMixin import TrackCallsMixin



class FsxFakeFsTree(
    FsTree,
    _fake_builtins.Mixin,
    _fake_os.Mixin,
    _fake_glob.Mixin,
    _fake_shutil.Mixin,
    _fake_tempfile.Mixin,
    _fake_zipfile.Mixin,
    _fake_ftplib.Mixin,
    TrackCallsMixin,
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
        TrackCallsMixin.__init__(self)

        self._monkeypatch = monkeypatch
        self._monkeypatch_fsx_funcs()

    def _monkeypatch_fsx_funcs(self):
        self._monkeypatch.setattr(fsx,          'open',               self._fake_builtins_open)
        self._monkeypatch.setattr(fsx.glob,     'iglob',              self._fake_glob_iglob)
        self._monkeypatch.setattr(fsx.glob,     'glob',               self._fake_glob_glob)
        self._monkeypatch.setattr(fsx.tempfile, 'NamedTemporaryFile', self._fake_tempfile_NamedTemporaryFile)
        self._monkeypatch.setattr(fsx.zipfile,  'ZipFile',            self._fake_zipfile_ZipFile)
        # if sys.version_info.major < 3:
        self._monkeypatch.setattr(fsx.scandir,  'scandir',            self._fake_scandir_scandir)
        self._monkeypatch.setattr(fsx.ftplib,   'FTP',                self._fake_ftplib_FTP)

        self._monkeypatch.setattr(fsx.os,       'listdir',            self._fake_os_listdir)
        self._monkeypatch.setattr(fsx.os,       'makedirs',           self._fake_os_makedirs)
        self._monkeypatch.setattr(fsx.os,       'rmdir',              self._fake_os_rmdir)
        self._monkeypatch.setattr(fsx.os,       'walk',               self._fake_os_walk)
        self._monkeypatch.setattr(fsx.os.path,  'exists',             self._fake_os_path_exists)
        self._monkeypatch.setattr(fsx.os.path,  'getsize',            self._fake_os_path_getsize)
        self._monkeypatch.setattr(fsx.os.path,  'isfile',             self._fake_os_path_isfile)
        self._monkeypatch.setattr(fsx.os.path,  'isdir',              self._fake_os_path_isdir)
        self._monkeypatch.setattr(fsx.os,       'chdir',              self._fake_os_chdir)
        self._monkeypatch.setattr(fsx.os,       'getcwd',             self._fake_os_getcwd)
        self._monkeypatch.setattr(fsx.os,       'remove',             self._fake_os_remove)
        self._monkeypatch.setattr(fsx.os,       'stat',               self._fake_os_stat)

        self._monkeypatch.setattr(fsx.shutil,   'rmtree',            self._fake_shutil_rmtree)

        # Legacy root-namespace functions, do not add new ones.
        self._monkeypatch.setattr(fsx,          'listdir',            self._fake_os_listdir)
        self._monkeypatch.setattr(fsx,          'makedirs',           self._fake_os_makedirs)
        self._monkeypatch.setattr(fsx,          'rmdir',              self._fake_os_rmdir)
        self._monkeypatch.setattr(fsx,          'walk',               self._fake_os_walk)
        self._monkeypatch.setattr(fsx,          'exists',             self._fake_os_path_exists)
        self._monkeypatch.setattr(fsx,          'isfile',             self._fake_os_path_isfile)
        self._monkeypatch.setattr(fsx,          'isdir',              self._fake_os_path_isdir)

    @env_error_to_os_specific
    def _find_or_raise(self, path, type_):
        return FsTree._find_or_raise(self, path, type_)

    @env_error_to_os_specific
    def _raise_not_found(self, file_path):
        return FsTree._raise_not_found(self, file_path)

