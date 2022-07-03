import subprocess


PATH = "examples/import_A.NkL"
DEBUGGING = False

subprocess.call(["python", "NowKwLang", PATH] + (["-d"] if DEBUGGING else []))
