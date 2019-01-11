from . _FsxFakeFsTree import FsxFakeFsTree

__all__ = ['FsxFakeFsTree']

try:
    import pytest
    _PYTEST_FOUND = True
except ImportError:
    _PYTEST_FOUND = False

if _PYTEST_FOUND:
    from . _fsx_fake import fsx_fake
    __all__ += ['fsx_fake']
