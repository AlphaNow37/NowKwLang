from NowKwLang import lexer
from NowKwLang.context import Ctx

def show_line(token, ctx: Ctx):
    line = ctx.lines[token.line - 1]
    if token.column == 0:  # For \n
        line += " "
        column = len(line)
    else:
        column = token.column
    line_indicator = f"{line}\n{' ' * (column - 1)}{'^' * token.length}"
    return line_indicator

class Error(Exception):
    def __init__(self, token, message: str, ctx: Ctx):
        self.ctx = ctx
        self.token: lexer.Token = token
        self.message = message

    def __str__(self):
        return f"{self.message}\n{show_line(self.token, self.ctx)}"

class SyntaxError(Error):
    pass

class ParsingError(SyntaxError):
    pass

class LexingError(SyntaxError):
    pass
