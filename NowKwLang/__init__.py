import pathlib
import sys

from NowKwLang import NkL_std_libs, run
from NowKwLang.parser import parse
from NowKwLang.lexer import lex
from NowKwLang.run import run
from NowKwLang.context import Ctx
from NowKwLang.interactive_console import ConsoleInteracter

def NkL_run(filename: str | pathlib.Path = None, debug=False):
    path = pathlib.Path(filename)
    if path.parent not in sys.path:
        sys.path.append(str(path.parent))
    return _run_code(filename=path, debug=debug, module_pyname="__main__")

def _run_code(source: "str | hasattr read" = None, filename: str | pathlib.Path = None,
              debug=False, return_scope=False, *, module_pyname):
    name = "<string>"
    if filename is not None:
        if source is not None:
            raise ValueError("Cannot specify both source and filename")
        name = path = pathlib.Path(filename)
        source = path.read_text()

    if hasattr(source, "read"):
        source = source.read()
        name = "<file>"
    if not isinstance(source, str):
        raise TypeError("Source must be a string")
    ctx = Ctx(name, source, module_pyname, debug=debug, is_real_file=filename is not None)
    tokens = lex(source, ctx)
    ast = parse(tokens, ctx)
    result = run(ast, ctx, return_scope=return_scope, module_pyname=module_pyname)
    return result

if __name__ == '__main__':
    ConsoleInteracter.run(False)
