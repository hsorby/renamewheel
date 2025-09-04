import os
import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from renamewheel.main import main

here = os.path.abspath(os.path.dirname(__file__))


def resource_path(resource_name):
    return os.path.join(here, "resources", resource_name)


def _mock_platform(linux=True):
    if linux and sys.platform != "linux":
        sys.platform = "linux"
    elif not linux:
        sys.platform = "darwin"


class RenameTestCase(unittest.TestCase):

    def setUp(self):
        os.chdir(resource_path(""))

    @patch('sys.argv', ['main.py'])
    def test_arg_error(self):
        self.assertRaises(SystemExit, main)

    @patch('sys.argv', ['main.py', 'some-wheel'])
    def test_wrong_platform(self):
        _mock_platform(False)
        captured_output = StringIO()

        with redirect_stdout(captured_output):
            result = main()

        output = captured_output.getvalue()

        self.assertEqual(1, result)
        self.assertEqual("", output)

    @patch('sys.argv', ['main.py', '-v', 'some-wheel'])
    def test_wrong_platform_verbose(self):
        _mock_platform(False)
        captured_output = StringIO()

        with redirect_stdout(captured_output):
            result = main()

        output = captured_output.getvalue()

        expected_output = "Error: This tool only supports Linux\n"
        self.assertEqual(1, result)
        self.assertEqual(expected_output, output)

    @patch('sys.argv', ['main.py', 'some-wheel'])
    def test_non_existent(self):
        _mock_platform()
        captured_output = StringIO()

        with redirect_stdout(captured_output):
            result = main()

        output = captured_output.getvalue()

        expected_output = ""
        self.assertEqual(2, result)
        self.assertEqual(expected_output, output)

    @patch('sys.argv', ['main.py', '-v', 'some-wheel'])
    def test_non_existent_verbose(self):
        _mock_platform()
        captured_output = StringIO()

        with redirect_stdout(captured_output):
            result = main()

        output = captured_output.getvalue()

        expected_output = "Cannot access 'some-wheel'. No such file.\n"
        self.assertEqual(2, result)
        self.assertEqual(expected_output, output)

    @patch('sys.argv', ['main.py', "this-0.1.0-py3-not-wheel.whl"])
    def test_not_a_platform_wheel(self):
        _mock_platform()
        captured_output = StringIO()

        with redirect_stdout(captured_output):
            result = main()

        output = captured_output.getvalue()

        expected_output = ""
        self.assertEqual(3, result)
        self.assertEqual(expected_output, output)

    @patch('sys.argv', ['main.py', '-v', "this-0.1.0-py3-not-wheel.whl"])
    def test_not_a_platform_wheel_verbose(self):
        _mock_platform()
        captured_output = StringIO()

        with redirect_stdout(captured_output):
            result = main()

        output = captured_output.getvalue()

        expected_output = "This does not look like a platform wheel 'this-0.1.0-py3-not-wheel.whl'.\n"
        self.assertEqual(3, result)
        self.assertEqual(expected_output, output)

    @patch('sys.argv', ['main.py', "renamewheel-0.3.1-py3-none-any.whl"])
    def test_not_a_wheel_libc(self):
        _mock_platform()
        captured_output = StringIO()

        with redirect_stdout(captured_output):
            result = main()

        output = captured_output.getvalue()

        expected_output = ""
        self.assertEqual(3, result)
        self.assertEqual(expected_output, output)

    @patch('sys.argv', ['main.py', '-v', "renamewheel-0.3.1-py3-none-any.whl"])
    def test_not_a_wheel_libc_verbose(self):
        _mock_platform()
        captured_output = StringIO()

        with redirect_stdout(captured_output):
            result = main()

        output = captured_output.getvalue()

        expected_output = f"This does not look like a platform wheel 'renamewheel-0.3.1-py3-none-any.whl'.\n"
        self.assertEqual(3, result)
        self.assertEqual(expected_output, output)

    @patch('sys.argv', ['main.py', "simple_manylinux_demo-4.0-cp312-cp312-manylinux_2_5_x86_64.whl"])
    def test_platform_wheel(self):
        _mock_platform()
        captured_output = StringIO()

        with redirect_stdout(captured_output):
            result = main()

        output = captured_output.getvalue()

        expected_output = ""
        self.assertEqual(0, result)
        self.assertEqual(expected_output, output)

    @patch('sys.argv', ['main.py', '-v', "simple_manylinux_demo-4.0-cp312-cp312-manylinux_2_5_x86_64.whl"])
    def test_platform_wheel_verbose(self):
        _mock_platform()
        captured_output = StringIO()

        with redirect_stdout(captured_output):
            result = main()

        output = captured_output.getvalue()

        expected_output = f"Renaming 'simple_manylinux_demo-4.0-cp312-cp312-manylinux_2_5_x86_64.whl' to 'simple_manylinux_demo-4.0-cp312-cp312-manylinux_2_5_x86_64.whl'.\n"
        self.assertEqual(0, result)
        self.assertEqual(expected_output, output)

    @patch('sys.argv', ['main.py', '-w', resource_path('..'), 'simple_manylinux_demo-4.0-cp312-cp312-manylinux_2_5_x86_64.whl'])
    def test_platform_wheel_working_dir(self):
        _mock_platform()
        captured_output = StringIO()

        with redirect_stdout(captured_output):
            result = main()

        output = captured_output.getvalue()

        expected_output = ""
        self.assertEqual(0, result)
        self.assertEqual(expected_output, output)
        os.remove(resource_path(os.path.join('..', 'simple_manylinux_demo-4.0-cp312-cp312-manylinux_2_5_x86_64.whl')))

    @patch('sys.argv', ['main.py', '-v', '-w', resource_path('..'), "simple_manylinux_demo-4.0-cp312-cp312-manylinux_2_5_x86_64.whl"])
    def test_platform_wheel_working_dir_verbose(self):
        _mock_platform()
        captured_output = StringIO()

        with redirect_stdout(captured_output):
            result = main()

        output = captured_output.getvalue()

        target_file = resource_path(os.path.join('..', 'simple_manylinux_demo-4.0-cp312-cp312-manylinux_2_5_x86_64.whl'))
        expected_output = f"Copying 'simple_manylinux_demo-4.0-cp312-cp312-manylinux_2_5_x86_64.whl' to {target_file!r}.\n"
        self.assertEqual(0, result)
        self.assertEqual(expected_output, output)
        os.remove(target_file)

    @patch('sys.argv', ['main.py', '-w', resource_path(''), 'simple_manylinux_demo-4.0-cp312-cp312-manylinux_2_5_x86_64.whl'])
    def test_platform_wheel_same_working_dir(self):
        _mock_platform()
        captured_output = StringIO()

        with redirect_stdout(captured_output):
            result = main()

        output = captured_output.getvalue()

        expected_output = ""
        self.assertEqual(0, result)
        self.assertEqual(expected_output, output)

    @patch('sys.argv', ['main.py', '-v', '-w', resource_path(''), "simple_manylinux_demo-4.0-cp312-cp312-manylinux_2_5_x86_64.whl"])
    def test_platform_wheel_same_working_dir_verbose(self):
        _mock_platform()
        captured_output = StringIO()

        with redirect_stdout(captured_output):
            result = main()

        output = captured_output.getvalue()

        expected_output = "Name hasn't changed, doing nothing.\n"
        self.assertEqual(0, result)
        self.assertEqual(expected_output, output)


if __name__ == "__main__":
    unittest.main()
