from functools import update_wrapper
import linecache
import operator

from NowKwLang.parser.block import Block
from NowKwLang.parser.expr import Expr, Variable, Const, Attribute, Call, Collection, Dict, CodeInject, Operator
from NowKwLang.parser.statment import AttrSetter, VarSetter
from NowKwLang.constants import MISSING
from NowKwLang.errors import show_line
from NowKwLang.lexer import Token
from NowKwLang.context import Ctx

from NowKwLang.modules import Scope

_DEBUG = False

class Function:
    def __init__(self, oncall, module):
        self.__oncall = oncall
        self.__call__ = oncall
        self.__name__ = "<function>"
        self.__doc__ = ""
        self.__module__ = module

    def __call__(self, *args, **kwargs):
        return self.__oncall(*args, **kwargs)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.__module__} {self.__name__} at {hex(id(self))}>"


OPERATORS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "//": operator.floordiv,
    "%": operator.mod,
    "**": operator.pow,
    "<<": operator.lshift,
    ">>": operator.rshift,
    "&": operator.and_,
    "|": operator.or_,
    "^": operator.xor,
    "~": operator.inv,
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
    "===": operator.is_,
    "!==": operator.is_not,
}
UNTOTALLY_EVALUATED_OPS = {
    "||": lambda obj: not obj,
    "&&": bool,
    "??": lambda obj: obj is None,
}

def get_expr_value(expr: Expr, scope):
    token: Token = expr.token
    match expr:
        case Variable(name):
            try:
                return scope[name]
            except NameError as e:
                raise NameError(str(e)) from None
        case Const(value):
            return value
        case Attribute(obj, attrname):
            return getattr(get_expr_value(obj, scope), attrname)
        case Call(obj, args, kwargs, is_subscript):
            exe_obj = get_expr_value(obj, scope)
            method = exe_obj.__getitem__ if is_subscript else exe_obj
            return method(
                *(get_expr_value(arg, scope) for arg in args),
                **{key.value: get_expr_value(value, scope) for (key, value) in kwargs}
            )
        case Collection(type_, elements):
            return type_(get_expr_value(elt, scope) for elt in elements)
        case Dict(items):
            return {
                get_expr_value(key, scope): get_expr_value(value, scope)
                for (key, value) in items
            }
        case CodeInject(obj, args, body, keys):
            if args is not None:
                evaluated_defaults = {
                    argname: get_expr_value(value, scope)
                    for (argname, value) in args
                    if value is not MISSING
                }
            else:
                evaluated_defaults = None

            class Function:
                def __init__(self):
                    self.__name__ = "<function>"
                    self.__doc__ = ""
                    self.__module__ = obj.token.ctx.path
                    self.__scope_factory__ = Scope

                def __call__(self, *fargs, **fkwargs):
                    __funcname__ = self.__name__
                    if args is None:
                        if fargs:
                            raise ValueError("Function takes no arguments but got %d" % len(fargs))
                        values = fkwargs
                    else:
                        values = evaluated_defaults | dict(zip(keys, fargs))
                        for key in fkwargs:
                            if key in values:
                                raise ValueError(f"Argument {key} is already defined")
                            elif key not in keys:
                                raise ValueError(f"Argument {key} is not defined")
                            else:
                                values[key] = fkwargs[key]
                        for argname in keys:
                            if argname not in values:
                                raise ValueError(f"Argument {argname} is missing")
                    new_scope = self.__scope_factory__(scope)
                    new_scope.update(values)
                    return run_block(body, new_scope)

                def __repr__(self):
                    return f"<{self.__class__.__name__} {self.__module__} {self.__name__} at {hex(id(self))}>"
            obj_ = get_expr_value(obj, scope)
            method = getattr(obj_, "__inject_code__", None)
            if method is None:
                return obj_(Function())
            else:
                return method(Function())

        case Operator(left, op, right):
            left = get_expr_value(left, scope)
            right = get_expr_value(right, scope)
            func = OPERATORS.get(op)
            if func is None:
                return right if UNTOTALLY_EVALUATED_OPS[op](left) else left
            else:
                return OPERATORS[op](left, right)
        case _:
            raise NotImplementedError(expr)

def run_stmt(ast, scope):
    match ast:
        case AttrSetter(obj, attrname, value):
            token = ast.token
            setattr(
                get_expr_value(obj, scope),
                attrname,
                get_expr_value(value, scope)
            )
        case VarSetter(varname, value):
            token = ast.token
            value = get_expr_value(value, scope)
            if varname == "...":
                varname: str = getattr(value, "__asname__", None)
                if varname is None:
                    varname = getattr(value, "__name__", None)
                if varname is None:
                    raise ValueError("Assigning to '...' requires a nameable object, "
                                     "with a __asname__ or __name__ attribute")
                elif not varname.isidentifier():
                    raise ValueError("Assigning to '...' requires a nameable object, "
                                     "with __asname__ or __name__  attribute that is a valid identifier")
            scope[varname] = value
        case Expr():
            return get_expr_value(ast, scope)

def run_block(ast: Block, scope):
    result = None
    for stmt in ast.statements:
        result = run_stmt(stmt, scope)
    if len(ast.statements) == 1:
        return result

def walk(exc):
    while exc:
        locals_ = exc.tb_frame.f_locals
        path = exc.tb_frame.f_code.co_filename
        line_number = exc.tb_lineno
        function_name = exc.tb_frame.f_code.co_name
        line = linecache.getline(path, line_number).lstrip()

        yield locals_, path, line_number, function_name, line
        exc = exc.tb_next

SCOPE_CACHE = {}

def run(ast: Block, ctx: Ctx, scope=None, return_scope=False):
    if scope is not None:
        pass
    elif not ctx.is_real_file:
        scope = Scope()
    elif ctx.path in SCOPE_CACHE:
        return SCOPE_CACHE[ctx.path]
    else:
        scope = Scope()
        SCOPE_CACHE[ctx.path] = scope

    DEBUG = ctx.debug or _DEBUG
    scope["__file__"] = ctx.path
    scope["__name__"] = ctx.file_name
    try:
        result = run_block(ast, scope)

    except Exception as e:
        message = "\n"
        tb = e.__traceback__
        pad = " "*2
        funcname = "<module>"
        last_filename, last_lineno, n = None, None, 0
        acc = 0
        for locals_, path, line_number, function_name, line in walk(tb):
            if not DEBUG and not locals_.get("__traceback_show__", True):
                continue
            if (path != __file__) or DEBUG:
                message += f"{pad}File \"{path}\", line {line_number}, in {function_name}\n{pad*2}{line}"

                if last_filename == path and last_lineno == line_number:
                    n += 1
                    if n > 5:
                        n = 5
                        acc += 1
                    elif acc:
                        message += f"{pad}[... {acc} more time\n]"
                        acc = 0
                last_lineno, last_filename = line_number, path

            if path == __file__:
                token = locals_.get('token', None)
                funcname = locals_.get('__funcname__', funcname)
                if token:
                    if DEBUG:
                        message += pad
                    if "__funcname__" in locals_:
                        funcname = locals_["__funcname__"]
                    message += f"{pad}File \"{ctx.path}\", line {token.line}, column {token.column}, in {funcname}\n"
                    line_indicator = show_line(token, token.ctx)
                    message += line_indicator + "\n"

                    if last_filename == ctx.path and last_lineno == token.line:
                        n += 1
                        if n > 5:
                            n = 5
                            acc += 1
                    elif acc:
                        message += f"{pad}[... {acc} more time\n]"
                        acc = 0
                    last_lineno, last_filename = token.line, ctx.path

        if e.__class__.__module__ == "builtins":
            message += f"{e.__class__.__name__}: {e}"
        else:
            message += f"{e.__class__.__module__}.{e.__class__.__name__}: {e}"
        raise update_wrapper(type(
            "RunningError",
            (e.__class__, ),
            {"__str__": lambda self: message, "__init__": lambda self, *_, **__: None}
        )(), e) from None
    else:
        if return_scope:
            return scope
        else:
            return result
