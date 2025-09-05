import os
import pathlib
import sys
import unittest
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from unittest.mock import patch

from renamewheel.main import main

# Get the absolute path to the directory of this file
here = os.path.abspath(os.path.dirname(__file__))


def resource_path(resource_name):
    """Constructs an absolute path to a file in the 'resources' directory."""
    return os.path.join(here, "resources", resource_name)


def _mock_platform(linux=True):
    """Mocks sys.platform to simulate running on Linux or a non-Linux OS."""
    if linux:
        # To test the Linux-specific logic, we ensure sys.platform is 'linux'
        if sys.platform != "linux":
            sys.platform = "linux"
    else:
        # To test non-Linux paths, we can set it to another common platform
        sys.platform = "darwin"


class RenameTestCase(unittest.TestCase):

    def setUp(self):
        """Set up the test environment before each test."""
        # Change the current working directory to the resources folder
        os.chdir(resource_path(""))

    def _run_main_and_assert(self, argv, expected_code, expected_output, linux_platform=True):
        """
        Helper function to run the main script and assert its output and return code.

        Args:
            argv (list): A list of strings to mock for sys.argv.
            expected_code (int): The expected exit code from the main function.
            expected_output (str): The expected string printed to stdout.
            linux_platform (bool): If True, mock a Linux environment.
        """
        _mock_platform(linux_platform)
        captured_output = StringIO()
        captured_error = StringIO()

        # Patch sys.argv and redirect stdout to capture the output
        with patch('sys.argv', argv), redirect_stdout(captured_output), redirect_stderr(captured_error):
            result = main()

        output = captured_output.getvalue()
        output += captured_error.getvalue()

        # Assert that the return code and captured output match expectations
        self.assertEqual(expected_code, result, f"Expected return code {expected_code}, but got {result}.")
        if expected_output is not None:
            self.assertEqual(expected_output, output, f"Expected output did not match.")

    @patch('sys.argv', ['main.py'])
    def test_arg_error(self):
        """Test that the script exits when no arguments are provided."""
        captured_error = StringIO()
        with redirect_stderr(captured_error):
            self.assertRaises(SystemExit, main)

    def test_wrong_platform(self):
        """Test silent failure on a non-Linux platform."""
        self._run_main_and_assert(['main.py', 'some-wheel'], 1, "", linux_platform=False)

    def test_wrong_platform_verbose(self):
        """Test verbose failure message on a non-Linux platform."""
        self._run_main_and_assert(
            ['main.py', '-v', 'some-wheel'], 1, "Error: This tool only supports Linux.\n", linux_platform=False
        )

    def test_non_existent(self):
        """Test silent failure for a wheel that does not exist."""
        self._run_main_and_assert(['main.py', 'some-wheel'], 2, "")

    def test_non_existent_verbose(self):
        """Test verbose failure for a non-existent wheel."""
        self._run_main_and_assert(
            ['main.py', '-v', 'some-wheel'], 2, "Cannot access 'some-wheel'. No such file.\n"
        )

    def test_not_a_platform_wheel(self):
        """Test silent failure for a file that is not a platform wheel."""
        self._run_main_and_assert(['main.py', "this-0.1.0-py3-not-wheel.whl"], 3, "")

    def test_not_a_platform_wheel_verbose(self):
        """Test verbose failure for a file that is not a platform wheel."""
        expected_output = "'this-0.1.0-py3-not-wheel.whl' is not a zip file.\n"
        self._run_main_and_assert(
            ['main.py', '-v', "this-0.1.0-py3-not-wheel.whl"],
            3,
            expected_output
        )

    def test_not_a_wheel_libc(self):
        """Test silent failure for a pure Python wheel."""
        self._run_main_and_assert(['main.py', "renamewheel-0.3.1-py3-none-any.whl"], 3, "")

    def test_not_a_wheel_libc_verbose(self):
        """Test verbose failure for a pure Python wheel."""
        self._run_main_and_assert(
            ['main.py', '-v', "renamewheel-0.3.1-py3-none-any.whl"],
            3,
            "'renamewheel-0.3.1-py3-none-any.whl' is not a valid platform wheel.\n"
        )

    def test_platform_wheel(self):
        """Test successful rename of a platform wheel."""
        wheel = "simple_manylinux_demo-4.0-cp312-cp312-manylinux_2_5_x86_64.whl"
        self._run_main_and_assert(['main.py', wheel], 0, "")

    def test_platform_wheel_verbose(self):
        """Test verbose output for a successful rename."""
        wheel = "simple_manylinux_demo-4.0-cp312-cp312-manylinux_2_5_x86_64.whl"
        expected_output = f"Renaming '{wheel}' to '{wheel}'.\n"
        expected_output = "Name and location haven't changed, doing nothing.\n"
        self._run_main_and_assert(['main.py', '-v', wheel], 0, expected_output)

    def test_platform_wheel_working_dir(self):
        """Test copying and renaming to a different working directory."""
        wheel = "simple_manylinux_demo-4.0-cp312-cp312-manylinux_2_5_x86_64.whl"
        target_dir = resource_path('..')
        target_file = os.path.join(target_dir, wheel)

        self._run_main_and_assert(['main.py', '-w', target_dir, wheel], 0, "")

        # Clean up the copied file
        self.assertTrue(os.path.exists(target_file))
        os.remove(target_file)

    def test_platform_wheel_working_dir_verbose(self):
        """Test verbose output when copying and renaming to a different directory."""
        wheel = "simple_manylinux_demo-4.0-cp312-cp312-manylinux_2_5_x86_64.whl"
        target_dir = resource_path('..')
        target_file = os.path.join(target_dir, wheel)
        expected_output = f"Copying '{resource_path(wheel)}' to '{target_file}'.\n"

        self._run_main_and_assert(['main.py', '-v', '-w', target_dir, wheel], 0, expected_output)

        # Clean up the copied file
        self.assertTrue(os.path.exists(target_file))
        os.remove(target_file)

    def test_platform_wheel_same_working_dir(self):
        """Test successful rename when the target directory is the same as the source."""
        wheel = "simple_manylinux_demo-4.0-cp312-cp312-manylinux_2_5_x86_64.whl"
        target_dir = resource_path('')
        self._run_main_and_assert(['main.py', '-w', target_dir, wheel], 0, "")

    def test_platform_wheel_same_working_dir_verbose(self):
        """Test verbose output when the target directory is the same and the name is unchanged."""
        wheel = "simple_manylinux_demo-4.0-cp312-cp312-manylinux_2_5_x86_64.whl"
        target_dir = resource_path('')
        expected_output = "Name and location haven't changed, doing nothing.\n"
        self._run_main_and_assert(['main.py', '-v', '-w', target_dir, wheel], 0, expected_output)

    def test_platform_wheel_rename(self):
        """Test successful rename when the target directory is the same as the source."""
        wheel = "Simple.Manylinux.Demo-4.0-cp313-cp313-manylinux_2_5_x86_64.whl"
        self._run_main_and_assert(['main.py', wheel], 0, "")
        # Restore renamed file.
        destination_path = pathlib.Path(resource_path('simple_manylinux_demo-4.0-cp313-cp313-manylinux_2_5_x86_64.whl'))
        source_path = pathlib.Path(resource_path(wheel))
        destination_path.rename(source_path)

    def test_platform_wheel_rename_verbose(self):
        """Test successful rename when the target directory is the same as the source."""
        wheel = "Simple.Manylinux.Demo-4.0-cp313-cp313-manylinux_2_5_x86_64.whl"
        expected_output = f"Renaming {wheel!r} to 'simple_manylinux_demo-4.0-cp313-cp313-manylinux_2_5_x86_64.whl'.\n"
        self._run_main_and_assert(['main.py', '-v', wheel], 0, expected_output)
        # Restore renamed file.
        destination_path = pathlib.Path(resource_path('simple_manylinux_demo-4.0-cp313-cp313-manylinux_2_5_x86_64.whl'))
        source_path = pathlib.Path(resource_path(wheel))
        destination_path.rename(source_path)

    def test_platform_wheel_invalid_output_dir(self):
        """Test successful rename when the target directory is the same as the source."""
        wheel = "simple_manylinux_demo-4.0-cp312-cp312-manylinux_2_5_x86_64.whl"
        target_dir = resource_path('die')
        self._run_main_and_assert(['main.py', '-w', target_dir, wheel], 4, "")

    def test_platform_wheel_invalid_output_dir_verbose(self):
        """Test successful rename when the target directory is the same as the source."""
        wheel = "simple_manylinux_demo-4.0-cp312-cp312-manylinux_2_5_x86_64.whl"
        target_dir = resource_path('die')
        expected_output = f"Output directory '{target_dir}' does not exist.\n"
        self._run_main_and_assert(['main.py', '-v', '-w', target_dir, wheel], 4, expected_output)

    def test_platform_wheel_invalid_architecture(self):
        wheel = "robotpy_hal-2025.3.2.3-cp313-cp313-linux_x86_64.whl"
        expected_output = ""
        self._run_main_and_assert(['main.py', wheel], 0, expected_output)
        # Restore renamed file.
        destination_path = pathlib.Path(resource_path('robotpy_hal-2025.3.2.3-cp313-cp313-manylinux_2_34_x86_64.whl'))
        source_path = pathlib.Path(resource_path(wheel))
        destination_path.rename(source_path)


if __name__ == "__main__":
    unittest.main()
