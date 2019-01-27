import sys
import pytest
from fsx.test import fsx_fake


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
