from NowKwLang.constants import MISSING

from NowKwLang.NkL_std_libs import scope as _scope


class Type:
    def __new__(cls, obj, bases=MISSING, attrs=MISSING, /, **kwargs):
        if not kwargs and bases is attrs is MISSING:
            return type(obj)
        if bases is MISSING:
            bases = ()
        if attrs is MISSING:
            attrs = {}
        new_cls = type(obj, bases, attrs | kwargs)
        new_cls.__module__ = cls.__module__
        return new_cls

    @classmethod
    def __copy__(cls):
        return type(cls.__name__, cls.__bases__, vars(cls).copy())

Type.__name__ = Type.__qualname__ = "type"

class Class:
    def __init__(self, name="<Anonymous class>", bases=(object, ), attrs=None, /, **kwargs):
        if not isinstance(name, str):
            raise TypeError("Class name must be a string")
        if not isinstance(bases, (tuple, list)):
            raise TypeError("Class bases must be a tuple or list")
        self.name = name
        self.bases = bases
        self.attrs = (attrs or {}) | kwargs

    def __inject_code__(self, func=None):
        __traceback_show__ = False
        if func is None:
            return Class().__inject_code__(func)
        else:
            scope: _scope.Scope

            def scope_factory(superscope):
                nonlocal scope
                scope = _scope.Scope(superscope)
                return scope

            __traceback_show__ = False
            func.__scope_factory__ = scope_factory
            func()
            cls = type(self.name, self.bases, self.attrs | scope)
            cls.__module__ = func.__module__
            return cls

Class.__name__ = Class.__qualname__ = "class"
