import sys
import pathlib
import importlib

import NowKwLang


def pyimport(module_name: str, asname=None):
    module = importlib.import_module(module_name)
    if asname is not None:
        module.__asname__ = asname
    return module

MODULE_CACHE = {}


class Module:
    def __init__(self, scope, filename, pyname):
        MODULE_CACHE.setdefault(filename, self)
        sys.modules[pyname] = self
        self.__dict__ = scope
        self.__pyname__ = pyname
        self._filename = filename

    def __repr__(self):
        return f"<NkL module at {str(self._filename)!r}>"

def _search_in_directory(segments, paths) -> tuple[pathlib.Path, list[str]] | None:
    mdl_name = segments[0]
    segments = segments[1:]

    for path in paths:
        dir_path = path / mdl_name
        if dir_path.exists() and dir_path.is_dir():
            dir_segs = _search_in_directory(segments, [dir_path])
            if dir_segs is not None:
                return dir_segs
        file_path = path / (mdl_name + ".NkL")
        if file_path.exists() and file_path.is_file():
            return file_path, segments
    else:
        return None

def nklimport(module_name: str, asname=None):
    if not module_name:
        raise ValueError("Module name is an empty string")
    segments = module_name.split(".")
    if "" in segments:
        raise ValueError("Invalid module name: there is an empty name")
    dir_segs = _search_in_directory(segments, map(pathlib.Path, sys.path))
    if dir_segs is None:
        raise ModuleNotFoundError("Module not found...")
    file_path, unused_segments = dir_segs
    mdl = MODULE_CACHE.get(file_path)
    if mdl is None:
        if unused_segments:
            used_segs = segments[:-len(unused_segments)]
        else:
            used_segs = segments
        name = ".".join(used_segs)
        module_scope = NowKwLang.run_code(filename=file_path, return_scope=True)
        mdl = Module(module_scope, file_path, name)
    obj = mdl
    for attr_seg in unused_segments:
        obj = getattr(obj, attr_seg)
    if asname is not None:
        obj.__asname__ = asname
    return obj

def importer(module_name: str, asname=None):
    try:
        return nklimport(module_name, asname)
    except ModuleNotFoundError:
        return pyimport(module_name, asname)
