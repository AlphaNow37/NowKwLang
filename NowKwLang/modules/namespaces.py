from NowKwLang.modules import scope

_DEFAULT = object()

def namespace(*args, **kwargs):
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
