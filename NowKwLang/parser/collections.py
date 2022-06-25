from NowKwLang.parser._stream import TokenStream, TokenSubStream
from NowKwLang.parser.expr import Expr, parse_expr, Variable
from NowKwLang.errors import ParsingError

from NowKwLang.lexer import Symbol, Name

KW = True
POS = False


def get_element(stream: TokenStream, dict_or_set, is_argdef, last_type) -> tuple[tuple[bool, Expr | Name, Expr | None], bool]:
    expr = parse_expr(stream)
    token = stream.get(0)
    if dict_or_set:
        if isinstance(token, Symbol) and token.value == ":":
            stream.consume(1)
            second_expr = parse_expr(stream)
            value = KW, expr, second_expr
            if last_type == POS:
                raise ParsingError(token, "A set can't contain pair of values", stream.ctx)
        else:
            value = POS, expr, None
            if last_type == KW:
                raise ParsingError(token, "A dict must contain pair of values", stream.ctx)
    else:
        after = stream.get(0)
        if isinstance(after, Symbol) and after.value == "=":
            if not isinstance(expr, Variable):
                raise ParsingError(after, "Keyworlds must be names", stream.ctx)
            stream.consume(1)
            second_expr = parse_expr(stream)
            value = KW, expr.token, second_expr
        elif last_type == KW:
            raise ParsingError(after, "Positionnal arg follow keyworld arg", stream.ctx)
        else:
            if is_argdef:
                if isinstance(expr, Variable):
                    value = POS, expr.token, None
                else:
                    raise ParsingError(after, "Positionnal args must be names", stream.ctx)
            else:
                value = POS, expr, None
    sep = stream.get(0)
    if sep is None:
        return value, False
    if isinstance(sep, Symbol) and sep.value == ",":
        stream.consume(1)
        return value, True
    raise ParsingError(sep, "Exprs must be separated by a ','", stream.ctx)


def parse_collection(sub_stream: TokenSubStream, is_argdef=False, dict_or_set=False) -> tuple[bool, list, list]:
    args = []
    kwargs = []
    has_sep = False
    last_type = None

    while sub_stream.get(0) is not None and sub_stream.get():
        (last_type, key, value), has_sep_ = get_element(sub_stream, dict_or_set, is_argdef, last_type)
        has_sep = has_sep or has_sep_
        if value is None:
            args.append(key)
        else:
            kwargs.append((key, value))
    return has_sep, args, kwargs
