import importlib
shutil = importlib.import_module('shutil')

__all__ = ['rmtree']

rmtree = shutil.rmtree
