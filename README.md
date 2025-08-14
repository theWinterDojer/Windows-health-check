![Banner](https://github.com/theWinterDojer/Windows-health-check/blob/main/public/banner.png?raw=true)

# Windows Health Check Tool

**Latest Release**: [Download Latest Version](https://github.com/theWinterDojer/windows-health-check/releases/latest)

GUI-based Windows system maintenance tool with Windows 95-inspired interface for automated diagnostic and repair utilities.

## Requirements

- Windows 10/11
- Administrator privileges (automatic UAC elevation)

## Installation

**Standalone Executable**: Download from releases (no installation required)

**Development**:
```bash
git clone https://github.com/theWinterDojer/windows-health-check.git
cd windows-health-check
pip install -r requirements.txt
python main.py
```

## Features

- **DISM Check/Scan Health**: Component store integrity verification
- **DISM Restore Health**: Automatic corruption repair (prompted when needed)
- **System File Checker (SFC)**: System file verification and repair
- **Check Disk (CHKDSK)**: File system error detection and repair
- **Real-time Output**: Live command execution with progress tracking
- **Smart Prompting**: Conditional repair dialogs based on diagnostic results

## Usage

1. Launch application (UAC elevation required)
2. Select diagnostic tools via checkboxes
3. Click "RUN SELECTED TOOLS"
4. Monitor real-time output and respond to repair prompts
5. Export results to text file

## Technical Details

### Architecture
- **Command Execution**: Thread-safe subprocess management with real-time output capture
- **Encoding**: UTF-16LE support for Windows tools (SFC compatibility)
- **UAC Elevation**: ctypes-based privilege escalation using ShellExecuteW
- **GUI Framework**: CustomTkinter with Windows 95 retro styling

### Dependencies
- `customtkinter`: Modern tkinter replacement
- `psutil`: System information gathering
- `pyinstaller`: Executable packaging

### Build
```bash
python -m PyInstaller --onefile --windowed --icon=icon.ico --add-data "icon.ico;." main.py
```

## Project Structure

```
windows-health-check/
├── main.py              # Application entry point
├── commands.py          # Command execution engine
├── ui/                  # GUI components
├── utils/               # UAC elevation utilities
└── requirements.txt     # Dependencies
```

## License

MIT License - See LICENSE file for details.
