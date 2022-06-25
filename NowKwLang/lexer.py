from typing import Iterator

from NowKwLang import errors
from NowKwLang.context import Ctx


class Token:
    def __init__(self, line, column, length, ctx):
        self.line = line
        self.column = column
        self.length = length
        self.ctx = ctx

    def __repr__(self):
        return f"<{self.__class__.__name__} {self._get_infos()} at {self.line}:{self.column}:{self.length}>"

    def _get_infos(self):
        return ""

    __match_args__ = ()

class Constant:
    value: ...
    __match_args__ = ("value",)

class NewStmt(Token):
    pass

class NewLine(NewStmt):
    def __init__(self, line, ctx):
        super().__init__(line, 0, 1, ctx)


class _ValueToken(Token):
    def __init__(self, line, column, length, value, ctx):
        super().__init__(line, column, length, ctx)
        self.value = value

    def _get_infos(self):
        return str(self.value)

    __match_args__ = ("value",)

class Name(_ValueToken):
    pass

class Int(_ValueToken, Constant):
    pass

class Float(_ValueToken, Constant):
    pass

class String(_ValueToken, Constant):
    pass

class Symbol(_ValueToken):
    def __init__(self, line, column, length, value, stype, ctx):
        super().__init__(line, column, length, value, ctx)
        self.stype = stype

    def _get_infos(self):
        return f"{super()._get_infos()} {self.stype}"

    __match_args__ = ("value", "stype")

_SYMBOLS = {
    "points": ["...", ".", ":"],
    "part_sep": [">>>"],
    "boolean": ['&&', "||"],
    "math": ["+", "-",  "**", "*", "//", "%", "|", "&", "??"],
    "logic": ["===", "!==", "==", "!=", ">=", "<=", ">", "<"],
    "_opening": ["(", "[", "{"],
    "_closing": [")", "]", "}"],
    "separator": [","],
    "assign": ["="],
}

def _buff(source, i, condition):
    buffer = ""
    while i < len(source) and condition(source[i]):
        buffer += source[i]
        i += 1
    i -= 1
    return buffer, i


def generate_tokens(source, ctx):
    i = 0
    line = 1
    column = 1
    while i < len(source):
        if source[i] == '\n':
            yield NewLine(line, ctx)
            line += 1
            column = 0
        elif source[i: i+3] == "///":
            i += 3
            buffer, i = _buff(source, i, lambda c: c != '\n')
        elif source[i:i+2] == "/*":
            i += 2
            column += 2
            while i < len(source) and source[i:i+2] != "*/":
                column += 1
                if source[i] == '\n':
                    line += 1
                    column = 1
                i += 1
            column += 1
            i += 1
        elif source[i] == ';':
            yield NewStmt(line, column, 1, ctx)
        elif source[i] in ' \t':
            buffer, i = _buff(source, i, lambda c: c in ' \t')
            column += len(buffer) - 1
        elif source[i].isdigit() or source[i] == "." and i + 1 < len(source) and source[i + 1].isdigit():
            is_float = source[i] == "."

            def match(c):
                nonlocal is_float
                if c.isdigit():
                    return True
                elif not is_float and c == ".":
                    is_float = True
                    return True
                elif c == "_":
                    return True
                return False

            buffer, i = _buff(source, i, match)
            token_cls, caster = (Float, float) if is_float else (Int, int)
            yield token_cls(line, column, len(buffer), caster(buffer), ctx)
            column += len(buffer) - 1
        elif source[i].isalpha() or source[i] == '_':
            buffer, i = _buff(source, i, lambda c: c.isalnum() or c == '_')
            yield Name(line, column, len(buffer), buffer, ctx)
            column += len(buffer) - 1
        elif source[i] in "'\"":
            string = ""
            quote = source[i]
            i += 1
            base_column = column
            base_line = line
            was_slashed = False
            length = 0
            for char in source[i:]:
                column += 1
                length += 1
                if was_slashed:
                    new_char = {
                        "'": "'",
                        '"': '"',
                        "\\": "\\",
                        "t": "\t",
                        "n": "\n",
                        "r": "\r",
                    }.get(char, "\\" + char)
                    string += new_char
                    was_slashed = False
                elif char == quote:
                    break
                elif char == '\n':
                    line += 1
                    column = 0
                elif char == '\\':
                    was_slashed = True
                else:
                    string += char
            else:
                raise errors.SyntaxError(Token(base_line, base_column-1, 1, ctx), "Unclosed string", ctx)
            i += length - 1
            yield String(base_line, base_column, length + 1, string, ctx)
        else:
            cont = True
            for stype, symbols in _SYMBOLS.items():
                for symbol in symbols:
                    if source[i:i + len(symbol)] == symbol:
                        if stype == "math" and source[i+len(symbol): i+len(symbol)+1] == "=":
                            yield Symbol(line, column, len(symbol) + 1, symbol + "=", "in-place", ctx)
                            column += 1
                            i += 1
                        else:
                            yield Symbol(line, column, len(symbol), symbol, stype, ctx)
                        column += len(symbol) - 1
                        i += len(symbol) - 1
                        cont = False
                        break
                if not cont:
                    break
        column += 1
        i += 1

class BracketGroup(Token):
    def __init__(self, line, column, bracket_char, tokens, ctx):
        super().__init__(line, column, 1, ctx)
        self.bracket_char = bracket_char
        self.tokens = tokens

    def __repr__(self):
        return f"<Group border={self.bracket_char} tokens={self.tokens}>"

    __match_args__ = ("bracket_char", "tokens")


CLOSERS = {
    "(": ")",
    "{": "}",
    "[": "]",
}

def group_brackets(iterator, closing, ctx, first_token=None):
    while True:
        try:
            token = next(iterator)
        except StopIteration:
            if closing is None:
                return
            else:
                raise errors.LexingError(first_token, "Unclosed bracket", ctx) from None
        match token:
            case Symbol(border, "_opening"):
                tokens = list(group_brackets(iterator, CLOSERS[border], ctx, token))
                yield BracketGroup(token.line, token.column, border, tokens, ctx)
            case Symbol(border, "_closing") if border == closing:
                return
            case Symbol(border, "_closing"):
                raise errors.LexingError(first_token, f"Closing bracket don't match any open bracket", ctx)
            case token:
                yield token

def lex(source: str, ctx) -> Iterator[Token | None]:
    iterator = iter(generate_tokens(source, ctx))
    yield from group_brackets(iterator, None, ctx)

if __name__ == '__main__':
    code = """
i = 0
while{i<10}{
    i = i + 1
    print(i)
}

"""
    print(repr(code))
    for token in lex(code, Ctx(None, code)):
        print(token)
