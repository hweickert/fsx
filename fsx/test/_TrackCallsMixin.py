import contextlib
import functools



class TrackCallsMixin(object):
    def __init__(self):
        self.__do_track_calls = False
        self.__track_calls_with_result = False
        self.__calls = None

    @contextlib.contextmanager
    def track_calls(self, with_result=False):
        if self.__calls is None:
            self.__install_call_tracking()
            self._monkeypatch_fsx_funcs()

        self.__calls = []
        self.__do_track_calls = True
        self.__track_calls_with_result = with_result
        try:
            yield
        finally:
            self.__do_track_calls = False
            self.__track_calls_with_result = False

    @property
    def calls(self):
        if self.__calls is None:
            raise RuntimeError('Call tracking was not enabled. Run code with context manager `with fsx_fake.track_calls(): ...` first.')
        return list(self.__calls)

    def _wrap_in_track_calls(self, func):
        @functools.wraps(func)
        def wrapper(*a, **kwa):
            res = func(*a, **kwa)
            if self.__do_track_calls:
                orig_func_name = func.__name__.replace('_fake_', '') \
                                              .replace('_', '.')
                if self.__track_calls_with_result:
                    call_tuple = (orig_func_name, a, kwa, res)
                else:
                    call_tuple = (orig_func_name, a, kwa)
                self.__calls.append(call_tuple)
            return res
        return wrapper

    def __install_call_tracking(self):
        for attrOrMethodName in dir(self):
            if not attrOrMethodName.startswith('_fake_'):
                continue
            attrOrMethod = getattr(self, attrOrMethodName)
            if callable(attrOrMethod):
                wrappedMethod = self._wrap_in_track_calls(attrOrMethod)
                setattr(self, attrOrMethodName, wrappedMethod)
