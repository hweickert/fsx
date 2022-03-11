#!/usr/bin/env python310
import io
import importlib

# Exports for backwards-compatibility (please use `fsx.os` instead):
from .os import path, listdir, makedirs, rmdir, walk

isfile = path.isfile
isdir = path.isdir
exists = path.exists

__all__ = [
    # Exports for backwards-compatibility (please use `fsx.os` instead):
    'isfile', 'isdir', 'exists',
    'listdir', 'makedirs', 'rmdir', 'walk'

    # Builtins:
    'open',
]

def open(filename, mode='r', encoding=None, newline=None):
    res = io.open(filename, mode, encoding=encoding, newline=newline)
    return res
