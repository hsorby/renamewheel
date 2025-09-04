import argparse
import os.path
import pathlib
import sys

from os.path import basename, isfile
from shutil import copyfile

from auditwheel.error import NonPlatformWheel, WheelToolsError
from auditwheel.wheel_abi import analyze_wheel_abi
from auditwheel.wheeltools import get_wheel_architecture, get_wheel_libc

def _parse_args():
    p = argparse.ArgumentParser(description="Rename Linux Python wheels.")
    p.add_argument("WHEEL_FILE", help="Path to wheel file.")
    p.add_argument("-w", "--working-dir", help="Working directory")

    return p.parse_args()


def _analyse_wheel(wheel_file):
    if not isfile(wheel_file):
        print(f"cannot access {wheel_file}. No such file")
        return 2

    try:
        arch = get_wheel_architecture(wheel_file)
    except (WheelToolsError, NonPlatformWheel):
        arch = None

    try:
        libc = get_wheel_libc(wheel_file)
    except WheelToolsError:
        libc = None

    try:
        winfo = analyze_wheel_abi(libc, arch, pathlib.Path(wheel_file), frozenset(), True, True)
    except NonPlatformWheel:
        print("This does not look like a platform wheel")
        return 3

    return winfo.overall_policy.name


def main():
    if sys.platform != "linux":
        print("Error: This tool only supports Linux")
        return 1

    args = _parse_args()

    tag = _analyse_wheel(args.WHEEL_FILE)
    if isinstance(tag, int):
        return tag

    file_name = basename(args.WHEEL_FILE)

    parts = file_name.split("-")
    parts[-1] = tag
    renamed_file_name = "-".join(parts) + ".whl"

    if args.working_dir:
        renamed_wheel_file = os.path.join(args.working_dir, renamed_file_name)
    else:
        renamed_wheel_file = os.path.join(os.path.dirname(args.WHEEL_FILE), renamed_file_name)

    print(f"Renaming '{args.WHEEL_FILE}' to '{renamed_wheel_file}'.")
    copyfile(args.WHEEL_FILE, renamed_wheel_file)
    return 0


if __name__ == "__main__":
    main()
