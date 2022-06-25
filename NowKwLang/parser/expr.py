from NowKwLang.parser._stream import TokenStream
from NowKwLang.parser import collections
from NowKwLang.errors import ParsingError
from NowKwLang.parser import block
from NowKwLang.constants import MISSING

from NowKwLang.lexer import Name, Token, Constant, Symbol, BracketGroup

class Expr:
    def __init__(self, token: Token):
        self.token = token

class Variable(Expr):
    def __init__(self, name: str, token):
        super().__init__(token)
        self.name = name

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}>"

    __match_args__ = ("name",)

class Const(Expr):
    def __init__(self, value, token):
        super().__init__(token)
        self.value = value

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.value}>"

    __match_args__ = ("value", )

class Attribute(Expr):
    def __init__(self, obj, name, token):
        super().__init__(token)
        self.obj = obj
        self.name = name

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.obj}:{self.name}>"

    __match_args__ = ("obj", "name")

class Call(Expr):
    def __init__(self, obj, args, kwargs, token, is_subscript):
        super().__init__(token)
        self.obj = obj
        self.args = args
        self.kwargs = kwargs
        self.is_subscript = is_subscript

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.obj}({self.args}, {self.kwargs})>"

    __match_args__ = ("obj", "args", "kwargs", "is_subscript")

class CodeInject(Expr):
    def __init__(self, obj, args, token, body):
        super(CodeInject, self).__init__(token)
        self.obj = obj
        self.args = args
        self.body = body
        if self.args is not None:
            self.keys = [arg[0] for arg in args]
        else:
            self.keys = None

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.obj}({self.args}) -> {self.body}>"

    __match_args__ = ("obj", "args", "body", "keys")

class Collection(Expr):
    def __init__(self, type_, exprs, token):
        super().__init__(token)
        self.type = type_
        self.exprs = exprs

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.type} ({self.exprs})>"

    __match_args__ = ("type", "exprs",)

class Dict(Expr):
    def __init__(self, items, token):
        super().__init__(token)
        self.items = items

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.items}>"

    __match_args__ = ("items", )

class Operator(Expr):
    def __init__(self, left, op, right, token):
        super().__init__(token)
        self.left = left
        self.op = op
        self.right = right
        self.token = token

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.left} {self.op} {self.right}>"
    __match_args__ = ("left", "op", "right")

def parse_expr(stream: TokenStream):
    token = stream.get(0)
    if token is None:
        raise NotImplementedError()
    return parse_operators(0, stream)

def parse_stack(stream: TokenStream):
    token: Token = stream.get(0)
    match token:
        case Name(name):
            actual = Variable(name, token)
        case Constant(value):
            actual = Const(value, token)
        case BracketGroup(opening, tokens):
            has_sep, args, kwargs = collections.parse_collection(stream.sub(tokens), dict_or_set=opening == "{")
            match (opening, has_sep, args, kwargs):
                case "(" | "[", _, _, [kw, *_]:
                    raise ParsingError(kw[1].token, "list and tuple can't have named parameters", stream.ctx)
                case '(', False, [arg, ], []:
                    actual = arg
                case "(", _, elements, []:
                    actual = Collection(tuple, elements, token)
                case "{", _, [], items:
                    actual = Dict(items, token)
                case "{", _, elements, []:
                    actual = Collection(set, elements, token)
                case "[", _, elements, []:
                    actual = Collection(list, elements, token)
                case _:
                    raise NotImplementedError()
        case Symbol("..."):
            actual = Variable("...", token)
        case _:
            raise ParsingError(token, "Invalid syntax", stream.ctx)
    stream.consume(1)
    while True:
        token = stream.get(0)
        match token:
            case Symbol("."):
                stream.consume(1)
                other = stream.get(0)
                if isinstance(other, Name):
                    actual = Attribute(actual, other.value, other)
                else:
                    raise ParsingError(other, "Atributes must be names", stream.ctx)
                stream.consume(1)
            case BracketGroup(opening, tokens):
                substream = stream.sub(tokens, opening in ('(', "["))
                stream.consume(1)
                if opening in ('(', "["):
                    _, args, kwargs = collections.parse_collection(substream, None)
                    actual = Call(actual, args, kwargs, token, opening == "[")
                else:
                    assert opening == "{"
                    i = 0
                    while True:
                        t = substream.get(i)
                        if isinstance(t, Symbol) and t.value == ">>>":
                            has_args = True
                            break
                        elif t is None:
                            has_args = False
                            break
                        else:
                            i += 1
                    if has_args:
                        args_substream = substream.sub(substream[:i], True)
                        _, args, kwargs = collections.parse_collection(args_substream, is_argdef=True)
                        args = [(arg, MISSING) for arg in args]
                        args += kwargs
                        seen = set()
                        for name, value in args:
                            if name.value in seen:
                                raise ParsingError(name, f"Duplicate argument name '{name.value}'", stream.ctx)
                            seen.add(name.value)
                        args = [(arg.value, value) for arg, value in args]
                        substream.consume(i+1)
                    else:
                        args = None
                    actual = CodeInject(actual, args, token, block.parse_block(substream))
            case _:
                break
    return actual


PRIORITY = [
    ("||", ), ("&&", ), ("===", "!=="),
    ("==", "!=", "<", ">", "<=", ">="),
    ("|",), ("^",), ("&",), ("<<", ">>"),
    ("+", "-"), ("*", "/", "//", "%"), ("**",), ("??", )
]
def parse_operators(level, stream: TokenStream):
    if level == len(PRIORITY):
        return parse_stack(stream)
    left = parse_operators(level+1, stream)
    ops = PRIORITY[level]
    while True:
        token = stream.get(0)
        match token:
            case Symbol(op) if op in ops:
                stream.consume(1)
                right = parse_operators(level+1, stream)
                left = Operator(left, op, right, token)
            case _:
                return left
