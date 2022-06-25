

class Ctx:
    def __init__(self, path, code):
        self.code = code
        self.path = path
        self.lines = code.split("\n")
        if path is not None:
            self.abspath = path.resolve()
        else:
            self.abspath = "<string>"
        self.abspathname = str(self.abspath)
