"""Regression tests for Windows packaging documentation consistency."""

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]


class PackagingConsistencyTests(unittest.TestCase):
    """Keep documented build commands aligned with the Windows build script."""

    def test_readme_documents_user_facing_source_build_flow(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("Build From Source", readme)
        self.assertIn("python -m venv .venv", readme)
        self.assertIn("python -m pip install -r requirements.txt", readme)
        self.assertIn("build.bat", readme)
        self.assertIn("dist\\Windows Health Check Tool.exe", readme)

    def test_requirements_include_packaging_dependencies(self):
        requirements = (REPO_ROOT / "requirements.txt").read_text(encoding="utf-8")

        for package in ("customtkinter", "psutil", "pyinstaller", "pywin32", "Pillow"):
            with self.subTest(package=package):
                self.assertIn(package, requirements)

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
        self.assertIn("--collect-all customtkinter", build_script)
        self.assertIn("python -m pip install -r requirements.txt", build_script)
        self.assertIn("import customtkinter, psutil, PIL, PyInstaller, win32api", build_script)
        self.assertIn('--name "Windows Health Check Tool"', build_script)
        self.assertIn('dist\\Windows Health Check Tool.exe', build_script)

    def test_spec_collects_customtkinter_resources(self):
        spec = (REPO_ROOT / "Windows Health Check Tool.spec").read_text(encoding="utf-8")

        self.assertIn("collect_all", spec)
        self.assertIn("collect_all('customtkinter')", spec)
        self.assertIn("binaries=customtkinter_binaries", spec)
        self.assertIn("datas=[('icon.ico', '.')] + customtkinter_datas", spec)
        self.assertIn("hiddenimports=customtkinter_hiddenimports", spec)


if __name__ == "__main__":
    unittest.main()
