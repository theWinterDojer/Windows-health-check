"""Regression tests for user-facing text consistency."""

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class UserFacingTextConsistencyTests(unittest.TestCase):
    """Keep docs/help text aligned with currently available app behavior."""

    def test_help_text_does_not_document_removed_dism_check_health_tool(self):
        """The app now offers DISM Scan Health, not a separate DISM Check Health option."""
        main_window_source = (REPO_ROOT / "ui" / "main_window.py").read_text(encoding="utf-8")

        self.assertNotIn("DISM CHECK HEALTH", main_window_source)
        self.assertNotIn("DISM Check Health", main_window_source)
        self.assertIn("DISM SCAN HEALTH", main_window_source)

    def test_readme_is_user_facing_and_omits_internal_maintenance_notes(self):
        """Public README should stay evergreen and avoid internal development notes."""
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("Live Output", readme)
        self.assertIn("Build From Source", readme)
        self.assertNotIn("Output batching is deferred pending measurement", readme)
        self.assertNotIn("Maintenance Notes", readme)


if __name__ == "__main__":
    unittest.main()
