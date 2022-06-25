from NowKwLang.parser._stream import TokenStream
from NowKwLang.parser.statment import parse_statment
from NowKwLang.errors import ParsingError

from NowKwLang.lexer import NewStmt

class Block:
    def __init__(self):
        self.statements = []

    def add(self, statement):
        self.statements.append(statement)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.statements}>"

def parse_block(stream: TokenStream):
    first = True
    block = Block()
    while (token := stream.get(0)) is not None:
        if isinstance(token, NewStmt):
            stream.consume(1)
            if isinstance(stream.get(0), NewStmt):
                continue
        else:
            if not first:
                raise ParsingError(token, "Expected a end of statement", stream.ctx)
        first = False
        stat = parse_statment(stream)
        if stat is not None:
            block.add(stat)
    return block
