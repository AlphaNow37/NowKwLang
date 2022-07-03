from textwrap import indent

from NowKwLang import lexer
from NowKwLang.context import Ctx

PAD = " "*2

error_message = """
{pad}File "{file}", line {line}, column {column}
{line_indicator}
{Errorname}: {message}
""".strip()

def show_line(token, ctx: Ctx):
    line = ctx.lines[token.line - 1]
    if token.column == 0:  # For \n
        line += " "
        column = len(line)
    else:
        column = token.column
    line_indicator = f"{line}\n{' ' * (column - 1)}{'^' * token.length}"
    return indent(line_indicator, PAD*2+"| ")

class Error(Exception):
    def __init__(self, token, message: str, ctx: Ctx):
        self.ctx = ctx
        self.token: lexer.Token = token
        self.message = message

    def __str__(self):
        return error_message.format(
            pad=PAD,
            file=self.ctx.path,
            line=self.token.line,
            column=self.token.column,
            line_indicator=show_line(self.token, self.ctx),
            Errorname=self.__class__.__name__,
            message=self.message
        )

class SyntaxError(Error):
    pass

class ParsingError(SyntaxError):
    pass

class LexingError(SyntaxError):
    pass
