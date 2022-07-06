from NowKwLang.constants import MISSING

def raise_(exc: Exception = None, cause=MISSING):
    """
    throw an exception
    :param exc: the exception to raise
    :param cause: the cause of the exc
    :return: None
    """
    if exc is None:
        raise
    if cause is MISSING:
        raise exc
    else:
        raise exc from cause

raise_.__name__ = "raise"


class Try:
    DONT_WORKS = type("DONT_WORKS_CLS", (object, ), {
        "__repr__": lambda: "Try.DONT_WORKS",
        "__bool__": False,
    })()

    def __init__(self, func):
        func.__scope_factory__ = lambda scope: scope
        self.func = func
        self.excepts = []

    def Except(self, *exc_types, pass_exc=True):
        if not exc_types:
            exc_types = (Exception,)

        class Wrapper:
            @staticmethod
            def __inject_code__(func):
                func.__scope_factory__ = lambda scope: scope
                self.excepts.append((exc_types, func, pass_exc))
                return self

        return Wrapper

    def Finally(self, func=None):
        __traceback_show__ = False
        if func is not None:
            func.__scope_factory__ = lambda scope: scope
        return self.run(func)

    def Else(self, func=None):
        __traceback_show__ = False
        if func is not None:
            func.__scope_factory__ = lambda scope: scope
        if self.run() is not self.DONT_WORKS:
            return func()

    def run(self, _final_func=None):
        __traceback_show__ = False
        result = self.DONT_WORKS
        try:
            result = self.func()
        except BaseException as e:
            for exc_types, handler, pass_exc in self.excepts:
                if isinstance(e, exc_types):
                    if pass_exc:
                        handler(e)
                    else:
                        handler()
                    break
            else:
                raise e from None
        finally:
            if _final_func:
                _final_func()
        return result

setattr(Try, "except", Try.Except)
setattr(Try, "finally", Try.Finally)
setattr(Try, "else", Try.Else)
