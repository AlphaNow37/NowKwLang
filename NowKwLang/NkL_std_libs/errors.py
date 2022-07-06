from NowKwLang.errors import SyntaxError as _Serror, ParsingError as _Perror, LexingError as _Lerror


class _WrapMeta(type):
    _alias = None

    def __instancecheck__(self, instance):
        return isinstance(instance, self._alias) or super().__instancecheck__(instance)

class SyntaxError(SyntaxError, metaclass=_WrapMeta):
    _alias = _Serror

    def __init__(self, message=None):
        if message is None:
            message = "An error occured"
        self.message = message

    def __str__(self):
        return self.message

class LexingError(SyntaxError):
    _alias = _Lerror

class ParsingError(SyntaxError):
    _alias = _Perror
