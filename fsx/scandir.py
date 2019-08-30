import importlib
try:
    scandir_mod = importlib.import_module('scandir')
except ModuleNotFoundError:
    # py3
    import os
    scandir_mod = os

__all__ = ["scandir", "walk"]

scandir = scandir_mod.scandir
walk = scandir_mod.walk
