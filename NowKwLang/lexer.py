from typing import Iterator
from collections import deque
import re

from NowKwLang import errors
from NowKwLang.context import Ctx


class CharStream:
    def __init__(self, iterator):
        self.chars = deque()
        if isinstance(iterator, str):
            self.chars.extend(iterator)
            iterator = iter(())
        self.iterator = iterator
        self.pos = 0
        self.line = 1
        self.col = 1

    def get(self, i=0, default=None):
        if i < len(self.chars):
            return self.chars[i]
        for _ in range(i - len(self.chars) + 1):
            try:
                self.chars.append(next(self.iterator))
            except StopIteration:
                return default
        return self.chars[-1]

    def consume(self, n):
        for _ in range(n):
            self.pos += 1
            if self.get() == "\n":
                self.line += 1
                self.col = 1
            else:
                self.col += 1
            self.chars.popleft()

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.get(item)
        elif isinstance(item, slice):
            return "".join(self.get(index, "") for index in range(item.start, item.stop))

    def startswith(self, string):
        return all(self.get(i) == char for i, char in enumerate(string))


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
        return repr(self.value)

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
    "math": ["+", "-",  "**", "*", "//", "%", "|", "&", "??", "<<", ">>"],
    "logic": ["===", "!==", "==", "!=", ">=", "<=", ">", "<"],
    "_opening": ["(", "[", "{"],
    "_closing": [")", "]", "}"],
    "separator": [","],
    "assign": ["="],
}

def _buff(stream: CharStream, condition):
    buffer = ""
    while condition(char := stream.get()):
        buffer += char
        stream.consume(1)
    return buffer


prefixs = {
    "re": ("re", "compile"),
    "json": ("json", "loads"),
}

def parse_string(stream: CharStream, ctx, prefix=""):
    caster = str
    is_raw = False
    if prefix in prefixs:
        module_name, method_name = prefixs[prefix]
        caster = getattr(__import__(module_name), method_name)
    else:
        if prefix.startswith("r"):
            is_raw = True
            prefix = prefix[1:]
        if prefix.startswith("b"):
            caster = str.encode
            prefix = prefix[1:]
        if prefix:
            raise errors.LexingError(Token(stream.line, stream.col-len(prefix), len(prefix), ctx), "Unkown prefix", ctx)
    endquote = stream.get()
    base_column = stream.col
    base_line = stream.line
    stream.consume(1)
    was_slashed = False
    text = ""
    while (char := stream.get()) != endquote or was_slashed:
        if char is None:
            raise errors.LexingError(Token(base_line, base_column, 1, ctx), "Unclosed string", ctx)
        stream.consume(1)
        if was_slashed:
            text += {
                "'": "'",
                '"': '"',
                "\\": "\\",
                "t": "\t",
                "n": "\n",
                "r": "\r",
            }.get(char, "\\" + char)
            was_slashed = False
        elif char == "\\" and not is_raw:
            was_slashed = True
        elif char != endquote:
            text += char
    stream.consume(1)
    casted = caster(text)
    return String(base_line, base_column, len(text), casted, ctx)


def generate_tokens(stream: CharStream, ctx):
    while (char := stream.get()) is not None:
        if char == '\n':
            yield NewLine(stream.line, ctx)
            stream.consume(1)
        elif stream.startswith("///"):
            _ = _buff(stream, lambda c: c != '\n')
        elif stream.startswith("/*"):
            o_line, o_col = stream.line, stream.col
            stream.consume(2)
            while not stream.startswith("*/"):
                stream.consume(1)
                if stream.get() is None:
                    raise errors.LexingError(Token(o_line, o_col, 2, ctx), "unclosed comment", ctx)
            stream.consume(2)
        elif char == ';':
            yield NewStmt(stream.line, stream.col, 1, ctx)
            stream.consume(1)
        elif char in ' \t':
            _ = _buff(stream, lambda c: c in ' \t')
        elif char.isdigit() or char == "." and stream.get(1, "_").isdigit():
            is_float = char == "."

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

            buffer = _buff(stream, match)
            token_cls, caster = (Float, float) if is_float else (Int, int)
            yield token_cls(stream.line, stream.col, len(buffer), caster(buffer), ctx)
        elif char.isalpha() or char == '_':
            base_col = stream.col
            buffer = _buff(stream, lambda c: c.isalnum() or c == '_')
            if stream.get() in "\"'":
                yield parse_string(stream, ctx, buffer)
            else:
                yield Name(stream.line, base_col, len(buffer), buffer, ctx)
        elif char in "'\"":
            yield parse_string(stream, ctx)
        else:
            cont = True
            for stype, symbols in _SYMBOLS.items():
                for symbol in symbols:
                    if stream.startswith(symbol):
                        if stype == "math" and stream.get(len(symbol)) == "=":
                            yield Symbol(stream.line, stream.col, len(symbol) + 1, symbol + "=", "in-place", ctx)
                            stream.consume(1)
                        else:
                            yield Symbol(stream.line, stream.col, len(symbol), symbol, stype, ctx)
                        stream.consume(len(symbol))
                        cont = False
                        break
                if not cont:
                    break
            else:
                raise errors.LexingError(Token(stream.line, stream.col, 1, ctx), f"Unknown character: {char!r}", ctx)

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
            case _:
                yield token

def lex(source: str | Iterator, ctx) -> Iterator[Token | None]:
    stream = CharStream(source)
    iterator = iter(generate_tokens(stream, ctx))
    yield from group_brackets(iterator, None, ctx)

if __name__ == '__main__':
    code = r"""
re'hey'
"""
    print(repr(code))
    for token in lex(code, Ctx("string", code, is_real_file=False)):
        print(token)
