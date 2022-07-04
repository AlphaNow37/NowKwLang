from typing import Callable

class _FuncMeta(type):
    def __repr__(cls):
        return "func"

class Func(metaclass=_FuncMeta):
    """
    return the function
    func("name", "doc"){...}  -> create a function with name "name" and doc "doc"
    func{...}                 -> create an anonymous function

    """
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

func = Func
