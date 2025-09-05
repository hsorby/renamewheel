import argparse
import os.path
import pathlib
import sys
import zipfile
from contextlib import redirect_stderr, nullcontext
from io import StringIO
from shutil import copyfile

from auditwheel.error import NonPlatformWheel, WheelToolsError
from auditwheel.wheel_abi import analyze_wheel_abi
from auditwheel.wheeltools import get_wheel_architecture, get_wheel_libc
from packaging.utils import InvalidWheelFilename, parse_wheel_filename

# --- Constants for Exit Codes ---
EXIT_SUCCESS = 0
EXIT_WRONG_PLATFORM = 1
EXIT_FILE_NOT_FOUND = 2
EXIT_NOT_PLATFORM_WHEEL = 3
EXIT_OUTPUT_DIRECTORY_NOT_FOUND = 4


# --- Custom Exceptions ---
class RenameWheelError(Exception):
    """Base exception for this script."""


class WheelNotFoundError(RenameWheelError):
    """Raised when the wheel file does not exist."""


class NotPlatformWheelError(RenameWheelError):
    """Raised when the file is not a valid platform wheel."""


def _parse_args() -> argparse.Namespace:
    """Parses command-line arguments using pathlib for paths."""
    p = argparse.ArgumentParser(description="Rename Linux Python wheels based on their ABI tag.")
    p.add_argument("WHEEL_FILE", type=pathlib.Path, help="Path to wheel file.")
    p.add_argument("-v", "--verbose", action="store_true", help="Print out messages to the console.")
    p.add_argument("-w", "--working-dir", type=pathlib.Path, help="Copy the renamed wheel to this directory.")
    return p.parse_args()


def _get_aspect(fcn, str_path, verbose):
    aspect = None
    try:
        captured_error = StringIO()
        context_manager = nullcontext() if verbose else redirect_stderr(captured_error)
        with context_manager:
            aspect = fcn(str_path)
    except (WheelToolsError, NonPlatformWheel):
        pass

    return aspect


def _analyse_wheel_abi_tag(wheel_path: pathlib.Path, verbose) -> str:
    """
    Analyzes a wheel file to determine its platform ABI tag.

    Args:
        wheel_path: The path to the wheel file.

    Returns:
        The determined platform ABI tag (e.g., 'manylinux_2_17_x86_64').

    Raises:
        WheelNotFoundError: If the wheel_path does not point to a file.
        NotPlatformWheelError: If the file is not a valid platform wheel.
    """
    if not wheel_path.is_file():
        raise WheelNotFoundError(f"Cannot access '{wheel_path}'. No such file.")

    if not zipfile.is_zipfile(wheel_path):
        raise NotPlatformWheelError(f"'{wheel_path.name}' is not a zip file.")

    str_path = str(wheel_path)
    arch = _get_aspect(get_wheel_architecture, str_path, verbose)
    libc = _get_aspect(get_wheel_libc, str_path, verbose)

    try:
        captured_error = StringIO()
        context_manager = nullcontext() if verbose else redirect_stderr(captured_error)
        with context_manager:
            winfo = analyze_wheel_abi(libc, arch, wheel_path, frozenset(), True, True)
    except NonPlatformWheel as e:
        raise NotPlatformWheelError(f"'{wheel_path.name}' is not a valid platform wheel.") from e

    return winfo.overall_policy.name


def _generate_new_filename(original_path: pathlib.Path, new_platform_tag: str) -> str:
    """
    Generates a new wheel filename with an updated platform tag using robust parsing.

    Args:
        original_path: The path to the original wheel file.
        new_platform_tag: The new platform tag to use.

    Returns:
        The new filename string.

    Raises:
        NotPlatformWheelError: If the original filename cannot be parsed.
    """
    original_filename = original_path.name
    name, version, build, tags = parse_wheel_filename(original_path.name)

    # Assume a single, primary tag for platform wheels and replace its platform part
    old_tag = next(iter(tags))

    # Workaround for parse_wheel_filename breaking wheel name.
    name = name.replace('-', '_')

    build_part = f"-{build}" if build else ""

    return f"{name}-{version}{build_part}-{old_tag.interpreter}-{old_tag.abi}-{new_platform_tag}.whl"


def main() -> int:
    """Main entry point for the script."""
    args = _parse_args()

    if sys.platform != "linux":
        if args.verbose:
            print("Error: This tool only supports Linux.", file=sys.stderr)
        return EXIT_WRONG_PLATFORM

    try:
        new_platform_tag = _analyse_wheel_abi_tag(args.WHEEL_FILE, args.verbose)
        new_filename = _generate_new_filename(args.WHEEL_FILE, new_platform_tag)
    except (WheelNotFoundError, NotPlatformWheelError) as e:
        if args.verbose:
            print(str(e), file=sys.stderr)
        return EXIT_FILE_NOT_FOUND if isinstance(e, WheelNotFoundError) else EXIT_NOT_PLATFORM_WHEEL

    source_path = args.WHEEL_FILE.resolve()

    # Determine the destination path
    output_dir = args.working_dir if args.working_dir is not None else source_path.parent
    destination_path = output_dir / new_filename

    if source_path == destination_path.resolve():
        if args.verbose:
            print("Name and location haven't changed, doing nothing.")
        return EXIT_SUCCESS

    if not os.path.isdir(output_dir):
        if args.verbose:
            print(f"Output directory '{output_dir}' does not exist.", file=sys.stderr)
        return EXIT_OUTPUT_DIRECTORY_NOT_FOUND

    if args.working_dir is not None:
        if args.verbose:
            print(f"Copying '{source_path}' to '{destination_path}'.")
        copyfile(source_path, destination_path)
    else:
        if args.verbose:
            print(f"Renaming '{source_path.name}' to '{destination_path.name}'.")
        source_path.rename(destination_path)

    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
