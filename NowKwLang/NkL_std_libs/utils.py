from NowKwLang.constants import MISSING

from functools import reduce as _base_reduce
_base_map = map
_base_filter = filter


class map:
    """
    map(iterable){value>>>...}{value>>>...} ... -> create an iterable that transform values
    """
    def __init__(self, iterable, func=None):
        self.iterable = iterable
        self.func = func

    def __iter__(self):
        if self.func is None:
            return iter(self.iterable)
        else:
            return iter(_base_map(self.func, self.iterable))

    def __getitem__(self, key):
        if self.func is None:
            return self.iterable[key]
        else:
            return self.func(self.iterable[key])

    def __len__(self):
        return len(self.iterable)

    def __inject_code__(self, func):
        if self.func is None:
            self.func = func
            return self
        else:
            return map(self, func)

class filter:
    """
    filter(iterable){value>>>...}{value>>>...} ... -> create an iterable that filter values
    """
    def __init__(self, iterable, func=None):
        self.iterable = iterable
        self.func = func

    def __iter__(self):
        if self.func is None:
            return iter(self.iterable)
        else:
            return iter(_base_filter(self.func, self.iterable))

    def __getitem__(self, key):
        if self.func is None:
            return True
        else:
            return self.func(self.iterable[key])

    def __inject_code__(self, func):
        if self.func is None:
            self.func = func
            return self
        else:
            return filter(self, func)

class reduce:
    """
    reduce(iterable){value>>>...} -> recuce
    recuce(func, iterable)        -> reduce
    reduce(..., initial=...)      -> reduce
    """
    def __new__(cls, func=None, iterable=MISSING, *,  initial=MISSING):
        if iterable is MISSING:
            if func is None:
                raise TypeError("reduce() without iterable")
            iterable, func = func, None
        if func is not None:
            if initial is MISSING:
                return _base_reduce(iterable, func)
            else:
                return _base_reduce(func, iterable, initial)
        else:
            return super().__new__(cls)

    def __init__(self, func=None, iterable=MISSING, *, initial=MISSING):
        if iterable is MISSING:
            iterable = func
        self.iterable = iterable
        self.initial = initial

    def __inject_code__(self, func):
        if self.initial is MISSING:
            return _base_reduce(func, self.iterable)
        else:
            return _base_reduce(func, self.iterable, self.initial)


def inject_code(obj, func):
    """
    Inject code in an object. As obj{func_statements}.
    Obj must have a __inject_code__ method or be callable
    :param obj: the object
    :param func: the function
    :return: the result of the method
    """
    method = getattr(obj, "__inject_code__", None)
    if method is None:
        return obj(func)
    else:
        return method(func)
