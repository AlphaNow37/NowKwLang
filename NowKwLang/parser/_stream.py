from typing import Iterator
from collections import deque

from NowKwLang.lexer import Token, NewLine
from NowKwLang.context import Ctx

class TokenStream:
    def __init__(self, gen, code: str, ctx: Ctx):
        self.cache = deque()
        self.gen: Iterator[Token] = gen
        self.code = code
        self.ctx = ctx

    def consume(self, n=1):
        for _ in range(n):
            if self.cache:
                self.cache.popleft()
            else:
                next(self.gen)

    def __getitem__(self, item) -> Token | list[Token]:
        if isinstance(item, int):
            if item >= len(self.cache):
                for x in range(item - len(self.cache) + 1):
                    self.cache.append(next(self.gen))
            return self.cache[item]
        elif isinstance(item, slice):
            assert item.stop is not None
            return [self[i] for i in range(item.start or 0, item.stop, item.step or 1)]

    def get(self, i=0) -> Token | None:
        try:
            return self[i]
        except (StopIteration, IndexError):
            return None

    def sub(self, tokens, remove_spaces=True):
        if remove_spaces:
            tokens = [tok for tok in tokens if not isinstance(tok, NewLine)]
        return TokenSubStream(self.ctx, tokens, self.code)

class TokenSubStream(TokenStream):
    def __init__(self, ctx, tokens, code):
        super().__init__(iter(()), code, ctx)
        self.cache = deque(tokens)
