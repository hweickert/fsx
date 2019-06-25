import sys
import pytest
import fsx
import fsx.os
from fsx.test import fsx_fake

class Test_getcwd(object):
    @pytest.mark.parametrize(
         'fstree,                       dirpath,        expCurDir', [
       ({'X:': {'temp': {}}},          'X:/temp/',     'X:/temp'),
       ({'X:': {'temp': {'foo': {}}}}, 'X:/temp/foo/', 'X:/temp/foo'),
    ])
    def test_getcwd_has_no_trailing_backslash_after_it_was_set_with_chdir(self, fstree, dirpath, expCurDir, fsx_fake):
        fsx_fake.add_dict(fstree)
        fsx.os.chdir(dirpath)
        assert fsx.os.getcwd() == expCurDir

    @pytest.mark.parametrize(
         'fstree,              dirpath,   expCurDir', [
       ({'X:': {}},           'X:',      'X:/'),
       ({'X:': {}},           'X:/',     'X:/'),
    ])
    def test_getcwd_has_trailing_on_driveletter_paths(self, fstree, dirpath, expCurDir, fsx_fake):
        fsx_fake.add_dict(fstree)
        fsx.os.chdir(dirpath)
        assert fsx.os.getcwd() == expCurDir

class Test_os_chdir(object):
    @pytest.mark.parametrize(
         'fstree,      dirpath', [
       ({'C:': {}},   'C:'),
       ({'C:': {}},   'C:/'),
    ])
    def test_chdir_works(self, fstree, dirpath, fsx_fake):
        fsx_fake.add_dict(fstree)
        fsx.os.chdir(dirpath)

    def test_raises_error_if_dir_doesnt_exist(self, fsx_fake, monkeypatch):
        dirpath = 'X:'

        monkeypatch.setattr('sys.platform', 'win32')
        with pytest.raises(WindowsError):
            fsx.os.chdir(dirpath)

        monkeypatch.setattr('sys.platform', 'darwin')
        with pytest.raises(OSError):
            fsx.os.chdir(dirpath)

        monkeypatch.setattr('sys.platform', 'linux2')
        with pytest.raises(OSError):
            fsx.os.chdir(dirpath)


    @pytest.mark.parametrize(
       'fstree,                        dirpath', [
       ({},                           'C:'    ),
       ({'': {}},                     'C:'    ),
       ({},                           'D:'    ),
       ({'': {}},                     'D:'    ),
    ])
    def test_raises_error_if_not_existing(self, fstree, dirpath, fsx_fake, monkeypatch):
        fsx_fake.add_dict(fstree)

        monkeypatch.setattr('sys.platform', 'win32')
        with pytest.raises(WindowsError):
            fsx.os.chdir(dirpath)

        monkeypatch.setattr('sys.platform', 'darwin')
        with pytest.raises(OSError):
            fsx.os.chdir(dirpath)

        monkeypatch.setattr('sys.platform', 'linux2')
        with pytest.raises(OSError):
            fsx.os.chdir(dirpath)


# --- tests with relative working-directory ---
@pytest.mark.parametrize('path, files, dirs, type_', [
    ('a',   [],    [],      None),
])
def test_exists_with_relative_dir(path, files, dirs, type_, fsx_fake):
    map(fsx_fake.add_file, files)
    map(fsx_fake.add_dir, dirs)
    exp = type_ in ['f', 'd']
    assert exp == fsx.os.path.exists(path)


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
    assert exp == fsx.os.path.exists(path)


@pytest.mark.parametrize('fstree', [
    {},
    {'C:': {}},
    {'': {}},
])
def test_exists_returns_false_on_empty_string(fstree, fsx_fake):
    fsx_fake.add_dict(fstree)
    assert fsx.os.path.exists('') == False

@pytest.mark.parametrize('path, files, dirs, type_', TYPE_TESTS)
def test_isfile(path, files, dirs, type_, fsx_fake):
    map(fsx_fake.add_file, files)
    map(fsx_fake.add_dir, dirs)
    exp = type_ == 'f'
    assert exp == fsx.os.path.isfile(path)
    assert exp == fsx.os.path.isfile(path)

@pytest.mark.parametrize('path, files, dirs, type_', TYPE_TESTS)
def test_isdir(path, files, dirs, type_, fsx_fake):
    map(fsx_fake.add_file, files)
    map(fsx_fake.add_dir, dirs)
    exp = type_ == 'd'
    assert exp == fsx.os.path.isdir(path)

# --- listdir ---
@pytest.mark.parametrize('files, path, exp', [
    (['X:/f'],         'X:',  ['f']),
    (['X:/f'],         'X:/', ['f']),
    (['X:/f', 'X:/f2'],'X:/', ['f', 'f2']),
])
def test_listdir_works(files, path, exp, fsx_fake):
    map(fsx_fake.add_file, files)
    res = fsx.os.listdir(path)
    assert res == exp

@pytest.mark.parametrize('files, path', [
    (['X:/f'],'C:'),
    (['X:/f'],''),
    (['X:/f'],'X:/f'),
    (['X:/f'],'X:/f/d2'),
])
def test_listdir_raises_error_if_dir_doesnt_exist(files, path, fsx_fake, monkeypatch):
    monkeypatch.setattr('sys.platform', 'win32')
    with pytest.raises(WindowsError):
        fsx.os.listdir(path)

    monkeypatch.setattr('sys.platform', 'linux2')
    with pytest.raises(OSError):
        fsx.os.listdir(path)

    monkeypatch.setattr('sys.platform', 'darwin')
    with pytest.raises(OSError):
        fsx.os.listdir(path)


@property
def name(self):
    return self._name
@name.setter
def name(self, value):
    self._name = value

# --- makedirs ---
@pytest.mark.parametrize('path, exp', [
    ('/temp/foo',    {'': {'temp': {'foo': {}}}}),
    ('/temp/foo/..', {'': {'temp': {}}}),
    ('temp/foo/..',  {'temp': {}}),
])
def test_makedirs_creates_dir(path, exp, fsx_fake):
    fsx.os.makedirs(path)
    assert fsx_fake.as_dict() == exp

@pytest.mark.parametrize('path, exp', [
    ('temp/foo', {'X:': {'temp': {'foo': {}}}}),
])
def test_makedirs_creates_relative_dir_after_chdir(path, exp, fsx_fake):
    fsx.os.makedirs('X:')
    fsx.os.chdir('X:')

    fsx.os.makedirs(path)
    assert fsx_fake.as_dict() == exp

def test_makedirs_raises_error_if_dir_already_exists(fsx_fake, monkeypatch):
    path = '/temp/foo'
    fsx.os.makedirs(path)

    monkeypatch.setattr('sys.platform', 'win32')
    with pytest.raises(WindowsError):
        fsx.os.makedirs(path)

    monkeypatch.setattr('sys.platform', 'darwin')
    with pytest.raises(OSError):
        fsx.os.makedirs(path)

    monkeypatch.setattr('sys.platform', 'linux2')
    with pytest.raises(OSError):
        fsx.os.makedirs(path)

# --- walk ---
@pytest.mark.parametrize(
    'fsdict,                                   top_path, exp_roots,                exp_dir_lists,        exp_file_lists', [
    ({'C:': {}},                               'C:',     ['C:'],                      [[]                ], [[]                ]),
    ({'C:': {'d1': {}}},                       'C:',     ['C:', 'C:/d1'],             [['d1'], []        ], [[], []            ]),
    ({'C:': {'d1': {'d2': {}}}},               'C:',     ['C:', 'C:/d1', 'C:/d1/d2'], [['d1'], ['d2'], []], [[], [], []        ]),
    ({'C:': {'d1': {}, 'f1': None}},           'C:',     ['C:', 'C:/d1'],             [['d1'], []        ], [['f1'], []        ]),
    ({'C:': {'d1': {'f2': None}, 'f1': None}}, 'C:',     ['C:', 'C:/d1'],             [['d1'], [], []    ], [['f1'], ['f2'], []]),
])
def test_walk_finds_roots_dirs_and_files(fsdict, top_path, exp_roots, exp_dir_lists, exp_file_lists, fsx_fake):
    fsx_fake.add_dict(fsdict)
    gen_walk = fsx.os.walk(top_path)
    for exp_root, exp_dir_list, exp_file_list in zip(exp_roots, exp_dir_lists, exp_file_lists):
        (root, dirs, files) = next(gen_walk)
        assert root == exp_root
        assert dirs == exp_dir_list
        assert files == exp_file_list

@pytest.mark.parametrize(
    'fsdict,                                             top_path,   exp_roots,                exp_dir_lists,   exp_file_lists', [
    ({'C:': {'d1': {'f2': None}, 'f1': None}},           'C:/d1',    ['C:/d1'],                [[]],            [['f2']]),
    ({'C:': {'d1': {'d2': {}}, 'f1': None}},             'C:/d1',    ['C:/d1',    'C:/d1/d2'], [['d2'], []],    [[], []]),
    ({'C:': {'d1': {'d2': {}, 'f2': None}, 'f1': None}}, 'C:/d1',    ['C:/d1',    'C:/d1/d2'], [['d2'], []],    [['f2'], []]),
    ({'C:': {'d1': {'d2': {}, 'f2': None}, 'f1': None}}, 'C:/d1/d2', ['C:/d1/d2'],             [[]],            [[]]),
])
def test_walk_on_path_below_first_node_works(fsdict, top_path, exp_roots, exp_dir_lists, exp_file_lists, fsx_fake):
    fsx_fake.add_dict(fsdict)
    gen_walk = fsx.os.walk(top_path)
    for exp_root, exp_dir_list, exp_file_list in zip(exp_roots, exp_dir_lists, exp_file_lists):
        (root, dirs, files) = next(gen_walk)
        assert root == exp_root
        assert dirs == exp_dir_list
        assert files == exp_file_list

def test_rmdir_removes_dir(fsx_fake):
    fsx_fake.add_dict({'temp': {}})
    fsx.os.rmdir('temp')
    assert fsx_fake.as_dict() == {}

def test_rmdir_removes_subdir(fsx_fake):
    fsx_fake.add_dict({'temp/subd': {}})
    fsx.os.rmdir('temp/subd')
    assert fsx_fake.as_dict() == {'temp': {}}

def test_rmdir_raises_if_subdir_exists(fsx_fake):
    fsx_fake.add_dict({'temp/subd': {}})
    with pytest.raises((WindowsError, IOError)):
        fsx.os.rmdir('temp')

def test_rmdir_raises_if_subfile_exists(fsx_fake):
    fsx_fake.add_dict({'temp/subd': None})
    with pytest.raises((WindowsError, IOError)):
        fsx.os.rmdir('temp')

# --- remove ---
def test_remove_removes_file(fsx_fake, monkeypatch):
    file_path = '/tmp/file'
    fsx_fake.add_file(file_path)

    assert fsx.os.path.exists(file_path) is True
    fsx.os.remove(file_path)
    assert fsx.os.path.exists(file_path) is False
    assert fsx.os.path.isfile(file_path) is False

def test_remove_raises_error_if_file_doesnt_exist(fsx_fake, monkeypatch):
    file_path = '/tmp/file'

    monkeypatch.setattr('sys.platform', 'win32')
    with pytest.raises(WindowsError):
        fsx.os.remove(file_path)

    monkeypatch.setattr('sys.platform', 'linux2')
    with pytest.raises(OSError):
        fsx.os.remove(file_path)

    monkeypatch.setattr('sys.platform', 'darwin')
    with pytest.raises(OSError):
        fsx.os.remove(file_path)

def test_remove_raises_error_if_file_is_directory(fsx_fake, monkeypatch):
    fsx_fake.add_dir('/tmp/file')

    path = '/tmp/file'
    monkeypatch.setattr('sys.platform', 'win32')
    with pytest.raises(WindowsError) as exc:
        fsx.os.remove(path)

    monkeypatch.setattr('sys.platform', 'linux2')
    with pytest.raises(OSError):
        fsx.os.remove(path)

    monkeypatch.setattr('sys.platform', 'darwin')
    with pytest.raises(OSError):
        fsx.os.remove(path)
