import importlib
ftplib = importlib.import_module('ftplib')

__all__ = ["FTP"]

FTP = ftplib.FTP
