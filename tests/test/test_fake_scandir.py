import pytest
import fsx
import fsx.scandir
import scandir
from fsx.test import fsx_fake


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
    gen_walk = fsx.scandir.scandir(top_path)
    for exp_entry in exp_entries:
        entry = next(gen_walk)
        assert entry.name == exp_entry.rstrip('/')
        assert entry.is_dir() == exp_entry.endswith('/')
        assert entry.is_file() != exp_entry.endswith('/')


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

@pytest.mark.parametrize(
    'fsdict,                           top_path', [
    ({'C:': {}},                       'C:/d1'),
])
def test_scandir_on_non_existing_raises(fsdict, top_path, fsx_fake):
    with pytest.raises((OSError, WindowsError)):
        next(fsx.scandir.scandir(top_path))
