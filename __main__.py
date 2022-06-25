import alpha_lang

code = """
5()
"""
print(repr(code))
output = alpha_lang.parse(code)
print(output)
output.run()
