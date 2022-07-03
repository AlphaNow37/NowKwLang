import argparse
import pathlib
import sys

import NowKwLang


parser = argparse.ArgumentParser(description="NowKwLang")
parser.add_argument("-file", help="file to run")
parser.add_argument("-d", "--debug", action="store_true", help="debug mode")

def main(argv):
    args = parser.parse_args(argv[1:])

    if args.file is None:
        NowKwLang.ConsoleInteracter.run()
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
    print("Running ...")
    NowKwLang.run_code(filename=file_path, debug=args.debug)
    return 0

if __name__ == '__main__':
    exit(main(sys.argv))
