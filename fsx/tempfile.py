import importlib
tempfile = importlib.import_module('tempfile')

__all__ = ['NamedTemporaryFile']


NamedTemporaryFile = tempfile.NamedTemporaryFile

