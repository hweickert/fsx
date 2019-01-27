import os
import fsx
import fsx.tempfile
from fsx.test import fsx_fake



class Test_NamedTemporaryFile:
    def test_do_not_create_a_real_file(self, fsx_fake):
        file_ = fsx.tempfile.NamedTemporaryFile(delete=False)
        assert os.path.exists(file_.name) == False

        file_ = fsx.tempfile.NamedTemporaryFile()
        assert os.path.exists(file_.name) == False

    def test_name_ends_with_suffix(self, fsx_fake):
        file_ = fsx.tempfile.NamedTemporaryFile(suffix='_suf')
        assert file_.name.endswith('_suf') == True

    def test_name_basename_begins_with_prefix(self, fsx_fake):
        file_ = fsx.tempfile.NamedTemporaryFile(prefix='pref_')
        basename = os.path.basename(file_.name)
        assert basename.startswith('pref_') == True

    def test_delete_false_makes_file_persistent(self, fsx_fake):
        file_ = fsx.tempfile.NamedTemporaryFile(delete=False)
        assert fsx.exists(file_.name) == True

    def test_delete_true_makes_file_disappear_after_close(self, fsx_fake):
        file_ = fsx.tempfile.NamedTemporaryFile(delete=True)
        file_.close()
        assert fsx.exists(file_.name) == False

    def test_read_works_on_persistent_file(self, fsx_fake):
        file_ = fsx.tempfile.NamedTemporaryFile(delete=False)
        file_.write('test')
        file_.close()

        assert fsx.open(file_.name, 'r').read() == 'test'


class Test_NamedTemporaryFile_ctxmanager:
    def test_delete_true_makes_file_disappear_when_garbage_collected(self, fsx_fake):
        def scope():
            file_ = fsx.tempfile.NamedTemporaryFile(delete=True)
            return file_.name
        path = scope()
        assert fsx.exists(path) == False

    def test_delete_false_makes_file_not_disappear_when_garbage_collected(self, fsx_fake):
        def scope():
            file_ = fsx.tempfile.NamedTemporaryFile(delete=False)
            return file_.name
        path = scope()
        assert fsx.exists(path) == True

    def test_delete_true_makes_file_disappear(self, fsx_fake):
        with fsx.tempfile.NamedTemporaryFile(delete=True) as file_:
            pass
        assert fsx.exists(file_.name) == False

    def test_delete_false_makes_file_disappear(self, fsx_fake):
        with fsx.tempfile.NamedTemporaryFile(delete=False) as file_:
            pass
        assert fsx.exists(file_.name) == True

    def test_write_works(self, fsx_fake):
        with fsx.tempfile.NamedTemporaryFile() as file_:
            file_.write('test')

    def test_write_with_delete_false_can_be_read_after(self, fsx_fake):
        with fsx.tempfile.NamedTemporaryFile(delete=False) as file_:
            file_.write('test')

        assert fsx.open(file_.name, 'r').read() == 'test'

