from __future__ import print_function
import sys
import zipfile
import io
import pytest
import os
import fsx
import fsx.os
import fsx.zipfile
from fsx.test import fsx_fake


class Test_ZipFile_write(object):
    @pytest.mark.parametrize(
         'curdir,       zipArchivePath,  memberFilePath,         expArchivePaths,                      expZipMemberName', [
        ('',           'arch.zip',      'file.txt',             ['arch.zip', '/arch.zip'],            'file.txt',          ),
        ('',           'arch.zip',      '/temp/file.txt',       [],                                   'temp/file.txt',     ),
        ('',           'arch.zip',      'C:/temp/file.txt',     [],                                   'temp/file.txt',     ),

        ('',           'arch.zip',      'C:/temp/file.txt',     ['arch.zip', '/arch.zip'],             'temp/file.txt',    ),
        ('C:/temp',    'arch.zip',      'C:/temp/file.txt',     ['C:/temp/arch.zip'],                  'file.txt',         ),
        ('C:/temp',    'arch.zip',      'C:/temp2/file.txt',    ['C:/temp/arch.zip'],                  'temp2/file.txt',   ),
        ('C:/temp',    'arch.zip',      'C:/temp123/file.txt',  ['C:/temp/arch.zip'],                  'temp123/file.txt', ),
        ('C:/d1',      'arch.zip',      'C:/d2/d3/file.txt',    ['C:/d1/arch.zip'],                    'd2/d3/file.txt',   ),

        ('C:',         'arch.zip',      'C:/temp/file.txt',     ['C:/arch.zip'],                       'temp/file.txt',    ),
        ('C:/',        'arch.zip',      'C:/temp/file.txt',     ['C:/arch.zip'],                       'temp/file.txt',    ),
        ('D:/test',    'arch.zip',      'C:/temp/file.txt',     ['D:/test/arch.zip'],                  'temp/file.txt',    ),
        ('C:/temp',    'arch.zip',      'C:/temp/file.txt',     ['C:/temp/arch.zip'],                  'file.txt',         ),
        ('C:/temp/d2', 'arch.zip',      'C:/temp/file.txt',     ['C:/temp/d2/arch.zip'],               'temp/file.txt',    ),

        ('/',          'arch.zip',      '/temp/file.txt',       ['arch.zip', '/arch.zip'],             'temp/file.txt',    ),
        ('/',          'temp/arch.zip', '/temp/file.txt',       ['temp/arch.zip', '/temp/arch.zip'],   'temp/file.txt',    ),
        ('/temp',      'arch.zip',      '/temp/file.txt',       ['arch.zip', '/temp/arch.zip'],        'file.txt',         ),

        ('/temp',      'arch.zip',      'file.txt',             ['arch.zip', '/temp/arch.zip'],        'file.txt',         ),
        ('/temp',      'arch.zip',      '/temp/subdir/file.txt',['arch.zip', '/temp/arch.zip'],        'subdir/file.txt',  ),
    ])
    def test_ZipFile_write_creates_file_which_can_be_read(self, curdir, zipArchivePath, memberFilePath, expArchivePaths, expZipMemberName, fsx_fake):
        fsx_fake.add_dir(curdir)
        fsx_fake.add_file(memberFilePath, 'file-content')

        fsx.os.chdir(curdir)
        with fsx.zipfile.ZipFile(zipArchivePath, 'w') as file_:
            file_.write(memberFilePath)

        with fsx.zipfile.ZipFile(zipArchivePath, 'r') as file_:
            assert file_.namelist() == [expZipMemberName]
            assert file_.read(expZipMemberName) == 'file-content'

        for expArchivePath in expArchivePaths:
            assert fsx.os.path.exists(expArchivePath) == True

class Test_ZipFile_read(object):
    def test_ZipFile_read_works_on_fake_files_which_received_content(self, fsx_fake):
        io_obj = io.BytesIO()
        with zipfile.ZipFile(io_obj, 'w') as file_:
            file_.writestr('f.txt', 'foo')
        zipcontent = io_obj.getvalue()

        fsx_fake.add_file('arch.zip', content=zipcontent)
        res = fsx.zipfile.ZipFile('arch.zip', 'r').read('f.txt')
        assert res == 'foo'

    def test_ZipFile_read_works_on_fake_files_received_an_empty_archive_as_content(self, fsx_fake):
        io_obj = io.BytesIO()
        zipfile.ZipFile(io_obj, 'w').close()
        zipcontent = io_obj.getvalue()

        fsx_fake.add_file('arch.zip', zipcontent)
        res = fsx.open('arch.zip', 'r').read()
        assert res == zipcontent

    def test_ZipFile_read_raises_if_not_existing(self, fsx_fake):
        # TODO: split into 2 tests executable on all OSes
        if sys.platform == 'win32':
            with pytest.raises(WindowsError):
                fsx.zipfile.ZipFile('doesnt-exist', 'r').read()
        else:
            with pytest.raises(OSError):
                fsx.zipfile.ZipFile('doesnt-exist', 'r').read()

class Test_ZipFile_writestr(object):
    def test_ZipFile_writestr_creates_file(self, fsx_fake):
        fsx.zipfile.ZipFile('arch.zip', 'w').writestr('f', 'test')
        assert fsx.exists('arch.zip') == True

    def test_ZipFile_writestr_can_be_read_again(self, fsx_fake):
        text = 'test'
        fsx.zipfile.ZipFile('arch.zip', 'w').writestr('f', text)
        res = fsx.zipfile.ZipFile('arch.zip', 'r').read('f')
        assert res == text

    def test_ZipFile_writestr_as_ctxmgr_works(self, fsx_fake):
        with fsx.zipfile.ZipFile('arch.zip', 'w') as file_:
            file_.writestr('f', '123')

        with fsx.zipfile.ZipFile('arch.zip', 'r') as file_:
            res = file_.read('f')

        assert res == '123'

    def test_ZipFile_append_as_ctxmgr_works(self, fsx_fake):
        io_obj = io.BytesIO()
        zipfile.ZipFile(io_obj, 'w').writestr('f1', 'foo')
        zipcontent = io_obj.getvalue()

        fsx_fake.add_file('arch.zip', zipcontent)

        with fsx.zipfile.ZipFile('arch.zip', 'a') as file_:
            file_.writestr('f2', 'bar')

        with fsx.zipfile.ZipFile('arch.zip', 'r') as file_:
            assert file_.read('f1') == 'foo'
            assert file_.read('f2') == 'bar'

    def test_ZipFile_append_adds_new_files_inside_archive(self, fsx_fake):
        io_obj = io.BytesIO()
        zipfile.ZipFile(io_obj, 'w').writestr('f1', 'foo')
        zipcontent = io_obj.getvalue()

        fsx_fake.add_file('arch.zip', zipcontent)

        with fsx.zipfile.ZipFile('arch.zip', 'a') as file_:
            file_.writestr('f2', 'bar')
            file_.writestr('f3', 'spam')

        assert fsx.zipfile.ZipFile('arch.zip', 'r').read('f1') == 'foo'
        assert fsx.zipfile.ZipFile('arch.zip', 'r').read('f2') == 'bar'
        assert fsx.zipfile.ZipFile('arch.zip', 'r').read('f3') == 'spam'


class Test_ZipFile_append_mode:
    def test_ZipFile_append_raises_error_if_parentnode_doesnt_exist(self, fsx_fake):
        # TODO: split into 2 tests executable on all OSes
        if sys.platform == 'win32':
            with pytest.raises(WindowsError):
                fsx.zipfile.ZipFile('p/arch.zip', 'a')
        else:
            with pytest.raises(OSError):
                fsx.zipfile.ZipFile('p/arch.zip', 'a')

