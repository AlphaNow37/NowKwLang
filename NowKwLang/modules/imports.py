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
        self.__dict__ = scope
        if name is not None:
            self.__asname__ = name

MODULE_CACHE = {}

def import_module(file, asname=None):
    if file in MODULE_CACHE:
        return MODULE_CACHE[file]
    else:
        module_scope = NowKwLang.run_code(filename=file, return_scope=True)
        mdl = Module(module_scope, asname)
        MODULE_CACHE[file] = mdl
        return mdl
