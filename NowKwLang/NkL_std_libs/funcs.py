from typing import Callable

class _ReprMeta(type):
    _name = "unknown"

    def __repr__(cls):
        return cls._name

class Func(metaclass=_ReprMeta):
    """
    return the function
    func("name", "doc"){...}  -> create a function with name "name" and doc "doc"
    func{...}                 -> create an anonymous function

    """
    _name = "func"

    def __init__(self, name="", doc=""):
        self.name = name
        self.doc = doc

    def __inject_code__(self, func: Callable = None):
        if func is None:
            func = self
            func.__name__ = ""
        else:
            if self.name is not None:
                func.__name__ = self.name
            if self.doc is not None:
                func.__doc__ = self.doc
        return func

    def __repr__(self):
        if self.name is self.doc is None:
            return "func"
        return f"func({self.name!r}, {self.doc!r})"

Func.__name__ = Func.__qualname__ = "func"


class MethodProxy(object):
    def __init__(self, instance, method):
        self.__instance = instance
        self.__method = method

    def __getattr__(self, item):
        return getattr(self.__method, item)

    def __call__(self, *args, **kwargs):
        return self.__method(self.__instance, *args, **kwargs)

    def __repr__(self):
        return f"<MethodProxy of {self.__instance!r}>"


class Method(Func):
    _name = "method"
    func = None

    def __inject_code__(self, func: Callable = None):
        self.func = super().__inject_code__(func)
        self.__name__ = self.func.__name__
        self.__doc__ = self.func.__doc__
        return self

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return MethodProxy(instance, self.func)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


Method.__name__ = Method.__qualname__ = "method"
