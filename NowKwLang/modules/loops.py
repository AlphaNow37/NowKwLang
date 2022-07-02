from NowKwLang.constants import MISSING


class While:
    def __init__(self, test, *, yielding=False, do_cache=True):
        if not callable(test):
            raise TypeError("test must be callable")
        if yielding and not do_cache:
            raise ValueError("You can't yield without caching")
        self.test = test
        self.yielding = yielding
        self.do_cache = do_cache

    def __inject_code__(self, func=None):
        if func is None:
            return While(self)
        else:
            __traceback_show__ = False
            func.__create_scope__ = False

            if self.yielding:
                return self._yields(func)
            elif self.do_cache:
                cache = []
                while self.test():
                    cache.append(func())
                return cache
            else:
                while self.test():
                    func()

    def _yields(self, func):
        __traceback_show__ = False
        while self.test():
            yield func()


class For:
    def __init__(self, target_name: str, iterable=MISSING, *, yielding=False, do_cache=True):
        if iterable is MISSING:
            target_name, iterable = None, target_name
        if not (isinstance(target_name, str) or target_name is None):
            raise TypeError("target_name must be a string or None")
        if yielding and not do_cache:
            raise ValueError("You can't yield without caching")
        self.target_name = target_name
        self.iterable = iterable
        self.yielding = yielding
        self.do_cache = do_cache

    def __inject_code__(self, func=None):
        if func is None:
            raise TypeError("You need to do for(<varname=None>, iterable){...}")
        else:
            func.__create_scope__ = False
            __traceback_show__ = False
            if self.yielding:
                return self._yields(func)
            elif self.do_cache:
                if self.target_name is None:
                    return [func(value) for value in self.iterable]
                else:
                    return [func(**{self.target_name: value}) for value in self.iterable]
            else:
                if self.target_name is None:
                    for value in self.iterable:
                        func(value)
                else:
                    for value in self.iterable:
                        func(**{self.target_name: value})

    def _yields(self, func):
        __traceback_show__ = False
        if self.target_name is None:
            yield from (func(value) for value in self.iterable)
        else:
            yield from (func(**{self.target_name: value}) for value in self.iterable)
