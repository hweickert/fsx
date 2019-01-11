import sys
import pytest
import fsx
from fsx.test import fsx_fake


TYPE_TESTS = [
    ('a',   [],    [],      None),
    ('a',   ['a'], [],      'f'),
    ('d',   [],    ['d'],   'd'),
    ('d/d', [],    ['d/d'], 'd'),
    ('d',   [],    ['d/d'], 'd'),
]

@pytest.mark.parametrize('path, files, dirs, type_', TYPE_TESTS)
def test_exists(path, files, dirs, type_, fsx_fake):
    map(fsx_fake.add_file, files)
    map(fsx_fake.add_dir, dirs)
    exp = type_ in ['f', 'd']
    assert exp == fsx.exists(path)

@pytest.mark.parametrize('path, files, dirs, type_', TYPE_TESTS)
def test_isfile(path, files, dirs, type_, fsx_fake):
    map(fsx_fake.add_file, files)
    map(fsx_fake.add_dir, dirs)
    exp = type_ == 'f'
    assert exp == fsx.isfile(path)

@pytest.mark.parametrize('path, files, dirs, type_', TYPE_TESTS)
def test_isdir(path, files, dirs, type_, fsx_fake):
    map(fsx_fake.add_file, files)
    map(fsx_fake.add_dir, dirs)
    exp = type_ == 'd'
    assert exp == fsx.isdir(path)


# --- glob ---
@pytest.mark.parametrize('pat, exist_files, exp', [
    ('*',     [],                    []),
    ('*',     ['a'],                 ['a']),
    ('*',     ['a', 'b'],            ['a', 'b']),
    ('*.e',   ['a'],                 []),
    ('*.e',   ['a.e'],               ['a.e']),
    ('*.e',   ['a.e', 'b.e'],        ['a.e', 'b.e']),
    ('d/*',   [],                    []),
    ('d/*',   ['d'],                 []),
    ('d/*',   ['x', 'd/a'],          ['d/a']),
    ('*/*',   ['d/a'],               ['d/a']),
    ('*/*',   ['x', 'd/a'],          ['d/a']),
    ('*/*/*', ['x', 'd/a'],          []),
    ('*/*/*', ['x', 'd/a', 'd/d/a'], ['d/d/a']),
])
def test_glob(pat, exist_files, exp, fsx_fake):
    map(fsx_fake.add_file, exist_files)
    res = fsx.glob.glob(pat)
    assert exp == res


# --- listdir ---
@pytest.mark.parametrize('files, path, exp', [
    (['X:/f'],         'X:',  ['f']),
    (['X:/f'],         'X:/', ['f']),
    (['X:/f', 'X:/f2'],'X:/', ['f', 'f2']),
])
def test_listdir_works(files, path, exp, fsx_fake):
    map(fsx_fake.add_file, files)
    res = fsx.listdir(path)
    assert res == exp

@pytest.mark.parametrize('files, path', [
    (['X:/f'],'C:'),
    (['X:/f'],''),
    (['X:/f'],'X:/f'),
    (['X:/f'],'X:/f/d2'),
])
def test_listdir_raises_ioerror_if_dir_doesnt_exist(files, path, fsx_fake):
    map(fsx_fake.add_file, files)
    with pytest.raises(IOError):
        fsx.listdir(path)


# --- open ---
def test_open_read_works_on_fake_files_which_received_content(fsx_fake):
    fsx_fake.add_file('f', content='test')
    res = fsx.open('f', 'r').read()
    assert res == 'test'

def test_open_read_works_on_fake_files_which_didnt_receive_content(fsx_fake):
    fsx_fake.add_file('f')
    res = fsx.open('f', 'r').read()
    assert res == ''

def test_open_read_raises_if_not_existing(fsx_fake):
    with pytest.raises(IOError):
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

def test_open_append_works(fsx_fake):
    fsx_fake.add_file('f', '1')
    fsx.open('f', 'a').write('23')
    res = fsx.open('f', 'r').read()
    assert res == '123'

def test_open_append_raises_error_if_parentnode_doesnt_exist(fsx_fake):
    with pytest.raises(IOError):
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

# --- Windows Compatibility ---
@pytest.mark.parametrize('dirpath, exp', [
    ('C:\\', {'C:': {}})
])
def test_add_dir_flips_fwdslashes_on_win(dirpath, exp, monkeypatch, fsx_fake):
    monkeypatch.setattr(sys, 'platform', 'win32')

    fsx_fake.add_dir(dirpath)
    assert fsx_fake.as_dict() == exp

@pytest.mark.parametrize('filepath, exp', [
    (r'C:\f', {'C:': {'f': None}}),
])
def test_add_file_flips_fwdslashes_on_win(filepath, exp, monkeypatch, fsx_fake):
    monkeypatch.setattr(sys, 'platform', 'win32')

    fsx_fake.add_file(filepath)
    assert fsx_fake.as_dict() == exp
