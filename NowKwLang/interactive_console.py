from collections import deque
from sys import stderr
import time

from NowKwLang.context import Ctx
from NowKwLang.lexer import lex, NewLine
from NowKwLang.parser import parse
from NowKwLang.run import run
from NowKwLang.modules.scope import Scope

class ConsoleInteracter:
    @classmethod
    def run(cls):
        return cls()

    def __init__(self):
        self.juste_asked_input = False
        self.chars = deque()
        self.ctx = Ctx("<console>", "", debug=False, is_real_file=False)
        del self.ctx.lines[:]
        tokens = iter(lex(self, self.ctx))
        scope = Scope()
        while True:
            toks = []
            while True:
                new_tok = next(tokens)
                if isinstance(new_tok, NewLine):
                    break
                toks.append(new_tok)
            self.juste_asked_input = False
            if not toks:
                continue
            try:
                ast = parse(iter(toks), self.ctx)
            except Exception as e:
                print("Traceback (most recent call last):", file=stderr)
                print(str(e).removeprefix("\n"), file=stderr)
                time.sleep(0.1)
                continue
            try:
                result = run(ast, self.ctx, scope=scope)
            except Exception as e:
                print("Traceback (most recent call last):", file=stderr)
                print(str(e).removeprefix("\n"), file=stderr)
                time.sleep(0.1)
                continue
            if result is not None:
                print(repr(result))
                time.sleep(0.1)

    def __next__(self):
        if not self.chars:
            prefix = "..." if self.juste_asked_input else "NkL"
            self.juste_asked_input = True
            line = input(f"{prefix} >>>")
            self.ctx.code += line + "\n"
            self.ctx.lines.append(line)
            self.chars.extend(line + "\n")
        return self.chars.popleft()

    def __iter__(self):
        return self
