import argparse
import os
import os.path
import pathlib
import sys

from os.path import basename, isfile
from shutil import copyfile

from auditwheel.error import NonPlatformWheel, WheelToolsError
from auditwheel.wheel_abi import analyze_wheel_abi
from auditwheel.wheeltools import get_wheel_architecture, get_wheel_libc
from packaging.utils import InvalidWheelFilename


def _parse_args():
    p = argparse.ArgumentParser(description="Rename Linux Python wheels.")
    p.add_argument("WHEEL_FILE", help="Path to wheel file.")
    p.add_argument("-v", "--verbose", action="store_true", help="Print out messages to the console.")
    p.add_argument("-w", "--working-dir", help="Copy file to working directory")

    return p.parse_args()


def _analyse_wheel(wheel_file, verbose):
    if not isfile(wheel_file):
        if verbose:
            print(f"Cannot access {wheel_file!r}. No such file.")
        return 2

    try:
        arch = get_wheel_architecture(wheel_file)
    except (WheelToolsError, NonPlatformWheel):
        arch = None

    try:
        libc = get_wheel_libc(wheel_file)
    except WheelToolsError:
        libc = None

    if arch is None or libc is None:
        if verbose:
            print(f"This does not look like a platform wheel {wheel_file!r}.")
        return 3

    winfo = analyze_wheel_abi(libc, arch, pathlib.Path(wheel_file), frozenset(), True, True)
    return winfo.overall_policy.name


def main():
    args = _parse_args()

    if sys.platform != "linux":
        if args.verbose:
            print("Error: This tool only supports Linux")
        return 1

    tag = _analyse_wheel(args.WHEEL_FILE, args.verbose)
    if isinstance(tag, int):
        return tag

    file_name = basename(args.WHEEL_FILE)

    parts = file_name.split("-")
    parts[-1] = tag
    renamed_file_name = "-".join(parts) + ".whl"

    if args.working_dir:
        renamed_wheel_file = os.path.join(args.working_dir, renamed_file_name)
        if os.path.join(os.path.abspath(os.curdir), args.WHEEL_FILE) != renamed_wheel_file:
            if args.verbose:
                print(f"Copying {args.WHEEL_FILE!r} to {renamed_wheel_file!r}.")
            copyfile(args.WHEEL_FILE, renamed_wheel_file)
        elif args.verbose:
            print(f"Name hasn't changed, doing nothing.")
    else:
        renamed_wheel_file = os.path.join(os.path.dirname(args.WHEEL_FILE), renamed_file_name)
        if args.verbose:
            print(f"Renaming {args.WHEEL_FILE!r} to {renamed_wheel_file!r}.")
        os.rename(args.WHEEL_FILE, renamed_file_name)

    return 0


if __name__ == "__main__":
    main()  # pragma: no cover
