"""
Windows Health Check Commands
Handles execution of Windows maintenance commands with real-time output capture
"""

import codecs
import locale
import os
import re
import subprocess
import threading
import queue
from typing import Callable, Optional, List


class CommandResult:
    """Container for command execution results"""
    def __init__(self, command: str, exit_code: int, output: str, error: str = ""):
        self.command = command
        self.exit_code = exit_code
        self.output = output
        self.error = error
        self.success = exit_code == 0


CHKDSK_FAILURE_PATTERNS = [
    "cannot open volume for direct access",
    "access denied",
    "is write protected",
    "unable to determine volume version and state",
]

CHKDSK_OK_PATTERNS = [
    "windows has scanned the file system and found no problems",
    "found no problems",
    "no problems were found",
    "found no issues",
]

CHKDSK_ISSUE_PATTERNS = [
    "errors found",
    "found problems",
    "windows found problems",
    "file system errors",
    "has identified one or more errors",
]

CHKDSK_ISSUE_EXIT_CODES = (1, 2, 3)


def analyze_chkdsk_result(result: CommandResult) -> dict:
    """Analyze CHKDSK results, treating findings as issues not failures."""
    output_lower = (result.output or "").lower()

    if any(pattern in output_lower for pattern in CHKDSK_FAILURE_PATTERNS):
        return {
            "status": "failed",
            "message": f"Tool execution failed (exit code: {result.exit_code})",
            "icon": "❌",
        }

    if any(pattern in output_lower for pattern in CHKDSK_OK_PATTERNS):
        return {"status": "success", "message": "No problems found", "icon": "✅"}

    if any(pattern in output_lower for pattern in CHKDSK_ISSUE_PATTERNS):
        return {"status": "issues_detected", "message": "Issues detected", "icon": "⚠️"}

    if result.exit_code in CHKDSK_ISSUE_EXIT_CODES:
        return {"status": "issues_detected", "message": "Issues detected", "icon": "⚠️"}

    if not result.success:
        return {
            "status": "failed",
            "message": f"Tool execution failed (exit code: {result.exit_code})",
            "icon": "❌",
        }

    return {"status": "success", "message": "Completed", "icon": "✅"}


def chkdsk_result_needs_fix(check_result: Optional[CommandResult]) -> bool:
    """Return True when CHKDSK output indicates a repair run should be offered."""
    if not check_result:
        return False

    return analyze_chkdsk_result(check_result)["status"] == "issues_detected"


def normalize_drive_letter(drive: str) -> str:
    """Validate and normalize a Windows drive letter for CHKDSK commands."""
    if not isinstance(drive, str):
        raise ValueError("Drive must be a single letter with optional colon")

    normalized = drive.strip().upper()
    if not re.fullmatch(r"[A-Z]:?", normalized):
        raise ValueError("Drive must be a single letter with optional colon")

    return f"{normalized[0]}:"


class WindowsCommandExecutor:
    """Executes Windows commands with real-time output capture"""
    
    def __init__(self, output_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize command executor
        
        Args:
            output_callback: Function to call with each line of output
        """
        self.output_callback = output_callback
        self.is_running = False
        self.current_process = None
        
    def _emit_stream_text(self, text: str, output_queue: queue.Queue, prefix: str = ""):
        """Split streamed text on CR/LF boundaries so inline progress updates surface immediately."""
        for line in text.replace("\r\n", "\r").replace("\n", "\r").split("\r"):
            clean_line = line.rstrip("\r\n")
            if clean_line:
                output_queue.put(f"{prefix}{clean_line}")

    def _read_output(self, pipe, output_queue: queue.Queue, encoding: str, prefix: str = ""):
        """Read subprocess output incrementally so CR-based progress is not buffered until newline."""
        decoder = codecs.getincrementaldecoder(encoding)(errors="replace")
        pending_text = ""
        fd = pipe.fileno()
        try:
            while self.is_running:
                chunk = os.read(fd, 64)
                if not chunk:
                    break

                pending_text += decoder.decode(chunk)

                last_break = max(pending_text.rfind("\r"), pending_text.rfind("\n"))
                if last_break == -1:
                    continue

                complete_text = pending_text[:last_break + 1]
                pending_text = pending_text[last_break + 1:]
                self._emit_stream_text(complete_text, output_queue, prefix)

            pending_text += decoder.decode(b"", final=True)
            final_line = pending_text.rstrip("\r\n")
            if final_line:
                output_queue.put(f"{prefix}{final_line}")
        except Exception as e:
            output_queue.put(f"ERROR: {str(e)}")
        finally:
            try:
                pipe.close()
            except Exception:
                pass

    def _process_stream_output(self, output_queue: queue.Queue, output_lines: List[str], error_lines: List[str]):
        """Drain queued subprocess output and forward it to the UI callback."""
        while True:
            try:
                line = output_queue.get_nowait()
            except queue.Empty:
                break

            output_lines.append(line)
            if self.output_callback:
                self.output_callback(line)
            if line.startswith("ERROR:"):
                error_lines.append(line)

    def _execute_streamed_command(self, command: str, encoding: str, shell: bool = True) -> CommandResult:
        """Execute a command with incremental streamed output capture."""
        if self.output_callback:
            self.output_callback(f"C:\\> {command}")

        output_lines = []
        error_lines = []
        output_queue = queue.Queue()

        try:
            self.is_running = True
            self.current_process = subprocess.Popen(
                command,
                shell=shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=False,
                creationflags=0
            )

            stdout_thread = threading.Thread(
                target=self._read_output,
                args=(self.current_process.stdout, output_queue, encoding, "")
            )
            stderr_thread = threading.Thread(
                target=self._read_output,
                args=(self.current_process.stderr, output_queue, encoding, "ERROR: ")
            )

            stdout_thread.start()
            stderr_thread.start()

            while self.current_process.poll() is None or not output_queue.empty():
                try:
                    line = output_queue.get(timeout=0.1)
                    output_lines.append(line)
                    if self.output_callback:
                        self.output_callback(line)
                    if line.startswith("ERROR:"):
                        error_lines.append(line)
                except queue.Empty:
                    continue

            exit_code = self.current_process.wait()
            stdout_thread.join(timeout=1)
            stderr_thread.join(timeout=1)
            self._process_stream_output(output_queue, output_lines, error_lines)

            return CommandResult(
                command=command,
                exit_code=exit_code,
                output="\n".join(output_lines),
                error="\n".join(error_lines)
            )
        except Exception as e:
            error_msg = f"Failed to execute command: {str(e)}"
            if self.output_callback:
                self.output_callback(f"ERROR: {error_msg}")

            return CommandResult(
                command=command,
                exit_code=-1,
                output="\n".join(output_lines),
                error=error_msg
            )
        finally:
            self.is_running = False
            if self.current_process:
                try:
                    self.current_process.terminate()
                except Exception:
                    pass
    
    def execute_command(self, command: str, shell: bool = True) -> CommandResult:
        """
        Execute a command with real-time output capture
        
        Args:
            command: Command to execute
            shell: Whether to use shell execution
            
        Returns:
            CommandResult object with execution details
        """
        return self._execute_streamed_command(
            command,
            encoding=locale.getpreferredencoding(False),
            shell=shell
        )
    
    def stop_execution(self):
        """Stop the currently running command"""
        self.is_running = False
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=5)
            except:
                try:
                    self.current_process.kill()
                except:
                    pass

    def execute_sfc(self, command: str = "sfc /scannow", shell: bool = True) -> CommandResult:
        """Execute SFC with proper UTF-16 decoding to avoid spaced characters."""
        return self._execute_streamed_command(command, encoding="utf-16le", shell=shell)


class HealthCheckCommands:
    """Specific Windows health check commands"""
    
    def __init__(self, executor: WindowsCommandExecutor):
        self.executor = executor
        
    def dism_scan_health(self) -> CommandResult:
        """Run DISM ScanHealth"""
        return self.executor.execute_command("DISM /Online /Cleanup-Image /ScanHealth")
    
    def dism_restore_health(self) -> CommandResult:
        """Run DISM RestoreHealth"""
        return self.executor.execute_command("DISM /Online /Cleanup-Image /RestoreHealth")
    
    def sfc_scan(self) -> CommandResult:
        """Run System File Checker with proper UTF-16 decoding"""
        return self.executor.execute_sfc("sfc /scannow")
    
    def chkdsk_check(self, drive: str = "c:") -> CommandResult:
        """Run CHKDSK check only"""
        normalized_drive = normalize_drive_letter(drive)
        return self.executor.execute_command(f"chkdsk {normalized_drive}")
    
    def chkdsk_fix(self, drive: str = "c:") -> CommandResult:
        """Run CHKDSK with fix"""
        normalized_drive = normalize_drive_letter(drive)
        return self.executor.execute_command(f"chkdsk {normalized_drive} /f")

    def chkdsk_needs_fix(self, check_result: CommandResult) -> bool:
        """Public helper for CHKDSK fix detection"""
        return chkdsk_result_needs_fix(check_result)
    
    def _chkdsk_needs_fix(self, check_result: CommandResult) -> bool:
        """Determine if CHKDSK fix is needed based on check output"""
        return chkdsk_result_needs_fix(check_result)


# Test function for command execution
def test_commands():
    """Test function to verify command execution works"""
    def print_output(line):
        print(f"OUTPUT: {line}")
    
    executor = WindowsCommandExecutor(output_callback=print_output)
    commands = HealthCheckCommands(executor)
    
    # Test with a simple command
    result = executor.execute_command("echo Testing command execution")
    print(f"Exit code: {result.exit_code}")
    print(f"Success: {result.success}")


if __name__ == "__main__":
    test_commands()
