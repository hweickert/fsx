import importlib
zipfile = importlib.import_module('zipfile')

__all__ = ['ZipFile']


ZipFile = zipfile.ZipFile
