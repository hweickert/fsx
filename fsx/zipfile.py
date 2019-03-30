import importlib
zipfile = importlib.import_module('zipfile')

__all__ = ["BadZipfile", "error", "ZIP_STORED", "ZIP_DEFLATED", "is_zipfile",
           "ZipInfo", "ZipFile", "PyZipFile", "LargeZipFile" ]

BadZipfile = zipfile.BadZipfile
error = zipfile.error
ZIP_STORED = zipfile.ZIP_STORED
ZIP_DEFLATED = zipfile.ZIP_DEFLATED
is_zipfile = zipfile.is_zipfile
ZipInfo = zipfile.ZipInfo
ZipFile = zipfile.ZipFile
PyZipFile = zipfile.PyZipFile
LargeZipFile = zipfile.LargeZipFile
