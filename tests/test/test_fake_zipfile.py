import sys
import zipfile
import io
import pytest
import fsx
import fsx.zipfile
from fsx.test import fsx_fake


def test_ZipFile_read_works_on_fake_files_which_received_content(fsx_fake):
    io_obj = io.BytesIO()
    with zipfile.ZipFile(io_obj, 'w') as file_:
        file_.writestr('f.txt', 'foo')
    zipcontent = io_obj.getvalue()

    fsx_fake.add_file('arch.zip', content=zipcontent)
    res = fsx.zipfile.ZipFile('arch.zip', 'r').read('f.txt')
    assert res == 'foo'

def test_ZipFile_read_works_on_fake_files_received_an_empty_archive_as_content(fsx_fake):
    io_obj = io.BytesIO()
    zipfile.ZipFile(io_obj, 'w').close()
    zipcontent = io_obj.getvalue()

    fsx_fake.add_file('arch.zip', zipcontent)
    res = fsx.open('arch.zip', 'r').read()
    assert res == zipcontent

def test_ZipFile_read_raises_if_not_existing(fsx_fake):
    # TODO: split into 2 tests executable on all OSes
    if sys.platform == 'win32':
        with pytest.raises(WindowsError):
            fsx.zipfile.ZipFile('doesnt-exist', 'r').read()
    else:
        with pytest.raises(OSError):
            fsx.zipfile.ZipFile('doesnt-exist', 'r').read()

def test_ZipFile_write_creates_file(fsx_fake):
    fsx.zipfile.ZipFile('arch.zip', 'w').writestr('f', 'test')
    assert fsx.exists('arch.zip') == True

def test_ZipFile_write_can_be_read_again(fsx_fake):
    text = 'test'
    fsx.zipfile.ZipFile('arch.zip', 'w').writestr('f', text)
    res = fsx.zipfile.ZipFile('arch.zip', 'r').read('f')
    assert res == text

def test_ZipFile_append_adds_new_files_inside_archive(fsx_fake):
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

def test_ZipFile_append_raises_error_if_parentnode_doesnt_exist(fsx_fake):
    # TODO: split into 2 tests executable on all OSes
    if sys.platform == 'win32':
        with pytest.raises(WindowsError):
            fsx.zipfile.ZipFile('p/arch.zip', 'a')
    else:
        with pytest.raises(OSError):
            fsx.zipfile.ZipFile('p/arch.zip', 'a')

def test_ZipFile_write_as_ctxmgr_works(fsx_fake):
    with fsx.zipfile.ZipFile('arch.zip', 'w') as file_:
        file_.writestr('f', '123')

    with fsx.zipfile.ZipFile('arch.zip', 'r') as file_:
        res = file_.read('f')

    assert res == '123'

def test_ZipFile_append_as_ctxmgr_works(fsx_fake):
    io_obj = io.BytesIO()
    zipfile.ZipFile(io_obj, 'w').writestr('f1', 'foo')
    zipcontent = io_obj.getvalue()

    fsx_fake.add_file('arch.zip', zipcontent)

    with fsx.zipfile.ZipFile('arch.zip', 'a') as file_:
        file_.writestr('f2', 'bar')

    with fsx.zipfile.ZipFile('arch.zip', 'r') as file_:
        assert file_.read('f1') == 'foo'
        assert file_.read('f2') == 'bar'
