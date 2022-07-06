from NowKwLang.constants import MISSING


class While:
    """
    A while loop
    syntax:
    while{condition}{...}    -> execute ... while condition, returning the list of the funcs results
    """
    def __init__(self, test, *, yielding=False, do_cache=True):
        if not callable(test):
            raise TypeError("test must be callable")
        self.test = test
        self.yielding = yielding
        self.do_cache = do_cache

    def __inject_code__(self, func=None):
        if func is None:
            return While(self)
        else:
            __traceback_show__ = False
            func.__scope_factory__ = lambda scope: scope

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
    """
    A for loop
    syntax:
    for("varname", iterable){...}    -> execute ... with varname equal to each value of iterable, returning the list of the funcs results
    for(iterable){varname>>>...}     -> equivalent
    for(..., do_cache=False){...}    -> don't cache func results, to optimise memory
    set(for(..., yielding=True){...})-> create a generator, can be used to create custom collections for example
    """
    def __init__(self, target_name: str, iterable=MISSING, *, yielding=False, do_cache=True):
        if iterable is MISSING:
            target_name, iterable = None, target_name
        if not (isinstance(target_name, str) or target_name is None):
            raise TypeError("target_name must be a string or None")
        self.target_name = target_name
        self.iterable = iterable
        self.yielding = yielding
        self.do_cache = do_cache

    def __inject_code__(self, func=None):
        if func is None:
            raise TypeError("You need to do for(<varname=None>, iterable){...}")
        else:
            func.__scope_factory__ = lambda scope: scope
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
