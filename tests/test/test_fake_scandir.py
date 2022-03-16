import pytest
import six
import fsx
import fsx.scandir
from fsx.test import fsx_fake



def test_scandir(fsx_fake):
    with pytest.raises((OSError, WindowsError)):
        next(fsx.scandir.scandir('X:/non-existing'))

    fsx_fake.add_dict({'C:/some/path.txt': 'foo'})
    entry = next(fsx.scandir.scandir('C:/some'))

    size = entry.stat().st_size
    assert size == 3

@pytest.mark.parametrize(
    'fsdict,                                   top_path, exp_entries', [
    ({'C:': {}},                               'C:',     []),
    ({'C:': {'d1': {}}},                       'C:',     ['d1/']),
    ({'C:': {'d1': {'d2': {}}}},               'C:',     ['d1/']),
    ({'C:': {'d1': {}, 'f1': None}},           'C:',     ['d1/', 'f1']),
    ({'C:': {'d1': {'f2': None}, 'f1': None}}, 'C:',     ['d1/', 'f1']),
])
def test_scandir_basic(fsdict, top_path, exp_entries, fsx_fake):
    fsx_fake.add_dict(fsdict)
    walk_entries = set(fsx.scandir.scandir(top_path))
    we_names = {we.name for we in walk_entries}
    exp_entries_names = {exp_entry.rstrip('/') for exp_entry in exp_entries}

    for we in walk_entries:
        if we.is_dir():
            assert we.name + '/' in exp_entries
        elif we.is_file():
            assert we.name in exp_entries
    assert we_names == exp_entries_names

@pytest.mark.parametrize(
    'fsdict,                                   top_path, exp_entries', [
    ({'C:': {'d1': {}}},                       'C:/d1',  []),
    ({'C:': {'d1': {'d2': {}}}},               'C:/d1',  ['d2/']),
    ({'C:': {'d1': {}, 'f1': None}},           'C:/d1',  []),
    ({'C:': {'d1': {'f2': None}, 'f1': None}}, 'C:/d1',  ['f2']),
])
def test_scandir_below_top_level_works(fsdict, top_path, exp_entries, fsx_fake):
    fsx_fake.add_dict(fsdict)
    gen_walk = fsx.scandir.scandir(top_path)
    for exp_entry in exp_entries:
        entry = next(gen_walk)
        assert entry.name == exp_entry.rstrip('/')
        assert entry.is_dir() == exp_entry.endswith('/')
        assert entry.is_file() != exp_entry.endswith('/')
