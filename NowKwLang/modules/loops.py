
class While:
    def __init__(self, test):
        if not callable(test):
            raise TypeError("test must be callable")
        self.test = test

    def __inject_code__(self, func=None):
        if func is None:
            return While(self)
        else:
            __traceback_show__ = False
            func.__create_scope__ = False
            while self.test():
                func()

class For:
    def __init__(self, target_name: str, iterable):
        if not isinstance(target_name, str):
            raise TypeError("target_name must be a string")
        self.target_name = target_name
        self.iterable = iterable

    def __inject_code__(self, func=None):
        if func is None:
            raise TypeError("You need to do for('varname', iterable){...}")
        else:
            func.__create_scope__ = False
            __traceback_show__ = False
            for value in self.iterable:
                func.__call__(**{self.target_name: value})
