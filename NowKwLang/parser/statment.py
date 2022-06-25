from NowKwLang.parser import expr as expr_mdl
from NowKwLang.parser._stream import TokenStream
from NowKwLang.errors import ParsingError

from NowKwLang.lexer import Symbol

class VarSetter:
    def __init__(self, name, value, token):
        self.name = name
        self.value = value
        self.token = token

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name}={self.value}>"

    __match_args__ = ("name", "value")

class AttrSetter:
    def __init__(self, obj, name, value, token):
        self.obj = obj
        self.name = name
        self.value = value
        self.token = token

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.obj}:{self.name}={self.value}>"

    __match_args__ = ("obj", "name", "value")

def get_setter(target, value, stream: TokenStream, token):
    match target:
        case expr_mdl.Variable(name):
            return VarSetter(name, value, token)
        case expr_mdl.Attribute(obj, name):
            return AttrSetter(obj, name, value, token)
        case expr_mdl.Const():
            raise ParsingError(target.token, "Cannot assign to a constant", stream.ctx)
        case expr_mdl.Call():
            raise ParsingError(target.token, "Cannot assign to a call", stream.ctx)
        case _:
            raise NotImplementedError()

def parse_statment(stream: TokenStream):
    token = stream.get(0)
    if token is None:
        return None
    expr = expr_mdl.parse_expr(stream)
    token = stream.get(0)
    match token:
        case Symbol("=" as op) | Symbol(op, "in-place"):
            stream.consume(1)
            second_expr = expr_mdl.parse_expr(stream)
            if op != "=":
                bef_op = op.removesuffix("=")
                second_expr = expr_mdl.Operator(expr, bef_op, second_expr, token)
            stmt = get_setter(expr, second_expr, stream, token)
        case _:
            stmt = expr
    return stmt
