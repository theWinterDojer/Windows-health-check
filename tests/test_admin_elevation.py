"""Regression tests for UAC elevation argument construction."""

import subprocess
import unittest

from utils.admin import build_elevation_command


class ElevationCommandTests(unittest.TestCase):
    """Tests for Windows-safe ShellExecuteW executable/argument values."""

    def test_script_mode_quotes_script_path_and_arguments_with_spaces(self):
        """Script relaunch arguments should preserve paths and values with spaces."""
        executable, arguments = build_elevation_command(
            executable="C:\\Program Files\\Python312\\python.exe",
            argv=[
                "C:\\Users\\Alice Smith\\Windows Health Check\\main.py",
                "--config",
                "C:\\Users\\Alice Smith\\settings file.json",
            ],
            frozen=False,
        )

        self.assertEqual(executable, "C:\\Program Files\\Python312\\python.exe")
        self.assertEqual(
            arguments,
            subprocess.list2cmdline([
                "C:\\Users\\Alice Smith\\Windows Health Check\\main.py",
                "--config",
                "C:\\Users\\Alice Smith\\settings file.json",
            ]),
        )

    def test_frozen_mode_quotes_only_runtime_arguments(self):
        """Packaged relaunch should pass executable separately and quote only extra args."""
        executable, arguments = build_elevation_command(
            executable="C:\\Apps\\Windows Health Check Tool.exe",
            argv=[
                "C:\\Apps\\Windows Health Check Tool.exe",
                "--log-file",
                "C:\\Users\\Alice Smith\\health check.log",
            ],
            frozen=True,
        )

        self.assertEqual(executable, "C:\\Apps\\Windows Health Check Tool.exe")
        self.assertEqual(
            arguments,
            subprocess.list2cmdline([
                "--log-file",
                "C:\\Users\\Alice Smith\\health check.log",
            ]),
        )
        self.assertNotIn("Windows Health Check Tool.exe", arguments)

    def test_returns_empty_argument_string_when_no_extra_args_in_frozen_mode(self):
        """ShellExecuteW accepts an empty parameter string for packaged no-arg launches."""
        executable, arguments = build_elevation_command(
            executable="C:\\Apps\\Windows Health Check Tool.exe",
            argv=["C:\\Apps\\Windows Health Check Tool.exe"],
            frozen=True,
        )

        self.assertEqual(executable, "C:\\Apps\\Windows Health Check Tool.exe")
        self.assertEqual(arguments, "")


if __name__ == "__main__":
    unittest.main()
