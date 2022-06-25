import sys
import pathlib
import NowKwLang

class Importer:
    def __init__(self):
        pass

    def __call__(self, module_name, asname=None):
        sys_paths = [pathlib.Path(p) for p in sys.path]
        for path in sys_paths:
            if path.is_dir():
                for file in path.iterdir():
                    if file.is_file():
                        if file.name.removesuffix(".NkL") == module_name:
                            return import_module(file, asname)
        else:
            module = __import__(module_name)
            if asname is not None:
                module.__asname__ = asname
            return module

class Module:
    def __init__(self, scope, name):
        if name is not None:
            self.__asname__ = name
        self.__dict__ = scope

def import_module(file, asname=None):
    module_scope = NowKwLang.run_code(filename=file)
    return Module(module_scope, asname)
