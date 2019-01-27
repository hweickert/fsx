import sys
import functools


def env_error_to_os_specific(func):
    @functools.wraps(func)
    def res(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except EnvironmentError as exc:
            msg = u'{exc}'.format(exc=exc)
            if sys.platform == 'win32':
                raise WindowsError(msg)
            else:
                raise OSError(msg)
    return res


