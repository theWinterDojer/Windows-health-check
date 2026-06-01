"""Regression tests for Windows packaging documentation consistency."""

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class PackagingConsistencyTests(unittest.TestCase):
    """Keep documented build commands aligned with the Windows build script."""

    def test_readme_pyinstaller_command_matches_named_windows_executable(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("--name \"Windows Health Check Tool\"", readme)
        self.assertIn("--icon=icon.ico", readme)
        self.assertIn("--add-data \"icon.ico;.\"", readme)

    def test_readme_dependencies_match_requirements(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        requirements = (REPO_ROOT / "requirements.txt").read_text(encoding="utf-8")

        for package in ("customtkinter", "psutil", "pyinstaller", "pywin32", "Pillow"):
            with self.subTest(package=package):
                self.assertIn(package, requirements)
                self.assertIn(package, readme)

    def test_gitignore_allows_canonical_windows_build_script_but_keeps_spec_ignored(self):
        gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")

        self.assertIn("*.bat", gitignore)
        self.assertIn("!build.bat", gitignore)
        self.assertIn("*.spec", gitignore)
        self.assertNotIn("!Windows Health Check Tool.spec", gitignore)

    def test_build_script_uses_root_icon_and_expected_executable_name(self):
        build_script = (REPO_ROOT / "build.bat").read_text(encoding="utf-8")

        self.assertIn("--icon=icon.ico", build_script)
        self.assertIn('--add-data "icon.ico;."', build_script)
        self.assertIn('--name "Windows Health Check Tool"', build_script)
        self.assertIn('dist\\Windows Health Check Tool.exe', build_script)


if __name__ == "__main__":
    unittest.main()
