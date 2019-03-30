import importlib
scandir_mod = importlib.import_module('scandir')

__all__ = ["scandir", "walk"]

scandir = scandir_mod.scandir
walk = scandir_mod.walk
