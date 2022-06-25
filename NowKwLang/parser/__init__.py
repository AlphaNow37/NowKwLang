from NowKwLang.parser._stream import TokenStream
from NowKwLang.parser import collections as _  # circular import
from NowKwLang.parser.block import parse_block
from NowKwLang.context import Ctx

def parse(tokens, code: str, ctx: Ctx):
    stream = TokenStream(tokens, code, ctx)
    return parse_block(stream)

if __name__ == '__main__':
    from NowKwLang.lexer import lex
    code = '''
    print(1 + 2)
    '''
    ctx = Ctx("<string>", code)
    tokens = lex(code, ctx)
    stream = TokenStream(tokens, code, ctx)
    print(stream[:5])
