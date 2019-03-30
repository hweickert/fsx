import sys
import pytest
import fsx
from fsx.test import fsx_fake


def test_open_read_works_on_fake_files_which_received_content(fsx_fake):
    fsx_fake.add_file('f', content='test')
    res = fsx.open('f', 'r').read()
    assert res == 'test'

def test_open_read_works_on_fake_files_which_didnt_receive_content(fsx_fake):
    fsx_fake.add_file('f')
    res = fsx.open('f', 'r').read()
    assert res == ''

def test_open_read_raises_if_not_existing(fsx_fake):
    # TODO: split into 2 tests executable on all OSes
    if sys.platform == 'win32':
        with pytest.raises(WindowsError):
            fsx.open('doesnt-exist', 'r').read()
    else:
        with pytest.raises(OSError):
            fsx.open('doesnt-exist', 'r').read()

def test_open_write_creates_file(fsx_fake):
    text = 'test'
    fsx.open('f', 'w').write(text)
    assert fsx.exists('f') == True

def test_open_write_can_be_read_again(fsx_fake):
    text = 'test'
    fsx.open('f', 'w').write(text)
    res = fsx.open('f', 'r').read()
    assert res == text

def test_open_write_raises_error_if_parent_directory_doesnt_exist(fsx_fake, monkeypatch):
    monkeypatch.setattr('sys.platform', 'win32')
    with pytest.raises(WindowsError):
        fsx.open('d/f', 'w').write('test')

def test_open_append_raises_error_if_parent_directory_doesnt_exist(fsx_fake, monkeypatch):
    monkeypatch.setattr('sys.platform', 'win32')
    with pytest.raises(WindowsError):
        fsx.open('d/f', 'a').write('test')


def test_open_append_works(fsx_fake):
    fsx_fake.add_file('f', '1')
    fsx.open('f', 'a').write('23')
    res = fsx.open('f', 'r').read()
    assert res == '123'

def test_open_append_raises_error_if_parentnode_doesnt_exist(fsx_fake):
    # TODO: split into 2 tests executable on all OSes
    if sys.platform == 'win32':
        with pytest.raises(WindowsError):
            fsx.open('p/f', 'a')
    else:
        with pytest.raises(OSError):
            fsx.open('p/f', 'a')

def test_open_write_as_ctxmgr_works(fsx_fake):
    text = 'test'

    with fsx.open('f', 'w') as file_:
        file_.write('123')

    with fsx.open('f', 'r') as file_:
        res = file_.read()

    assert res == '123'

def test_open_append_as_ctxmgr_works(fsx_fake):
    fsx_fake.add_file('f', '1')

    with fsx.open('f', 'a') as file_:
        file_.write('23')

    with fsx.open('f', 'r') as file_:
        res = file_.read()

    assert res == '123'

