import pytest
import fsx
from fsx.test import fsx_fake


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

