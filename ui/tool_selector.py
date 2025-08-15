"""
Maintenance Tool Selection Component
Provides checkboxes for selecting Windows maintenance tools
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import PhotoImage
import subprocess
import os
import sys
from typing import Dict, List, Callable
from PIL import Image, ImageTk
import tempfile


class ToolSelectorPanel:
    """Tool selection panel with Windows 95 styling"""
    
    def __init__(self, parent):
        self.parent = parent
        self.checkboxes: Dict[str, ctk.CTkCheckBox] = {}
        self.tool_states: Dict[str, bool] = {}
        
        # Define available tools
        self.tools = [
            ("dism_check", "DISM Check Health", "Quick check for image corruption"),
            ("dism_scan", "DISM Scan Health", "Deep scan for image corruption"),
            ("sfc_scan", "System File Checker", "Scan and repair system files"),
            ("chkdsk_check", "Check Disk (C:)", "Check disk for errors")
        ]
        
        # Create the main frame with retro styling
        self.frame = ctk.CTkFrame(
            parent,
            fg_color="#c0c0c0",  # Windows 95 gray
            border_color="#808080",
            border_width=2,
            corner_radius=0  # Sharp corners for retro look
        )
        
        self._create_tool_selection()
    
    def _create_tool_selection(self):
        """Create the tool selection interface"""
        # Title
        title_label = ctk.CTkLabel(
            self.frame,
            text="Diagnostic Tools",
            font=ctk.CTkFont(family="MS Sans Serif", size=13, weight="bold"),
            text_color="#000000",
            fg_color="transparent"
        )
        title_label.pack(pady=(15, 20))
        
        # Create checkboxes for each tool
        for tool_id, tool_name, tool_desc in self.tools:
            self._create_tool_checkbox(tool_id, tool_name, tool_desc)
        
        # Control buttons frame
        controls_frame = ctk.CTkFrame(
            self.frame,
            fg_color="transparent",
            corner_radius=0
        )
        controls_frame.pack(pady=20, padx=15, fill="x")
        
        # Select All button
        select_all_btn = ctk.CTkButton(
            controls_frame,
            text="Select All",
            command=self.select_all_tools,
            width=80,
            height=25,
            corner_radius=0,
            fg_color="#c0c0c0",
            text_color="#000000",
            border_color="#808080",
            border_width=1,
            hover_color="#d4d0c8",
            font=ctk.CTkFont(family="MS Sans Serif", size=11)
        )
        select_all_btn.pack(side="left", padx=(0, 5))
        
        # Clear All button
        clear_all_btn = ctk.CTkButton(
            controls_frame,
            text="Clear All",
            command=self.clear_all_tools,
            width=80,
            height=25,
            corner_radius=0,
            fg_color="#c0c0c0",
            text_color="#000000",
            border_color="#808080",
            border_width=1,
            hover_color="#d4d0c8",
            font=ctk.CTkFont(family="MS Sans Serif", size=11)
        )
        clear_all_btn.pack(side="left", padx=5)
        
        # Run Selected button (large and prominent)
        self.run_button = ctk.CTkButton(
            self.frame,
            text="SELECT TOOLS TO RUN",
            command=self._on_run_clicked,
            width=220,
            height=40,
            corner_radius=0,
            fg_color="#008080",  # Windows 95 teal
            text_color="#ffffff",
            border_color="#004040",
            border_width=2,
            hover_color="#006060",
            font=ctk.CTkFont(family="MS Sans Serif", size=12, weight="bold")
        )
        self.run_button.pack(pady=(5, 8))
        
        # Reliability History button
        reliability_btn = ctk.CTkButton(
            self.frame,
            text="View Reliability History",
            command=self._open_reliability_history,
            width=220,
            height=30,
            corner_radius=0,
            fg_color="#800080",  # Purple - retro Windows color
            text_color="#ffffff",
            border_color="#400040",
            border_width=2,
            hover_color="#600060",
            font=ctk.CTkFont(family="MS Sans Serif", size=11)
        )
        reliability_btn.pack(pady=(3, 8))
        
        # System Tools section
        self._create_system_tools_section()
        
        # Initialize with recommended defaults
        self.set_defaults()
    
    def _create_tool_checkbox(self, tool_id: str, tool_name: str, tool_desc: str):
        """Create a checkbox for a maintenance tool"""
        # Container for checkbox and description
        tool_frame = ctk.CTkFrame(
            self.frame,
            fg_color="transparent",
            corner_radius=0
        )
        tool_frame.pack(pady=4, padx=20, fill="x")
        
        # Checkbox
        checkbox = ctk.CTkCheckBox(
            tool_frame,
            text=tool_name,
                            font=ctk.CTkFont(family="MS Sans Serif", size=12),
            text_color="#000000",
            fg_color="#c0c0c0",
            checkmark_color="#000000",
            border_color="#808080",
            hover_color="#d4d0c8",
            corner_radius=0,
            border_width=1
        )
        checkbox.pack(anchor="w")
        
        # Store checkbox reference
        self.checkboxes[tool_id] = checkbox
        self.tool_states[tool_id] = False
        
        # Bind checkbox change event
        checkbox.configure(command=lambda: self._on_tool_toggled(tool_id))
    
    def _on_tool_toggled(self, tool_id: str):
        """Handle tool checkbox toggle"""
        self.tool_states[tool_id] = self.checkboxes[tool_id].get()
        self._update_run_button()
    
    def _update_run_button(self):
        """Update run button state based on selections"""
        selected_count = sum(1 for state in self.tool_states.values() if state)
        
        if selected_count > 0:
            self.run_button.configure(
                text=f"RUN {selected_count} SELECTED TOOL{'S' if selected_count != 1 else ''}",
                state="normal"
            )
        else:
            self.run_button.configure(
                text="SELECT TOOLS TO RUN",
                state="disabled"
            )
    
    def _on_run_clicked(self):
        """Handle run button click"""
        # This will be connected to the main app's run method
        if hasattr(self, 'run_callback') and self.run_callback:
            self.run_callback(self.get_selected_tools())
    
    def set_run_callback(self, callback: Callable):
        """Set the callback function for when run is clicked"""
        self.run_callback = callback
    
    def select_all_tools(self):
        """Select all available tools"""
        for tool_id, checkbox in self.checkboxes.items():
            checkbox.select()
            self.tool_states[tool_id] = True
        self._update_run_button()
    
    def clear_all_tools(self):
        """Clear all tool selections"""
        for tool_id, checkbox in self.checkboxes.items():
            checkbox.deselect()
            self.tool_states[tool_id] = False
        self._update_run_button()
    
    def set_defaults(self):
        """Set recommended default selections"""
        # Start with all tools unchecked (user request)
        for tool_id in self.checkboxes:
            self.checkboxes[tool_id].deselect()
            self.tool_states[tool_id] = False
        
        self._update_run_button()
    
    def get_selected_tools(self) -> List[str]:
        """Get list of selected tool IDs"""
        return [tool_id for tool_id, state in self.tool_states.items() if state]
    
    def set_enabled(self, enabled: bool):
        """Enable or disable all controls"""
        state = "normal" if enabled else "disabled"
        
        for checkbox in self.checkboxes.values():
            checkbox.configure(state=state)
        
        if enabled:
            self._update_run_button()
        else:
            self.run_button.configure(state="disabled")
    
    def _extract_icon_from_exe(self, exe_path: str, size: int = 32) -> tk.PhotoImage:
        """Extract icon from Windows executable"""
        try:
            # Try to extract icon using Windows API
            import win32gui
            import win32ui
            import win32con
            import win32api
            
            # Get the icon handle from the executable
            large, small = win32gui.ExtractIconEx(exe_path, 0)
            if small:
                icon_handle = small[0]
            elif large:
                icon_handle = large[0]
            else:
                return None
            
            # Convert to bitmap
            hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
            hbmp = win32ui.CreateBitmap()
            hbmp.CreateCompatibleBitmap(hdc, size, size)
            hdc = hdc.CreateCompatibleDC()
            hdc.SelectObject(hbmp)
            hdc.FillSolidRect((0, 0, size, size), 0xffffff)
            
            # Draw the icon
            win32gui.DrawIconEx(hdc.GetHandleOutput(), 0, 0, icon_handle, size, size, 0, None, win32con.DI_NORMAL)
            
            # Convert to PIL Image
            bmpstr = hbmp.GetBitmapBits(True)
            img = Image.frombuffer('RGB', (size, size), bmpstr, 'raw', 'BGRX', 0, 1)
            
            # Convert to PhotoImage
            return ImageTk.PhotoImage(img)
            
        except Exception:
            # Fallback: return None if icon extraction fails
            return None
    
    def _find_exe_path(self, exe_name: str) -> str:
        """Find full path to Windows executable"""
        try:
            # Try system32 first
            system32_path = os.path.join(os.environ.get('SYSTEMROOT', 'C:\\Windows'), 'System32', exe_name)
            if os.path.exists(system32_path):
                return system32_path
            
            # Try windows directory
            windows_path = os.path.join(os.environ.get('SYSTEMROOT', 'C:\\Windows'), exe_name)
            if os.path.exists(windows_path):
                return windows_path
            
            # Try PATH
            import shutil
            path = shutil.which(exe_name)
            if path:
                return path
                
        except Exception:
            pass
        
        return exe_name  # Return original if not found
    
    def _create_system_tools_section(self):
        """Create system tools section with icon buttons"""        
        # Tools data (removed Performance Monitor)
        system_tools = [
            ("eventvwr.exe", "Event\nViewer", self._open_event_viewer),
            ("resmon.exe", "Resource\nMonitor", self._open_resource_monitor),
            ("msinfo32.exe", "System\nInfo", self._open_system_info),
            ("mdsched.exe", "Memory\nDiagnostic", self._open_memory_diagnostic)
        ]
        
        # Create grid container
        tools_grid = ctk.CTkFrame(
            self.frame,
            fg_color="transparent",
            corner_radius=0
        )
        tools_grid.pack(pady=(5, 15), padx=15, fill="x")
        
        # Create tool buttons in grid (2 columns)
        for i, (exe_name, tool_name, command) in enumerate(system_tools):
            row = i // 2
            col = i % 2
            
            # Extract icon from executable
            exe_path = self._find_exe_path(exe_name)
            icon_image = self._extract_icon_from_exe(exe_path, 24)
            
            # Create tool button with icon
            if icon_image:
                # Create button with icon and text
                tool_btn = tk.Button(
                    tools_grid,
                    text=tool_name,
                    image=icon_image,
                    compound=tk.TOP,
                    command=command,
                    width=85,
                    height=55,
                    bg="#d4d0c8",
                    fg="#000000",
                    relief=tk.RAISED,
                    bd=1,
                    font=("MS Sans Serif", 8),
                    activebackground="#e4e0d8"
                )
                # Keep a reference to prevent garbage collection
                tool_btn.image = icon_image
            else:
                # Fallback to text-only button
                tool_btn = ctk.CTkButton(
                    tools_grid,
                    text=tool_name,
                    command=command,
                    width=85,
                    height=45,
                    corner_radius=0,
                    fg_color="#d4d0c8",
                    text_color="#000000",
                    border_color="#808080",
                    border_width=1,
                    hover_color="#e4e0d8",
                    font=ctk.CTkFont(family="MS Sans Serif", size=8)
                )
            
            tool_btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")
        
        # Configure grid weights for equal spacing
        tools_grid.grid_columnconfigure(0, weight=1)
        tools_grid.grid_columnconfigure(1, weight=1)
    
    def _open_event_viewer(self):
        """Open Event Viewer"""
        try:
            subprocess.run("eventvwr.exe", shell=True, check=False)
        except Exception:
            pass
    
    def _open_resource_monitor(self):
        """Open Resource Monitor"""
        try:
            subprocess.run("resmon.exe", shell=True, check=False)
        except Exception:
            pass
    
    def _open_system_info(self):
        """Open System Information"""
        try:
            subprocess.run("msinfo32.exe", shell=True, check=False)
        except Exception:
            pass
    
    def _open_memory_diagnostic(self):
        """Open Windows Memory Diagnostic"""
        try:
            subprocess.run("mdsched.exe", shell=True, check=False)
        except Exception:
            pass
    
    def _open_reliability_history(self):
        """Open Windows Reliability History"""
        import subprocess
        try:
            # Open Reliability Monitor directly
            subprocess.run("perfmon.exe /rel", shell=True, check=False)
        except Exception as e:
            # Fallback: try opening Control Panel path
            try:
                subprocess.run("control.exe /name Microsoft.ActionCenter /page pageReliabilityView", shell=True, check=False)
            except Exception:
                # Last resort: try direct executable
                try:
                    subprocess.run("ReliabilityMonitor.exe", shell=True, check=False)
                except Exception:
                    pass  # Silently fail if none work
    
    def pack(self, **kwargs):
        """Pack the frame"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the frame"""
        self.frame.grid(**kwargs)
