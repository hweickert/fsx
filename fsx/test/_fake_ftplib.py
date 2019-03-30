import os
import ftplib
from fnmatch import fnmatch
from fstree import FsTree, TYPE_FILE, TYPE_DIR, node_matches_type
import fsx
import fsx.scandir


class Mixin(object):
    def _fake_ftplib_FTP(self, url):
        res = FakeFTP(self, url)
        return res

class FakeFTP(object):
    def __init__(self, fsx_fake, url):
        self._fsx_fake = fsx_fake
        self._url = 'ftp://'+url
        self._logged_in = False

    def storbinary(self, command, fp):
        if not self._logged_in:
            raise ftplib.error_perm('530 Please log in with USER and PASS first.')

        parts = command.split(' ', 1)
        if len(parts) == 2 and parts[0] == 'STOR':
            dst_path = _get_abs_url_path(self._url, parts[1])
            try:
                content = fp.read()
                fsx.open(dst_path, 'wb').write(content)
            except EnvironmentError as exc:
                msg = '{exc.__class__.__name__}: {exc}'.format(exc=exc)
                raise ftplib.error_perm(msg)
        else:
            raise NotImplementedError("Commands other than 'STOR' are currently not implemented.")

    def mkd(self, pathname):
        self._fsx_fake.add_dir(self._url + '/' + pathname)

    def nlst(self, argument):
        if not self._logged_in:
            raise ftplib.error_perm('530 Please log in with USER and PASS first.')

        res = []

        path = _get_abs_url_path(self._url, argument)
        for entry in fsx.scandir.scandir(path):
            res.append(entry.name)

        return res

    def retrbinary(self, argument, callback):
        if not self._logged_in:
            raise ftplib.error_perm('530 Please log in with USER and PASS first.')

        parts = argument.split(' ', 1)
        if len(parts) == 2 and parts[0] == 'RETR':
            path = _get_abs_url_path(self._url, parts[1])
            try:
                with fsx.open(path, 'rb') as file_:
                    callback(file_.read())
            except EnvironmentError as exc:
                msg = '{exc.__class__.__name__}: {exc}'.format(exc=exc)
                raise ftplib.error_perm(msg)
        else:
            raise NotImplementedError("Commands other than 'RETR' are currently not implemented.")

    def login(self, user, password):
        self._logged_in = True

    def prot_p(self):
        if not self._logged_in:
            raise AttributeError("FTP instance has no attribute 'prot_p'")

    def quit(self):
        self._logged_in = False

    def close(self):
        self._logged_in = False

def _get_abs_url_path(url, path):
    path = path.lstrip('/')
    path = url+'/'+path
    path = path.rstrip('/')
    return path
