import subprocess


PATH = "examples/test.NkL"
DEBUGGING = False

subprocess.call(["python", "NowKwLang", PATH] + (["-d"] if DEBUGGING else []))
