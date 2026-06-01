"""Regression tests for the system information panel."""

import sys
import types
import unittest


# ui.system_info imports customtkinter for widget construction, but these tests only
# exercise formatting logic and should not require the GUI dependency to be installed.
sys.modules.setdefault("customtkinter", types.ModuleType("customtkinter"))

from ui.system_info import SystemInfoPanel


class SystemInfoPanelFormattingTests(unittest.TestCase):
    """Tests for formatting gathered system information."""

    def test_format_system_info_handles_unavailable_disk_values(self):
        """Unavailable C: disk details should render as N/A instead of crashing."""
        for missing_value in (None, "N/A"):
            with self.subTest(missing_value=missing_value):
                panel = object.__new__(SystemInfoPanel)
                panel.info_data = {
                    "os": "Windows 11",
                    "memory_total": 16.0,
                    "memory_free": 8.0,
                    "memory_used_percent": 50.0,
                    "disk_total": missing_value,
                    "disk_free": missing_value,
                    "disk_used_percent": missing_value,
                    "cpu_count": 8,
                    "cpu_percent": 12.5,
                }

                formatted = panel._format_system_info()

                self.assertIn("Disk C: N/A", formatted)
                self.assertIn("RAM: 8.0GB free / 16.0GB total (50.0% free)", formatted)
                self.assertIn("CPU: 8 cores (12.5% usage)", formatted)


if __name__ == "__main__":
    unittest.main()
