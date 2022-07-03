

class Ctx:
    def __init__(self, path, code, debug=False, is_real_file=True):
        self.is_real_file = is_real_file
        self.code = code
        self.path = path
        self.lines = code.split("\n")
        if is_real_file:
            self.abspath = path.resolve()
        else:
            self.abspath = path
        self.debug = debug
