import importlib
os = importlib.import_module('os')

__all__ = ['chdir', 'getcwd', 'remove', 'stat', 'listdir', 'makedirs', 'rmdir', 'path', 'walk']

chdir = os.chdir
listdir = os.listdir
makedirs = os.makedirs
rmdir = os.rmdir
getcwd = os.getcwd
remove = os.remove
stat = os.stat

def walk(top):
    # TODO: Not yet supported parameters: topdown=True, onerror=None, followlinks=False
    try:
        walker = importlib.import_module('scandir')
    except:
        walker = os
    res = walker.walk(top)
    return res

class path:
    @staticmethod
    def isfile(path):
        res = os.path.isfile(path)
        return res

    @staticmethod
    def isdir(path):
        res = os.path.isdir(path)
        return res

    @staticmethod
    def exists(path):
        res = os.path.exists(path)
        return res

    @staticmethod
    def abspath(path):
        res = os.path.abspath(path)
        return res

    @staticmethod
    def getsize(path):
        res = os.path.getsize(path)
        return res
