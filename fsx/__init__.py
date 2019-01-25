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

def makedirs(path):
    res = os.makedirs(path)
    return res

def open(filename, mode='r', encoding=None):
    res = codecs.open(filename, mode, encoding=encoding)
    return res

def walk(top):
    # TODO: Not yet supported parameters: topdown=True, onerror=None, followlinks=False
    try:
        import scandir
        walker = scandir
    except:
        walker = os
    res = walker.walk(top)
    return res
