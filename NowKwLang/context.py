

class Ctx:
    def __init__(self, path, code, pyname, debug=False, is_real_file=True):
        self.is_real_file = is_real_file
        self.code = code
        self.path = path
        self.lines = code.split("\n")
        self.pyname = pyname
        if is_real_file:
            self.abspath = path.resolve()
            self.file_name = path.stem
        else:
            self.abspath = path
            self.file_name = path
        self.debug = debug
