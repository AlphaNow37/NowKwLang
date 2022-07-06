from NowKwLang.NkL_std_libs.exceptions import raise_, Try
from NowKwLang.NkL_std_libs.errors import SyntaxError
from NowKwLang.NkL_std_libs.funcs import func
from NowKwLang.NkL_std_libs.loops import For, While
from NowKwLang.NkL_std_libs.imports import pyimport, nklimport, importer
from NowKwLang.NkL_std_libs.constants import *
from NowKwLang.NkL_std_libs.conditions import If
from NowKwLang.NkL_std_libs.utils import map, filter, reduce, inject_code
from NowKwLang.NkL_std_libs.namespaces_withs import Namespace, With

class Scope(dict):
    """
    A scope that contain the variables of the frame, with a superscope to fallback if a var is not found
    """
    def __init__(self, superscope=None):
        if superscope is None:
            superscope = builtin_scope
        self.superscope = superscope
        super().__init__(locals=self.locals, vars=self.vars)

    def locals(self):
        return self

    def vars(self, obj=None):
        if obj is None:
            return self.locals()
        else:
            return vars(obj)

    def __missing__(self, key):
        return self.superscope[key]

    def __getitem__(self, item):
        if item == "...":
            return empty_value
        try:
            return super(Scope, self).__getitem__(item)
        except NameError as e:
            raise NameError(str(e)) from None

class _BuiltinScope(dict):
    def __init__(self):
        super(_BuiltinScope, self).__init__(__builtins__ | {
            "Scope": Scope,
            "__builtins__": self,
            "SyntaxError": SyntaxError,
            "raise": raise_,
            "try": Try, "Try": Try,
            "func": func,
            "for": For, "For": For,
            "while": While, "While": While,
            "import": importer, "pyimport": pyimport, "nkl_import": nklimport,
            "...": empty_value,
            "empty_value": empty_value,
            "EmptyValue": EmptyValue,
            "if": If, "If": If,
            "map": map, "filter": filter, "reduce": reduce,
            "inject_code": inject_code,
            "pass": lambda *args: args,
            "namespace": Namespace, "with": With,
        })

    def __missing__(self, key):
        raise NameError(f"Variable {key!r} not defined") from None

    def __getattr__(self, item):
        return self[item]

builtin_scope = _BuiltinScope()

if __name__ == '__main__':
    print(dict(builtin_scope))
