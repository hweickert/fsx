import fsx.os
import sys
import pytest
from fsx.test import fsx_fake



def test_tracking(fsx_fake):
    fsx.os.path.exists('/tmp/file')
    with pytest.raises(RuntimeError) as raises_patch:
        fsx_fake.calls
    assert str(raises_patch.value) == 'Call tracking was not enabled. ' \
                                      'Run code with context manager ' \
                                      '`with fsx_fake.track_calls(): ...` first.'


    with fsx_fake.track_calls():
        fsx.os.path.exists('/tmp/file')
    assert fsx_fake.calls == [('os.path.exists', ('/tmp/file',), {})]


    with fsx_fake.track_calls(with_result=True):
        fsx.os.path.exists('/tmp/file')
    assert fsx_fake.calls == [('os.path.exists', ('/tmp/file',), {}, False)]


    with fsx_fake.track_calls():
        pass
    assert fsx_fake.calls == []
