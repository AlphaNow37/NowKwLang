
class _InjectWaiter:
    def __init__(self, value):
        self.value = value

    def __inject_code__(self, _):
        return self.value

class _ElseWaiter:
    def __init__(self, value):
        self.value = value

    def __inject_code__(self, _):
        return self

    def Elif(self, *_, **__):
        return _InjectWaiter(_ElseWaiter(self.value))

    @property
    def Else(self):
        return _InjectWaiter(self.value)

setattr(_ElseWaiter, "elif", _ElseWaiter.Elif)
setattr(_ElseWaiter, "else", _ElseWaiter.Else)

class _InjectExecutor:
    @staticmethod
    def __inject_code__(func):
        __traceback_show__ = False
        return func()

class If:
    def __init__(self, passed):
        self.test_passed = passed

    def __inject_code__(self, func=None):
        if func is None:
            raise TypeError("You need to do if(test){...}")
        else:
            func.__create_scope__ = False
            func.__traceback_show__ = False
            if self.test_passed:
                __traceback_show__ = False
                self.value = func()
            else:
                self.value = None
        return self

    @property
    def Else(self):
        if self.test_passed:
            return _InjectWaiter(self.value)
        else:
            return _InjectExecutor()

    def Elif(self, passed):
        if self.test_passed:
            return _ElseWaiter(self.value)
        else:
            return If(passed)

setattr(If, "else", If.Else)
setattr(If, "elif", If.Elif)
