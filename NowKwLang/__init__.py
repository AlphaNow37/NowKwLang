import pathlib

from NowKwLang import modules, run
from NowKwLang.parser import parse
from NowKwLang.lexer import lex
from NowKwLang.run import run
from NowKwLang.context import Ctx


def run_code(source: "str | hasattr read" = None, filename: str | pathlib.Path = None):
    name = None
    if filename is not None:
        if source is not None:
            raise ValueError("Cannot specify both source and filename")
        name = path = pathlib.Path(filename)
        source = path.read_text()
    if hasattr(source, "read"):
        source = source.read()
    if not isinstance(source, str):
        raise TypeError("Source must be a string")
    ctx = Ctx(name, source)
    tokens = lex(source, ctx)
    ast = parse(tokens, source, ctx)
    result = run(ast, ctx)
    return result
