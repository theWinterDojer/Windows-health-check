import sys
import types
import unittest
from unittest.mock import patch


customtkinter_stub = sys.modules.setdefault("customtkinter", types.ModuleType("customtkinter"))

tkinter_stub = sys.modules.setdefault("tkinter", types.ModuleType("tkinter"))
setattr(tkinter_stub, "TOP", "top")
setattr(tkinter_stub, "RAISED", "raised")
setattr(tkinter_stub, "PhotoImage", object)

pil_stub = sys.modules.setdefault("PIL", types.ModuleType("PIL"))
image_stub = sys.modules.setdefault("PIL.Image", types.ModuleType("PIL.Image"))
image_tk_stub = sys.modules.setdefault("PIL.ImageTk", types.ModuleType("PIL.ImageTk"))

from ui.tool_selector import ToolSelectorPanel


class FakeProcess:
    def __init__(self, returncode=None):
        self.returncode = returncode

    def poll(self):
        return self.returncode


class SystemToolLaunchErrorTests(unittest.TestCase):
    def make_panel(self):
        panel = object.__new__(ToolSelectorPanel)
        panel.launch_error_callback = None
        return panel

    def test_system_tool_launch_uses_nonblocking_popen_without_shell(self):
        panel = self.make_panel()

        with patch("ui.tool_selector.subprocess.run") as run_mock, \
                patch("ui.tool_selector.subprocess.Popen", return_value=FakeProcess()) as popen_mock:
            launched = panel._open_event_viewer()

        self.assertTrue(launched)
        run_mock.assert_not_called()
        popen_mock.assert_called_once_with(["eventvwr.exe"], shell=False)

    def test_system_tool_launch_failure_reports_to_callback(self):
        panel = self.make_panel()
        errors = []
        panel.set_launch_error_callback(errors.append)

        with patch("ui.tool_selector.subprocess.Popen", side_effect=OSError("missing executable")):
            launched = panel._open_event_viewer()

        self.assertFalse(launched)
        self.assertEqual(1, len(errors))
        self.assertIn("Failed to open Event Viewer", errors[0])
        self.assertIn("missing executable", errors[0])

    def test_reliability_history_reports_one_error_after_all_launch_attempts_fail(self):
        panel = self.make_panel()
        errors = []
        panel.set_launch_error_callback(errors.append)

        with patch("ui.tool_selector.subprocess.Popen", side_effect=OSError("blocked")) as popen_mock:
            launched = panel._open_reliability_history()

        self.assertFalse(launched)
        self.assertEqual(3, popen_mock.call_count)
        self.assertEqual(1, len(errors))
        self.assertIn("Failed to open Reliability History", errors[0])
        self.assertIn("blocked", errors[0])

    def test_reliability_history_fallback_success_does_not_report_error(self):
        panel = self.make_panel()
        errors = []
        panel.set_launch_error_callback(errors.append)

        def popen_side_effect(command, shell):
            if command == ["perfmon.exe", "/rel"]:
                raise OSError("primary unavailable")
            return FakeProcess()

        with patch("ui.tool_selector.subprocess.Popen", side_effect=popen_side_effect) as popen_mock:
            launched = panel._open_reliability_history()

        self.assertTrue(launched)
        self.assertEqual(2, popen_mock.call_count)
        self.assertEqual([], errors)

    def test_system_tool_immediate_nonzero_exit_reports_to_callback(self):
        panel = self.make_panel()
        errors = []
        panel.set_launch_error_callback(errors.append)

        with patch("ui.tool_selector.subprocess.Popen", return_value=FakeProcess(returncode=1)):
            launched = panel._open_resource_monitor()

        self.assertFalse(launched)
        self.assertEqual(1, len(errors))
        self.assertIn("Failed to open Resource Monitor", errors[0])
        self.assertIn("exit code 1", errors[0])

    def test_reliability_history_immediate_nonzero_primary_attempts_fallback(self):
        panel = self.make_panel()
        errors = []
        panel.set_launch_error_callback(errors.append)

        def popen_side_effect(command, shell):
            if command == ["perfmon.exe", "/rel"]:
                return FakeProcess(returncode=1)
            return FakeProcess()

        with patch("ui.tool_selector.subprocess.Popen", side_effect=popen_side_effect) as popen_mock:
            launched = panel._open_reliability_history()

        self.assertTrue(launched)
        self.assertEqual(2, popen_mock.call_count)
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
