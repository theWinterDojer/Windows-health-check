"""Regression tests for CHKDSK drive validation."""

import unittest

from commands import CommandResult, HealthCheckCommands, WindowsCommandExecutor, normalize_drive_letter


class RecordingExecutor(WindowsCommandExecutor):
    """Capture command strings without launching external tools."""

    def __init__(self):
        self.commands = []

    def execute_command(self, command: str, shell: bool = True) -> CommandResult:
        self.commands.append(command)
        return CommandResult(command, 0, "")


class ChkdskDriveValidationTests(unittest.TestCase):
    """Tests for safe CHKDSK drive argument handling."""

    def test_normalize_drive_letter_accepts_single_letter_with_optional_colon(self):
        """Single drive letters should normalize to uppercase with a colon."""
        for raw_drive in ("C", "C:", "c", "c:", " z ", "z: "):
            with self.subTest(raw_drive=raw_drive):
                self.assertEqual(normalize_drive_letter(raw_drive), f"{raw_drive.strip()[0].upper()}:")

    def test_normalize_drive_letter_rejects_malformed_or_unsafe_values(self):
        """Only a single Windows drive letter with optional colon is accepted."""
        unsafe_values = [
            "",
            " ",
            "CC",
            "C::",
            "C:\\",
            "C: /f",
            "C: & whoami",
            "C: && dir",
            "C|dir",
            "1:",
            "?:",
            None,
        ]

        for raw_drive in unsafe_values:
            with self.subTest(raw_drive=raw_drive):
                with self.assertRaises(ValueError):
                    normalize_drive_letter(raw_drive)

    def test_chkdsk_check_uses_normalized_drive_in_command(self):
        """CHKDSK check commands should use normalized drive strings."""
        executor = RecordingExecutor()
        commands = HealthCheckCommands(executor=executor)

        result = commands.chkdsk_check("d")

        self.assertEqual(result.command, "chkdsk D:")
        self.assertEqual(executor.commands, ["chkdsk D:"])

    def test_chkdsk_fix_uses_normalized_drive_in_command(self):
        """CHKDSK fix commands should use normalized drive strings."""
        executor = RecordingExecutor()
        commands = HealthCheckCommands(executor=executor)

        result = commands.chkdsk_fix("e:")

        self.assertEqual(result.command, "chkdsk E: /f")
        self.assertEqual(executor.commands, ["chkdsk E: /f"])

    def test_chkdsk_commands_reject_unsafe_drive_before_execution(self):
        """Unsafe drive values should fail before reaching the executor."""
        executor = RecordingExecutor()
        commands = HealthCheckCommands(executor=executor)

        with self.assertRaises(ValueError):
            commands.chkdsk_check("C: & whoami")
        with self.assertRaises(ValueError):
            commands.chkdsk_fix("C: /r")

        self.assertEqual(executor.commands, [])


if __name__ == "__main__":
    unittest.main()
