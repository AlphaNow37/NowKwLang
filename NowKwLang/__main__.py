"""
__main__ manage the command-line interface.
usages:
python NowKwLang -h/--help           -> help interface
python NowKwLang -d/--debug <file>   -> run file in debug mode
python NowKwLang <file>              -> run file
python NowKwLang -d/--debug          -> run interactive console in debug mode
python NowKwLang                     -> run interactive console
"""
import argparse
import pathlib
import sys

actual_file = pathlib.Path(__file__).resolve()
if str(actual_file.parent) in sys.path:
    sys.path.remove(str(actual_file.parent))
    sys.path.append(str(actual_file.parent.parent))

import NowKwLang


parser = argparse.ArgumentParser(description="NowKwLang")
parser.add_argument("file", help="file to run", nargs="?")
parser.add_argument("-d", "--debug", action="store_true", help="debug mode")

def main():
    args = parser.parse_args()

    if args.file is None:
        NowKwLang.ConsoleInteracter.run(debug=args.debug)
        return 0

    file_path = pathlib.Path(args.file)
    if not file_path.exists():
        print(f"File {file_path} not found")
        return 1
    if not file_path.is_file():
        print(f"{file_path} is not a file")
        return 2
    if file_path.suffix != ".NkL":
        print(f"{file_path} is not a .NkL file")
        return 3
    NowKwLang.run_code(filename=file_path, debug=args.debug)
    return 0

if __name__ == '__main__':
    exit(main())
