from NowKwLang.NkL_std_libs import scope

_DEFAULT = object()

def Namespace(*args, **kwargs):
    args = list(reversed(args))

    class NameSpacedScope(scope.Scope):
        def __setitem__(self, key, value):
            self.superscope[key] = value

        def __getitem__(self, item):
            value = kwargs.get(item, _DEFAULT)
            if value is not _DEFAULT:
                return value
            for arg in args:
                value = getattr(arg, item, _DEFAULT)
                if value is not _DEFAULT:
                    return value
            return super().__getitem__(item)

    def wrapper(func):
        __traceback_show__ = False
        func.__scope_factory__ = NameSpacedScope
        return func()

    return wrapper

Namespace.__name__ = Namespace.__qualname__ = "namespace"

def With(*args, **kwargs):
    def wrapper(func):
        class WithScope(scope.Scope):
            def __setitem__(self, key, value):
                self.superscope[key] = value

            def __getitem__(self, item):
                if item in entered_nameds:
                    return entered_nameds[item]
                return super().__getitem__(item)

        __traceback_show__ = False
        func.__scope_factory__ = WithScope
        entered_nameds = {name: obj.__enter__() for (name, obj) in kwargs.items()}
        for obj in args:
            obj.__enter__()
        try:
            result = func()
        except BaseException as e:
            a, b, c = type(e), e, e.__traceback__
            for obj in args:
                res = obj.__exit__(a, b, c)
                if res:
                    a = b = c = None
            if a is None:
                return None
            else:
                raise
        else:
            for obj in args:
                obj.__exit__(None, None, None)
            for name, obj in entered_nameds.items():
                obj.__exit__(None, None, None)
            return result
    return wrapper

With.__name__ = With.__qualname__ = "with"
