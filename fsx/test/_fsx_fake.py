import pytest
from . _FsxFakeFsTree import FsxFakeFsTree


@pytest.fixture
def fsx_fake(monkeypatch):
    res = FsxFakeFsTree(monkeypatch)
    yield res
