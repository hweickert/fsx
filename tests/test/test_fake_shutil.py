import sys
import pytest
import fsx
import fsx.shutil
from fsx.test import fsx_fake

class Test_rmtree(object):
    @pytest.mark.parametrize(
        'fstree,' \
        'dirpath,'\
        'expTreeDict', [
        (
            {'X:': {'a': {'b': {}}}},
            'X:/a/b',
            {'X:': {'a': {}}}
        ),
        (
            {'X:': {'a': {'b': {'file': 'test'}}}},
            'X:/a',
            {'X:': {}}
        ),
    ])
    def test_removes_directory_and_nodes_underneath(self,
        fstree,
        dirpath,
        expTreeDict,
        fsx_fake,
    ):
        fsx_fake.add_dict(fstree)
        fsx.shutil.rmtree(dirpath)

        res = fsx_fake.as_dict()

        assert res == expTreeDict

    def test_onerror_parameter_works_and_silences_error(self, fsx_fake):
        fsx.shutil.rmtree('X:/test', onerror=lambda *a, **kwa: None)

    def test_raises_if_dir_does_not_exist(self, fsx_fake):
        with pytest.raises(EnvironmentError):
            fsx.shutil.rmtree('X:/test')

    def test_ignore_errors_does_not_raise_if_folder_doesnt_exist(self, fsx_fake):
        fsx.shutil.rmtree('X:/test', ignore_errors=True)
