import argparse
import os
import sys

from auditwheel.wheel_abi import NonPlatformWheel, analyze_wheel_abi
from os.path import isfile


def _parse_args():
    p = argparse.ArgumentParser(description="Rename Linux Python wheels.")
    p.add_argument("WHEEL_FILE", help="Path to wheel file.")
    return p.parse_args()


def _analyse_wheel(wheel_file):
    if not isfile(wheel_file):
        print(f"cannot access {wheel_file}. No such file")
        return 2

    try:
        winfo = analyze_wheel_abi(wheel_file)
    except NonPlatformWheel:
        print("This does not look like a platform wheel")
        return 3

    return {"from": winfo.overall_tag, "to": winfo.sym_tag}


def main():
    if sys.platform != "linux":
        print("Error: This tool only supports Linux")
        return 1

    args = _parse_args()

    result = _analyse_wheel(args.WHEEL_FILE)
    if isinstance(result, int):
        return result

    renamed_wheel_file = args.WHEEL_FILE.replace(result["from"], result["to"])

    print(f"Renaming '{args.WHEEL_FILE}' to '{renamed_wheel_file}'.")
    os.rename(args.WHEEL_FILE, renamed_wheel_file)
    return 0


if __name__ == "__main__":
    main()
