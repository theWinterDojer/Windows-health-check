"""
Windows Health Check Tool - Main Entry Point
A modern GUI tool for Windows system maintenance and diagnostics with retro Windows 95 styling
"""

import sys
import threading
import time
from typing import List
from tkinter import messagebox
import tkinter as tk

from utils.admin import check_and_elevate, is_admin
from commands import WindowsCommandExecutor, HealthCheckCommands
from ui.main_window import MainWindow


class HealthCheckApp:
    """Main application class for Windows Health Check Tool"""
    
    def __init__(self):
        # Check admin privileges first
        if not is_admin():
            # The check_and_elevate function will handle the user prompt
            # and either elevate (which exits this process) or return False
            if not check_and_elevate():
                # User declined elevation - exit gracefully
                sys.exit(0)
        
        # Initialize command executor
        self.executor = WindowsCommandExecutor(output_callback=self.output_callback)
        self.commands = HealthCheckCommands(self.executor)
        
        # Create main window with run callback
        self.window = MainWindow(run_callback=self.run_selected_tools)
        
        # Execution state
        self.is_running = False
        self.current_tools = []
        self.completed_tools = 0
        
        # Progress simulation state
        self.progress_thread = None
        self.base_progress = 0.0
        self.current_tool_progress = 0.0
        self.stop_progress_simulation = False
        
        # System info update timer
        self.system_info_timer = None
        
        # Welcome message
        self.window.append_separator()
        self.window.append_output("Windows Health Check Tool - Ready", "#00ffff")
        self.window.append_output("Administrator privileges: ✓ ACTIVE", "#00ff00")
        self.window.append_separator()
        self.window.append_output("")
        
        # Start system info updates
        self.start_system_info_updates()
    
    def output_callback(self, line: str):
        """Callback function for command output"""
        self.window.append_output(line)
    
    def start_progress_simulation(self, tool_name: str):
        """Start a smooth progress simulation for the current tool"""
        self.stop_progress_simulation = False
        self.current_tool_progress = 0.0
        
        # Use realistic timing estimates based on user testing
        tool_durations = {
            "DISM Check Health": 2,         # User's actual timing
            "DISM Scan Health": 55,         # User's actual timing
            "DISM Restore Health": 60,      # Estimate (similar to SFC)
            "DISM Health Diagnostics": 57,  # CheckHealth + ScanHealth
            "System File Checker": 60,      # User's actual timing
            "Check Disk": 30,               # User preference
            "Disk Check Diagnostics": 30    # Just check usually
        }
        
        def simulate_progress():
            # Get realistic duration for this specific tool
            tool_duration = tool_durations.get(tool_name, 30)  # Default to 30 if not found
            increment = 1.0 / (tool_duration * 10)  # Update 10 times per second
            
            while not self.stop_progress_simulation and self.current_tool_progress < 0.95:
                self.current_tool_progress += increment
                
                # Calculate total progress (base + current tool portion)
                tools_total = len(self.current_tools)
                tool_portion = 1.0 / tools_total if tools_total > 0 else 1.0
                total_progress = self.base_progress + (self.current_tool_progress * tool_portion)
                
                # Update the progress bar
                self.window.update_progress(total_progress, f"Running {tool_name}...")
                
                time.sleep(0.1)  # Update every 100ms
        
        self.progress_thread = threading.Thread(target=simulate_progress, daemon=True)
        self.progress_thread.start()
    
    def stop_progress_simulation_now(self):
        """Stop the current progress simulation"""
        self.stop_progress_simulation = True
        if self.progress_thread:
            self.progress_thread.join(timeout=0.5)
    
    def advance_to_next_tool(self):
        """Advance base progress to the next tool"""
        tools_total = len(self.current_tools)
        if tools_total > 0:
            self.base_progress = self.completed_tools / tools_total
            self.current_tool_progress = 0.0
    
    def start_system_info_updates(self):
        """Start periodic system info updates every 2 seconds"""
        def update_info():
            self.window.system_info.refresh()
            # Schedule next update in 2 seconds
            self.system_info_timer = self.window.root.after(2000, update_info)
        
        update_info()
    
    def stop_system_info_updates(self):
        """Stop system info updates"""
        if self.system_info_timer:
            self.window.root.after_cancel(self.system_info_timer)
            self.system_info_timer = None
    
    def prompt_user(self, title: str, message: str) -> bool:
        """Show user prompt dialog and return True/False based on user choice"""
        # Ensure the dialog is shown on the main GUI thread and stays on top
        def show_modal_dialog():
            # Create the dialog using the main window as parent for proper modality
            dialog = tk.Toplevel(self.window.root)
            dialog.title(title)
            dialog.geometry("400x150")
            dialog.configure(bg="#c0c0c0")
            dialog.resizable(False, False)
            
            # Make it modal and always on top
            dialog.transient(self.window.root)
            dialog.grab_set()  # Make it modal
            dialog.attributes("-topmost", True)  # Always on top
            dialog.focus_force()  # Force focus
            
            # Center the dialog relative to the main window
            self.window._center_window(dialog, 400, 150)
            
            # Create dialog content
            frame = tk.Frame(dialog, bg="#c0c0c0")
            frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Message text
            msg_label = tk.Label(
                frame,
                text=message,
                bg="#c0c0c0",
                font=("MS Sans Serif", 10),
                wraplength=350,
                justify="left"
            )
            msg_label.pack(pady=(0, 20))
            
            # Button frame
            btn_frame = tk.Frame(frame, bg="#c0c0c0")
            btn_frame.pack()
            
            # Result variable
            self.dialog_result = None
            
            def on_yes():
                self.dialog_result = True
                dialog.destroy()
            
            def on_no():
                self.dialog_result = False
                dialog.destroy()
            
            # Yes button
            yes_btn = tk.Button(
                btn_frame,
                text="Yes",
                command=on_yes,
                width=10,
                bg="#c0c0c0",
                font=("MS Sans Serif", 9),
                relief="raised",
                bd=2
            )
            yes_btn.pack(side="left", padx=(0, 10))
            
            # No button
            no_btn = tk.Button(
                btn_frame,
                text="No",
                command=on_no,
                width=10,
                bg="#c0c0c0",
                font=("MS Sans Serif", 9),
                relief="raised",
                bd=2
            )
            no_btn.pack(side="left")
            
            # Handle window close (X button) as "No"
            dialog.protocol("WM_DELETE_WINDOW", on_no)
            
            # Wait for the dialog to be closed
            dialog.wait_window()
            
            return self.dialog_result
        
        # Show the dialog and return the result
        return show_modal_dialog()
    
    def run_selected_tools(self, selected_tools: List[str]):
        """Run the selected maintenance tools"""
        if self.is_running:
            self.window.append_error("Tools are already running!")
            return
        
        if not selected_tools:
            self.window.append_error("No tools selected!")
            return
        
        # Start execution in a separate thread
        self.current_tools = selected_tools
        self.completed_tools = 0
        thread = threading.Thread(target=self._execute_tools_thread, daemon=True)
        thread.start()
    
    def _execute_tools_thread(self):
        """Execute tools in a separate thread"""
        try:
            self.is_running = True
            self.window.set_tools_enabled(False)
            
            total_tools = len(self.current_tools)
            
            # We'll add a separator after showing the execution plan
            
            # Simple execution - just run tools in the order selected
            
            # Now show the actual execution plan
            self.window.append_separator()
            self.window.append_output(f"Starting execution of {len(self.current_tools)} diagnostic(s)...", "#00ffff")
            self.window.append_separator()
            
            for i, tool_id in enumerate(self.current_tools):
                # Set up progress simulation for this tool
                self.advance_to_next_tool()
                
                # Get friendly tool name for progress display
                tool_names = {
                    "dism_check": "DISM Check Health",
                    "dism_scan": "DISM Scan Health", 
                    "dism_restore": "DISM Restore Health",
                    "sfc_scan": "System File Checker",
                    "chkdsk_check": "Check Disk"
                }
                display_name = tool_names.get(tool_id, tool_id)
                
                # Start smooth progress simulation
                self.start_progress_simulation(display_name)
                
                # Execute the tool
                self._execute_single_tool(tool_id)
                
                # Stop progress simulation and complete this tool
                self.stop_progress_simulation_now()
                self.completed_tools += 1
                
                # Small delay between tools
                time.sleep(0.5)
            
            # Final progress update
            self.window.update_progress(1.0, "All tools completed")
            
            # Show summary
            self._show_execution_summary()
            
        except Exception as e:
            self.window.append_error(f"Execution error: {str(e)}")
        
        finally:
            # Stop any running progress simulation
            self.stop_progress_simulation_now()
            
            # Reset execution state
            self.is_running = False
            self.base_progress = 0.0
            self.current_tool_progress = 0.0
            self.completed_tools = 0
            
            self.window.set_tools_enabled(True)
            self.window.update_progress(0, "Ready")
    
    def _execute_single_tool(self, tool_id: str):
        """Execute a single maintenance tool"""
        # Get friendly tool names
        tool_names = {
            "dism_check": "DISM CHECK HEALTH",
            "dism_scan": "DISM SCAN HEALTH", 
            "sfc_scan": "SYSTEM FILE CHECKER",
            "chkdsk_check": "CHECK DISK"
        }
        
        tool_name = tool_names.get(tool_id, tool_id.upper())
        
        # Clear section separator
        self.window.append_output("")
        self.window.append_output("=" * 50, "#808080")
        self.window.append_output(f"=== {tool_name} ===", "#ffff00")
        self.window.append_output("=" * 50, "#808080")
        self.window.append_output("")
        
        try:
            if tool_id == "dism_check":
                result = self.commands.dism_check_health()
                self._show_single_result(tool_id, result)
            elif tool_id == "dism_scan":
                result = self.commands.dism_scan_health()
                self._show_single_result(tool_id, result)
                
                # Check if RestoreHealth is needed after ScanHealth
                if result.success and "no component store corruption detected" not in result.output.lower():
                    should_restore = self.prompt_user(
                        "DISM Corruption Detected",
                        "DISM has detected corruption that can be repaired.\n\n"
                        "Would you like to run DISM RestoreHealth to fix the issues?\n"
                        "(This may take several minutes)"
                    )
                    
                    if should_restore:
                        self.window.append_output("")
                        self.window.append_output("--- Proceeding to DISM Restore Health ---")
                        self.window.append_output("")
                        
                        restore_result = self.commands.dism_restore_health()
                        self._show_single_result("dism_restore", restore_result)
            elif tool_id == "sfc_scan":
                result = self.commands.sfc_scan()
                self._show_single_result(tool_id, result)
            elif tool_id == "chkdsk_check":
                result = self.commands.chkdsk_check()
                self._show_single_result(tool_id, result)
                
                # Check if Fix is needed after Check
                if result.success and result.output and "errors found" in result.output.lower():
                    should_fix = self.prompt_user(
                        "Disk Errors Detected",
                        "Check Disk has detected errors that can be repaired.\n\n"
                        "Would you like to run Check Disk with fix to repair the errors?\n"
                        "(This may take several minutes and requires a system restart)"
                    )
                    
                    if should_fix:
                        self.window.append_output("")
                        self.window.append_output("--- Proceeding to Check Disk Fix ---")
                        self.window.append_output("")
                        
                        fix_result = self.commands.chkdsk_fix()
                        self._show_single_result("chkdsk_fix", fix_result)
            else:
                self.window.append_error(f"Unknown tool: {tool_id}")
                return
                    
        except Exception as e:
            self.window.append_error(f"Failed to execute {tool_id}: {str(e)}")
        
        # End section spacing
        self.window.append_output("")
        self.window.append_output(f"--- {tool_name} COMPLETED ---", "#00ff00")
    

    def _show_single_result(self, tool_id: str, result):
        """Display the result of a single tool execution"""
        if not result.success:
            self.window.append_error(f"{tool_id} failed with exit code {result.exit_code}")
            if result.error:
                self.window.append_output(f"Error details: {result.error}", "#ff0000")
    
    def _show_execution_summary(self):
        """Show execution summary"""
        self.window.append_output("")
        self.window.append_separator()
        self.window.append_output("EXECUTION SUMMARY", "#00ffff")
        self.window.append_separator()
        self.window.append_output(f"Total diagnostics ran: {len(self.current_tools)}/{len(self.current_tools)}")
        self.window.append_output("Check the output above for detailed results.")
        self.window.append_output("")
        self.window.append_success("Maintenance cycle completed!")
        self.window.append_output("You may now run additional tools or export the results.")
        self.window.append_separator()
    
    def run(self):
        """Start the application"""
        self.window.run()


def main():
    """Main entry point"""
    try:
        app = HealthCheckApp()
        app.run()
    except KeyboardInterrupt:
        print("Application interrupted by user")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
