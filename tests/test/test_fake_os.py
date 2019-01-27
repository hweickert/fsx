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
    # TODO: split into 2 tests executable on all OSes
    if sys.platform == 'win32':
        with pytest.raises(WindowsError):
            fsx.listdir(path)
    else:
        with pytest.raises(OSError):
            fsx.listdir(path)

# --- makedirs ---
@pytest.mark.parametrize('path, exp', [
    ('/temp/foo', {'': {'temp': {'foo': {}}}}),
])
def test_makedirs_creates_dir(path, exp, fsx_fake):
    fsx.makedirs(path)
    assert fsx_fake.as_dict() == exp

def test_makedirs_raises_error_if_dir_already_exists(fsx_fake):
    path = '/temp/foo'
    fsx.makedirs(path)

    # TODO: split into 2 tests executable on all OSes
    if sys.platform == 'win32':
        with pytest.raises(WindowsError):
            fsx.makedirs(path)
    else:
        with pytest.raises(OSError):
            fsx.makedirs(path)

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
    gen_walk = fsx.walk(top_path)
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
    gen_walk = fsx.walk(top_path)
    for exp_root, exp_dir_list, exp_file_list in zip(exp_roots, exp_dir_lists, exp_file_lists):
        (root, dirs, files) = next(gen_walk)
        assert root == exp_root
        assert dirs == exp_dir_list
        assert files == exp_file_list

def test_rmdir_removes_dir(fsx_fake):
    fsx_fake.add_dict({'temp': {}})
    fsx.rmdir('temp')
    assert fsx_fake.as_dict() == {}

def test_rmdir_removes_subdir(fsx_fake):
    fsx_fake.add_dict({'temp/subd': {}})
    fsx.rmdir('temp/subd')
    assert fsx_fake.as_dict() == {'temp': {}}

def test_rmdir_raises_if_subdir_exists(fsx_fake):
    fsx_fake.add_dict({'temp/subd': {}})
    with pytest.raises((WindowsError, IOError)):
        fsx.rmdir('temp')

def test_rmdir_raises_if_subfile_exists(fsx_fake):
    fsx_fake.add_dict({'temp/subd': None})
    with pytest.raises((WindowsError, IOError)):
        fsx.rmdir('temp')

