"""
Maintenance Tool Selection Component
Provides checkboxes for selecting Windows maintenance tools
"""

import customtkinter as ctk
from typing import Dict, List, Callable


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
        self.run_button.pack(pady=(20, 15))
        
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
    
    def pack(self, **kwargs):
        """Pack the frame"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the frame"""
        self.frame.grid(**kwargs)
