"""Regression tests for shared CHKDSK result classification."""

import sys
import types
import unittest


# main.py imports GUI modules, but these tests only exercise pure result analysis.
tkinter_stub = types.ModuleType("tkinter")
setattr(tkinter_stub, "messagebox", types.SimpleNamespace())
sys.modules.setdefault("tkinter", tkinter_stub)

main_window_stub = types.ModuleType("ui.main_window")
setattr(main_window_stub, "MainWindow", object)
sys.modules.setdefault("ui.main_window", main_window_stub)

from commands import CommandResult, HealthCheckCommands, WindowsCommandExecutor, analyze_chkdsk_result
from main import ResultAnalyzer


class ChkdskAnalysisTests(unittest.TestCase):
    """Tests for CHKDSK classification used by prompting and summaries."""

    def _result(self, output, exit_code=0):
        return CommandResult("chkdsk c:", exit_code, output)

    def test_shared_chkdsk_analysis_marks_access_errors_as_failures_without_fix_prompt(self):
        """Access failures should not be treated as repairable disk findings."""
        result = self._result("Access denied while opening the volume", exit_code=1)
        commands = HealthCheckCommands(executor=WindowsCommandExecutor())

        self.assertEqual(
            analyze_chkdsk_result(result),
            {
                "status": "failed",
                "message": "Tool execution failed (exit code: 1)",
                "icon": "❌",
            },
        )
        self.assertEqual(ResultAnalyzer.analyze_tool_result("Check Disk", result), analyze_chkdsk_result(result))
        self.assertFalse(commands.chkdsk_needs_fix(result))

    def test_shared_chkdsk_analysis_marks_findings_as_issues_and_prompts_for_fix(self):
        """Repairable CHKDSK findings should be summarized and prompt for /f."""
        result = self._result("Windows found problems with the file system.", exit_code=0)
        commands = HealthCheckCommands(executor=WindowsCommandExecutor())

        self.assertEqual(
            analyze_chkdsk_result(result),
            {"status": "issues_detected", "message": "Issues detected", "icon": "⚠️"},
        )
        self.assertEqual(ResultAnalyzer.analyze_tool_result("Check Disk", result), analyze_chkdsk_result(result))
        self.assertTrue(commands.chkdsk_needs_fix(result))

    def test_shared_chkdsk_analysis_treats_repair_exit_codes_as_issues(self):
        """CHKDSK issue exit codes should align between summary and repair prompt logic."""
        result = self._result("CHKDSK completed with status code 2", exit_code=2)
        commands = HealthCheckCommands(executor=WindowsCommandExecutor())

        self.assertEqual(
            analyze_chkdsk_result(result),
            {"status": "issues_detected", "message": "Issues detected", "icon": "⚠️"},
        )
        self.assertEqual(ResultAnalyzer.analyze_tool_result("Check Disk", result), analyze_chkdsk_result(result))
        self.assertTrue(commands.chkdsk_needs_fix(result))

    def test_shared_chkdsk_analysis_marks_clean_scan_as_success_without_fix_prompt(self):
        """Clean CHKDSK output should not request a repair run."""
        result = self._result("Windows has scanned the file system and found no problems.", exit_code=0)
        commands = HealthCheckCommands(executor=WindowsCommandExecutor())

        self.assertEqual(
            analyze_chkdsk_result(result),
            {"status": "success", "message": "No problems found", "icon": "✅"},
        )
        self.assertEqual(ResultAnalyzer.analyze_tool_result("Check Disk", result), analyze_chkdsk_result(result))
        self.assertFalse(commands.chkdsk_needs_fix(result))


if __name__ == "__main__":
    unittest.main()
