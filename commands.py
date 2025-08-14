"""
Windows Health Check Commands
Handles execution of Windows maintenance commands with real-time output capture
"""

import subprocess
import io
import threading
import queue
import time
from typing import Callable, Optional, List, Tuple


class CommandResult:
    """Container for command execution results"""
    def __init__(self, command: str, exit_code: int, output: str, error: str = ""):
        self.command = command
        self.exit_code = exit_code
        self.output = output
        self.error = error
        self.success = exit_code == 0


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
        
    def _read_output(self, pipe, output_queue: queue.Queue, prefix: str = ""):
        """Read output from subprocess pipe in a separate thread - minimal processing"""
        try:
            while self.is_running:
                line = pipe.readline()
                if not line:  # EOF
                    break
                # Handle carriage returns (progress indicators) and remove trailing whitespace
                clean_line = line.rstrip('\r\n')
                if clean_line:  # Only add non-empty lines
                    output_queue.put(f"{prefix}{clean_line}")
        except Exception as e:
            output_queue.put(f"ERROR: {str(e)}")
        finally:
            pipe.close()

    def _read_output_utf16(self, pipe, output_queue: queue.Queue, prefix: str = ""):
        """Read output from a binary pipe that emits UTF-16LE text (e.g., SFC)."""
        try:
            # Wrap the binary pipe with a TextIO wrapper using UTF-16LE decoding.
            # UTF-16LE doesn't require BOM and is what Windows uses for SFC output.
            text_stream = io.TextIOWrapper(pipe, encoding='utf-16le', errors='replace')
            while self.is_running:
                line = text_stream.readline()
                if not line:
                    break
                clean_line = line.rstrip('\r\n')
                if clean_line:
                    output_queue.put(f"{prefix}{clean_line}")
        except Exception as e:
            output_queue.put(f"ERROR: {str(e)}")
        finally:
            try:
                text_stream.detach()
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
        if self.output_callback:
            self.output_callback(f"C:\\> {command}")
        
        output_lines = []
        error_lines = []
        output_queue = queue.Queue()
        
        try:
            self.is_running = True
            
            # Start the process (minimal processing - capture exactly what Windows outputs)
            self.current_process = subprocess.Popen(
                command,
                shell=shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                creationflags=0
            )
            
            # Start threads to read stdout and stderr
            stdout_thread = threading.Thread(
                target=self._read_output,
                args=(self.current_process.stdout, output_queue, "")
            )
            stderr_thread = threading.Thread(
                target=self._read_output,
                args=(self.current_process.stderr, output_queue, "ERROR: ")
            )
            
            stdout_thread.start()
            stderr_thread.start()
            
            # Process output in real-time
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
            
            # Wait for process to complete
            exit_code = self.current_process.wait()
            
            # Wait for threads to finish
            stdout_thread.join(timeout=1)
            stderr_thread.join(timeout=1)
            
            # Get any remaining output
            while not output_queue.empty():
                try:
                    line = output_queue.get_nowait()
                    output_lines.append(line)
                    if line.startswith("ERROR:"):
                        error_lines.append(line)
                except queue.Empty:
                    break
            
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
                except:
                    pass
    
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
        if self.output_callback:
            self.output_callback(f"C:\\> {command}")

        output_lines = []
        error_lines = []
        output_queue = queue.Queue()

        try:
            self.is_running = True
            # Launch without text/universal_newlines; we'll decode as UTF-16 ourselves.
            self.current_process = subprocess.Popen(
                command,
                shell=shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=False,
                creationflags=0
            )

            stdout_thread = threading.Thread(
                target=self._read_output_utf16,
                args=(self.current_process.stdout, output_queue, "")
            )
            stderr_thread = threading.Thread(
                target=self._read_output_utf16,
                args=(self.current_process.stderr, output_queue, "ERROR: ")
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
            while not output_queue.empty():
                try:
                    line = output_queue.get_nowait()
                    output_lines.append(line)
                    if line.startswith("ERROR:"):
                        error_lines.append(line)
                except queue.Empty:
                    break

            return CommandResult(
                command=command,
                exit_code=exit_code,
                output="\n".join(output_lines),
                error="\n".join(error_lines)
            )
        except Exception as e:
            error_msg = f"Failed to execute SFC: {str(e)}"
            if self.output_callback:
                self.output_callback(f"ERROR: {error_msg}")
            return CommandResult(command=command, exit_code=-1, output="\n".join(output_lines), error=error_msg)
        finally:
            self.is_running = False
            if self.current_process:
                try:
                    self.current_process.terminate()
                except Exception:
                    pass


class HealthCheckCommands:
    """Specific Windows health check commands"""
    
    def __init__(self, executor: WindowsCommandExecutor):
        self.executor = executor
        
    def dism_check_health(self) -> CommandResult:
        """Run DISM CheckHealth"""
        return self.executor.execute_command("DISM /Online /Cleanup-Image /CheckHealth")
    
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
        return self.executor.execute_command(f"chkdsk {drive}")
    
    def chkdsk_fix(self, drive: str = "c:") -> CommandResult:
        """Run CHKDSK with fix"""
        return self.executor.execute_command(f"chkdsk {drive} /f")
    
    def run_smart_dism_sequence(self, prompt_callback=None) -> list:
        """
        Run DISM commands: ScanHealth first, then RestoreHealth if corruption detected
        
        Args:
            prompt_callback: Function to call when user prompt is needed
            
        Returns:
            List of CommandResult objects
        """
        results = []
        
        # Step 1: Run ScanHealth to check for corruption
        scan_result = self.dism_scan_health()
        results.append(("dism_scan", scan_result))
        
        # Step 2: Check if RestoreHealth is needed
        if scan_result.success and "no component store corruption detected" not in scan_result.output.lower():
            # Step 3: Prompt user for RestoreHealth
            should_restore = True  # Default to yes
            if prompt_callback:
                should_restore = prompt_callback(
                    "DISM Corruption Detected",
                    "DISM has detected corruption that can be repaired.\n\n"
                    "Would you like to run DISM RestoreHealth to fix the issues?\n"
                    "(This may take several minutes)"
                )
            
            if should_restore:
                # Add visual separator before RestoreHealth
                if hasattr(self.executor, 'output_callback') and self.executor.output_callback:
                    self.executor.output_callback("")
                    self.executor.output_callback("--- Proceeding to DISM Restore Health ---")
                    self.executor.output_callback("")
                
                restore_result = self.dism_restore_health()
                results.append(("dism_restore", restore_result))
        
        return results
    

    
    def run_smart_chkdsk_sequence(self, prompt_callback=None) -> list:
        """
        Run CHKDSK in smart sequence: check first, then fix if errors found
        
        Args:
            prompt_callback: Function to prompt user for confirmation
            
        Returns:
            List of CommandResult objects
        """
        results = []
        
        # Step 1: Always run Check first (read-only)
        check_result = self.chkdsk_check()
        results.append(("chkdsk_check", check_result))
        
        # Step 2: Analyze check output for errors
        needs_fix = self._chkdsk_needs_fix(check_result)
        
        if needs_fix:
            # Add visual separator before fix command
            if hasattr(self.executor, 'output_callback') and self.executor.output_callback:
                self.executor.output_callback("")
                self.executor.output_callback("--- Proceeding to Check Disk Fix ---")
                self.executor.output_callback("")
            
            # Step 3: Prompt user for fix
            should_fix = True  # Default to yes
            if prompt_callback:
                should_fix = prompt_callback(
                    "Disk Errors Detected",
                    "Check Disk has detected errors that can be repaired.\n\n"
                    "Would you like to run Check Disk with fix to repair the errors?\n"
                    "(This may take several minutes and require a restart for system drive)"
                )
            
            if should_fix:
                fix_result = self.chkdsk_fix()
                results.append(("chkdsk_fix", fix_result))
        
        return results
    
    def _chkdsk_needs_fix(self, check_result: CommandResult) -> bool:
        """Determine if CHKDSK fix is needed based on check output"""
        if not check_result.success or not check_result.output:
            return False
        
        output_lower = check_result.output.lower()
        
        # Look for the specific "Errors found" message that CHKDSK outputs
        return "errors found" in output_lower


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
