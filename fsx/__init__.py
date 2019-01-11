import os
import codecs


def isfile(path):
    res = os.path.isfile(path)
    return res

def isdir(path):
    res = os.path.isdir(path)
    return res

def exists(path):
    res = os.path.exists(path)
    return res

def listdir(path):
    res = os.listdir(path)
    return res

def open(filename, mode='r', encoding=None):
    res = codecs.open(filename, mode, encoding=encoding)
    return res
