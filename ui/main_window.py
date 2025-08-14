"""
Main Window Component
Windows 95 styled main interface for Windows Health Check Tool
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Optional, Callable, List
import datetime
import os
import sys

from .system_info import SystemInfoPanel
from .tool_selector import ToolSelectorPanel
from .output_panel import OutputPanel


class MainWindow:
    """Main application window with Windows 95 retro styling"""

    def __init__(self, run_callback: Optional[Callable] = None):
        self.run_callback = run_callback

        # Configure CustomTkinter for Windows 95 look
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Create main window
        self.root = ctk.CTk()
        self.root.title("Windows Health Check Tool")
        self.root.geometry("1000x800")
        self.root.minsize(700, 600)

        # Set window icon
        self._set_window_icon()

        # Configure Windows 95 styling
        self.root.configure(fg_color="#c0c0c0")

        self._create_interface()

        # Connect run callback
        if run_callback:
            self.tool_selector.set_run_callback(run_callback)
    
    def _get_icon_path(self):
        """Get the path to the icon file, works for both development and packaged executable"""
        if getattr(sys, 'frozen', False):
            # Running as packaged executable - PyInstaller extracts to sys._MEIPASS
            application_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        else:
            # Running as script
            application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        icon_path = os.path.join(application_path, 'icon.ico')
        return icon_path if os.path.exists(icon_path) else None
    
    def _set_window_icon(self):
        """Set the window icon using the icon.ico file"""
        try:
            icon_path = self._get_icon_path()
            if icon_path and os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            # Silently fail if icon can't be loaded - don't break the app
            pass
    
    def _create_interface(self):
        """Create the main interface layout"""
        # Create menu bar (Windows 95 style)
        self._create_menu_bar()
        
        # Main title with Windows logo gradient
        self._create_gradient_title_bar()
        
        # System information panel (top)
        self.system_info = SystemInfoPanel(self.root)
        self.system_info.pack(fill="x", padx=15, pady=(15, 10))
        
        # Bottom status bar (pack first to reserve space)
        self._create_status_bar()
        
        # Main content area (horizontal layout) - fill remaining space
        content_frame = ctk.CTkFrame(
            self.root,
            fg_color="transparent",
            corner_radius=0
        )
        content_frame.pack(fill="both", expand=True, padx=15, pady=(5, 10))
        
        # Left panel - Tool selector (fixed width for better proportions)
        self.tool_selector = ToolSelectorPanel(content_frame)
        self.tool_selector.pack(side="left", fill="y", padx=(0, 10))
        # Set a minimum width for the tool selector
        self.tool_selector.frame.configure(width=280)
        
        # Right panel - Output display
        self.output_panel = OutputPanel(content_frame)
        self.output_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
    
    def _create_menu_bar(self):
        """Create Windows 95 style menu bar"""
        # Note: CustomTkinter doesn't have native menu support, so we'll create a frame
        menu_frame = ctk.CTkFrame(
            self.root,
            fg_color="#c0c0c0",
            corner_radius=0,
            height=25,
            border_color="#808080",
            border_width=1
        )
        menu_frame.pack(fill="x", padx=2, pady=2)
        menu_frame.pack_propagate(False)
        
        # File menu button with dropdown
        self.file_btn = ctk.CTkButton(
            menu_frame,
            text="File",
            width=50,
            height=20,
            corner_radius=0,
            fg_color="transparent",
            text_color="#000000",
            hover_color="#d4d0c8",
            font=ctk.CTkFont(family="MS Sans Serif", size=12),
            command=self._show_file_menu
        )
        self.file_btn.pack(side="left", padx=2, pady=2)
        
        # Create the file menu dropdown
        self.file_menu = tk.Menu(self.root, tearoff=0, font=("MS Sans Serif", 9))
        self.file_menu.add_command(label="Save Output to File...", command=self._save_output)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        

        
        # Help menu button
        help_btn = ctk.CTkButton(
            menu_frame,
            text="Help",
            width=50,
            height=20,
            corner_radius=0,
            fg_color="transparent",
            text_color="#000000",
            hover_color="#d4d0c8",
            font=ctk.CTkFont(family="MS Sans Serif", size=12),
            command=self._show_help_menu
        )
        help_btn.pack(side="left", padx=2, pady=2)
    
    def _create_gradient_title_bar(self):
        """Create a gradient title bar inspired by the Windows logo colors"""
        # Container frame for the title bar
        title_container = ctk.CTkFrame(
            self.root,
            fg_color="transparent",
            corner_radius=0,
            height=40
        )
        title_container.pack(fill="x", padx=2, pady=(2, 0))
        title_container.pack_propagate(False)
        
        # Create canvas for gradient drawing
        self.title_canvas = tk.Canvas(
            title_container,
            height=40,
            highlightthickness=0,
            relief="flat"
        )
        self.title_canvas.pack(fill="both", expand=True)
        
        # Draw the gradient and text when the canvas is ready
        self.title_canvas.after_idle(self._draw_gradient_title)
        
        # Bind resize event to redraw gradient
        self.title_canvas.bind("<Configure>", self._on_title_canvas_resize)
    
    def _draw_gradient_title(self):
        """Draw the Windows logo inspired gradient background with title text"""
        # Clear canvas
        self.title_canvas.delete("all")
        
        # Get canvas dimensions
        width = self.title_canvas.winfo_width()
        height = self.title_canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return  # Canvas not ready yet
        
        # Windows logo colors (Red, Green, Blue, Yellow)
        colors = [
            "#F25022",  # Red
            "#7FBA00",  # Green  
            "#00A4EF",  # Blue
            "#FFB900"   # Yellow
        ]
        
        # Create horizontal gradient
        segment_width = width / len(colors)
        
        for i, color in enumerate(colors):
            x1 = int(i * segment_width)
            x2 = int((i + 1) * segment_width)
            
            # For smooth transitions, we'll create many thin rectangles with interpolated colors
            if i < len(colors) - 1:
                next_color = colors[i + 1]
                # Create smooth transition over the segment
                for x in range(x1, x2):
                    # Calculate interpolation factor (0.0 to 1.0)
                    factor = (x - x1) / segment_width if segment_width > 0 else 0
                    
                    # Interpolate between current and next color
                    interpolated_color = self._interpolate_color(color, next_color, factor)
                    
                    self.title_canvas.create_line(
                        x, 0, x, height,
                        fill=interpolated_color,
                        width=1
                    )
            else:
                # Last segment - solid color
                self.title_canvas.create_rectangle(
                    x1, 0, x2, height,
                    fill=color,
                    outline=color
                )
        
        # Add title text with shadow effect for better readability
        title_text = "Windows Health Check Tool"
        
        # Text shadow (slightly offset)
        self.title_canvas.create_text(
            width // 2 + 1, height // 2 + 1,
            text=title_text,
            font=("MS Sans Serif", 15, "bold"),
            fill="#000000",  # Black shadow
            anchor="center"
        )
        
        # Main text
        self.title_canvas.create_text(
            width // 2, height // 2,
            text=title_text,
            font=("MS Sans Serif", 15, "bold"),
            fill="#ffffff",  # White text
            anchor="center"
        )
    
    def _interpolate_color(self, color1, color2, factor):
        """Interpolate between two hex colors"""
        # Convert hex to RGB
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        
        # Interpolate
        r = int(r1 + (r2 - r1) * factor)
        g = int(g1 + (g2 - g1) * factor)
        b = int(b1 + (b2 - b1) * factor)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _on_title_canvas_resize(self, event):
        """Redraw gradient when canvas is resized"""
        self.title_canvas.after_idle(self._draw_gradient_title)
    
    def _create_status_bar(self):
        """Create bottom status bar with progress"""
        status_frame = ctk.CTkFrame(
            self.root,
            fg_color="#c0c0c0",
            corner_radius=0,
            height=40,
            border_color="#808080",
            border_width=1
        )
        status_frame.pack(side="bottom", fill="x", padx=2, pady=(0, 2))
        status_frame.pack_propagate(False)
        
        # Status text (on the left)
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready",
            font=ctk.CTkFont(family="MS Sans Serif", size=12),
            text_color="#000000"
        )
        self.status_label.pack(side="left", padx=15)
        
        # Progress bar (expanding to fill middle space)
        self.progress_bar = ctk.CTkProgressBar(
            status_frame,
            height=18,
            corner_radius=0,
            fg_color="#808080",
            progress_color="#008080"
        )
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=15, pady=11)
        self.progress_bar.set(0)
        
        # Admin status
        admin_status = "✓ Administrator" if hasattr(self, 'is_admin') else "✓ Administrator"
        admin_label = ctk.CTkLabel(
            status_frame,
            text=admin_status,
            font=ctk.CTkFont(family="MS Sans Serif", size=12),
            text_color="#008000"  # Green for admin status
        )
        admin_label.pack(side="right", padx=15)
    
    def _show_file_menu(self):
        """Show file menu dropdown directly below the File button"""
        try:
            # Update the button to get current geometry
            self.file_btn.update_idletasks()
            
            # Get the exact button coordinates
            button_x = self.file_btn.winfo_rootx()
            button_y = self.file_btn.winfo_rooty()
            button_height = self.file_btn.winfo_height()
            
            # Position the menu directly below the button
            menu_x = button_x
            menu_y = button_y + button_height
            
            # Show the dropdown menu
            self.file_menu.tk_popup(menu_x, menu_y)
        except Exception as e:
            # Fallback: try to position relative to root window
            try:
                x = self.root.winfo_rootx() + 10
                y = self.root.winfo_rooty() + 50
                self.file_menu.tk_popup(x, y)
            except Exception:
                # Last resort fallback
                self.file_menu.tk_popup(100, 100)
    
    def _save_output(self):
        """Save current output to a text file"""
        try:
            # Get current output text
            output_text = self.output_panel.text_widget.get("1.0", "end-1c")
            
            if not output_text.strip():
                messagebox.showwarning("No Output", "There is no output to save.")
                return
            
            # Default filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"health_check_results_{timestamp}.txt"
            
            # Open save dialog
            filename = filedialog.asksaveasfilename(
                title="Save Output",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=default_filename
            )
            
            if filename:
                # Create comprehensive report
                report_content = self._generate_report(output_text)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                
                messagebox.showinfo("Saved", f"Output saved to:\n{filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save output:\n{str(e)}")
    
    def _generate_report(self, output_text: str) -> str:
        """Generate a comprehensive report with system info and output"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Get system info if available
        system_info = ""
        if hasattr(self, 'system_info'):
            system_info = self.system_info._format_system_info()
        
        report = f"""
========================================
Windows Health Check Tool - Report
========================================
Generated: {timestamp}

System Information:
{system_info}

========================================
Execution Output:
========================================
{output_text}

========================================
End of Report
========================================
"""
        return report
    
    def _center_window(self, window, width, height):
        """Center a window relative to the main application window"""
        try:
            # Update the main window to get current geometry
            self.root.update_idletasks()
            
            # Get main window position and size
            main_x = self.root.winfo_rootx()
            main_y = self.root.winfo_rooty()
            main_width = self.root.winfo_width()
            main_height = self.root.winfo_height()
            
            # Calculate center position
            center_x = main_x + (main_width - width) // 2
            center_y = main_y + (main_height - height) // 2
            
            # Ensure the window doesn't go off-screen
            center_x = max(0, center_x)
            center_y = max(0, center_y)
            
            # Set the window position
            window.geometry(f"{width}x{height}+{center_x}+{center_y}")
            
        except Exception:
            # Fallback: center on screen
            window.geometry(f"{width}x{height}")
            window.update_idletasks()
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            window.geometry(f"{width}x{height}+{x}+{y}")

    def _show_help_menu(self):
        """Show help menu with diagnostic test explanations"""
        # Create help dialog
        help_window = tk.Toplevel(self.root)
        help_window.title("Help - Diagnostic Tests")
        help_window.geometry("600x500")
        help_window.configure(bg="#c0c0c0")
        help_window.resizable(True, True)
        
        # Center the window relative to the main application
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Calculate center position relative to parent window
        self._center_window(help_window, 600, 500)
        
        # Create scrollable text area
        frame = tk.Frame(help_window, bg="#c0c0c0")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create text widget with scrollbar
        text_frame = tk.Frame(frame, bg="#ffffff", relief="sunken", bd=2)
        text_frame.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")
        
        text_widget = tk.Text(
            text_frame,
            wrap="word",
            yscrollcommand=scrollbar.set,
            font=("MS Sans Serif", 10),
            bg="#ffffff",
            fg="#000000",
            padx=10,
            pady=10
        )
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=text_widget.yview)
        
        # Help content
        help_content = """
WINDOWS HEALTH CHECK TOOL - DIAGNOSTIC TESTS

This tool provides automated Windows system maintenance and diagnostic capabilities. Below are explanations of each diagnostic test:

════════════════════════════════════════════════════════

🔧 DISM CHECK HEALTH
Purpose: Quick check for Windows image corruption
What it does: Scans the Windows component store for any signs of corruption or inconsistencies
When to use: As a first step to identify potential system image problems
Time required: 5-10 seconds
Safe to run: Yes, read-only operation

════════════════════════════════════════════════════════

🔍 DISM SCAN HEALTH  
Purpose: Deep scan for Windows image corruption
What it does: Performs a thorough scan of the Windows component store to identify specific corruption issues
When to use: When CheckHealth indicates problems, or for comprehensive diagnostics
Time required: 2-5 minutes
Safe to run: Yes, read-only operation

════════════════════════════════════════════════════════

🛠️ DISM RESTORE HEALTH (Automatic)
Purpose: Repair Windows image corruption
What it does: Downloads clean files from Windows Update to replace corrupted system files
When to use: Only runs automatically when corruption is detected that can be repaired
Time required: 10-30 minutes
Safe to run: Yes, but requires internet connection for downloads
Note: This tool automatically prompts you to run this only when needed

════════════════════════════════════════════════════════

🔧 SYSTEM FILE CHECKER (SFC)
Purpose: Scan and repair Windows system files
What it does: Compares system files against a cached copy and replaces corrupted files
When to use: To fix corrupted system files, resolve stability issues
Time required: 3-5 minutes
Safe to run: Yes, has built-in protection mechanisms

════════════════════════════════════════════════════════

💽 CHECK DISK (CHKDSK) - Check Only
Purpose: Scan disk for errors without fixing
What it does: Examines the file system and metadata for logical inconsistencies
When to use: To identify disk problems before attempting repairs
Time required: 2-3 minutes
Safe to run: Yes, read-only operation

════════════════════════════════════════════════════════

💽 CHECK DISK (CHKDSK) - Fix Errors
Purpose: Scan and repair disk errors
What it does: Fixes file system errors, bad sector mapping, and metadata issues
When to use: When check-only mode finds errors that need repair
Time required: 10 minutes to several hours (depends on disk size)
Safe to run: Generally yes, but may require restart for system drive

════════════════════════════════════════════════════════

💡 RECOMMENDED USAGE:

1. Start with DISM Check Health and System File Checker for most issues
2. Use DISM Scan Health if Check Health finds problems  
3. Let the tool automatically prompt you for DISM Restore Health if needed
4. Use Check Disk tools if you suspect hardware/storage issues
5. Always ensure you have recent backups before running repair operations

════════════════════════════════════════════════════════

⚠️ IMPORTANT NOTES:

• All operations require Administrator privileges
• Some operations may require internet connection
• Repairs on system drive may require restart
• Large disks may take several hours for full check/repair
• Always save important work before running maintenance tools

════════════════════════════════════════════════════════

For more information about Windows system maintenance, consult Microsoft's official documentation or contact your system administrator.
"""
        
        text_widget.insert("1.0", help_content)
        text_widget.config(state="disabled")  # Make read-only
        
        # OK button
        button_frame = tk.Frame(help_window, bg="#c0c0c0")
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ok_btn = tk.Button(
            button_frame,
            text="OK",
            command=help_window.destroy,
            bg="#c0c0c0",
            font=("MS Sans Serif", 9),
            width=10,
            relief="raised",
            bd=2
        )
        ok_btn.pack(side="right")
    
    def update_progress(self, progress: float, status: str = ""):
        """
        Update the progress bar and status
        
        Args:
            progress: Progress value (0.0 to 1.0)
            status: Status message
        """
        self.progress_bar.set(progress)
        if status:
            self.status_label.configure(text=status)
        self.root.update_idletasks()
    
    def set_status(self, status: str):
        """Set the status bar text"""
        self.status_label.configure(text=status)
        self.root.update_idletasks()
    
    def get_selected_tools(self) -> List[str]:
        """Get the list of selected tools"""
        return self.tool_selector.get_selected_tools()
    
    def set_tools_enabled(self, enabled: bool):
        """Enable or disable tool selection"""
        self.tool_selector.set_enabled(enabled)
    
    def append_output(self, text: str, color: str = None):
        """Append text to output panel"""
        if color:
            self.output_panel.append_output(text, color)
        else:
            self.output_panel.append_output(text)
    
    def append_command(self, command: str):
        """Append command to output panel"""
        self.output_panel.append_command(command)
    
    def append_success(self, text: str):
        """Append success message to output panel"""
        self.output_panel.append_success(text)
    
    def append_error(self, text: str):
        """Append error message to output panel"""
        self.output_panel.append_error(text)
    
    def append_separator(self):
        """Append separator to output panel"""
        self.output_panel.append_separator()
    
    def clear_output(self):
        """Clear output panel"""
        self.output_panel.clear_output()
    
    def run(self):
        """Start the main event loop"""
        self.root.mainloop()
    
    def destroy(self):
        """Destroy the window"""
        self.root.destroy()
