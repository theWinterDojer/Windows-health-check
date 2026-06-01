![Banner](https://github.com/theWinterDojer/Windows-health-check/blob/main/public/banner.png?raw=true)

# Windows Health Check Tool

**Latest Release**: [Download Latest Version](https://github.com/theWinterDojer/windows-health-check/releases/latest)

Windows Health Check Tool is a Windows 10/11 maintenance app with a Windows 95-inspired interface. It provides quick access to common diagnostic and repair tools, shows live command output, and helps guide you through follow-up repair actions when issues are found.

## Requirements

- Windows 10 or Windows 11
- Administrator privileges

The app requests administrator access when needed so Windows maintenance tools can run correctly.

## Installation

Download the latest standalone executable from the [Releases page](https://github.com/theWinterDojer/windows-health-check/releases/latest).

No installation is required. Download the executable, run it, and approve the Windows administrator prompt.

## Features

- **DISM Scan Health**: Checks the Windows component store for corruption.
- **DISM Restore Health**: Repairs component store corruption when needed.
- **System File Checker (SFC)**: Verifies and repairs protected Windows system files.
- **Check Disk (CHKDSK)**: Checks a selected drive for file system issues and can schedule repairs.
- **Windows System Tools**: Opens Event Viewer, Resource Monitor, System Information, Windows Memory Diagnostic, and Reliability History.
- **System Monitoring**: Shows live CPU and memory usage.
- **Live Output**: Displays diagnostic command output as tools run.
- **Smart Repair Prompts**: Offers follow-up repair actions when diagnostic output indicates a repair may help.
- **Export Results**: Saves the displayed diagnostic output to a text file.

## Usage

1. Launch Windows Health Check Tool.
2. Approve the administrator prompt.
3. Select the diagnostic tools you want to run.
4. Click **RUN SELECTED TOOLS**.
5. Watch the live output and respond to any repair prompts.
6. Export the results if you want to save a record of the run.

## Notes

- Some tools can take several minutes to complete.
- CHKDSK repairs may require a restart or may be scheduled for the next boot.
- DISM Restore Health and SFC can modify Windows system files as part of normal repair behavior.
- If you are unsure what a repair prompt means, review the displayed diagnostic output before continuing.

## Build From Source

Most users should use the standalone executable from the Releases page. If you want to build the app yourself, use Windows with Python installed:

```bash
git clone https://github.com/theWinterDojer/windows-health-check.git
cd windows-health-check
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
build.bat
```

The built executable will be created at:

```text
dist\Windows Health Check Tool.exe
```

## License

MIT License - See LICENSE file for details.
