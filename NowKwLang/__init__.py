import pathlib
import sys

from NowKwLang import modules, run
from NowKwLang.parser import parse
from NowKwLang.lexer import lex
from NowKwLang.run import run
from NowKwLang.context import Ctx
from NowKwLang.interactive_console import ConsoleInteracter


def run_code(source: "str | hasattr read" = None, filename: str | pathlib.Path = None, debug=False):
    name = "<string>"
    if filename is not None:
        if source is not None:
            raise ValueError("Cannot specify both source and filename")
        name = path = pathlib.Path(filename)
        source = path.read_text()
        if path.parent not in sys.path:
            sys.path.append(str(path.parent))
    if hasattr(source, "read"):
        source = source.read()
        name = "<file>"
    if not isinstance(source, str):
        raise TypeError("Source must be a string")
    ctx = Ctx(name, source, debug=debug, is_real_file=filename is not None)
    tokens = lex(source, ctx)
    ast = parse(tokens, ctx)
    result = run(ast, ctx)
    return result

if __name__ == '__main__':
    ConsoleInteracter.run()
