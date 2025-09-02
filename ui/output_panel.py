"""
DOS-style Output Panel Component
Real-time command output display with retro DOS aesthetic
"""

import customtkinter as ctk
import tkinter as tk
from typing import Optional


class OutputPanel:
    """DOS-style output panel with Windows 95 retro styling"""
    
    def __init__(self, parent):
        self.parent = parent
        
        # Create the main frame with retro styling
        self.frame = ctk.CTkFrame(
            parent,
            fg_color="#c0c0c0",  # Windows 95 gray
            border_color="#808080",
            border_width=2,
            corner_radius=0
        )
        
        self._create_output_display()
    
    def _create_output_display(self):
        """Create the DOS-style output display"""
        # Title
        title_label = ctk.CTkLabel(
            self.frame,
            text="Output Console",
            font=ctk.CTkFont(family="MS Sans Serif", size=15, weight="bold"),
            text_color="#000000",
            fg_color="transparent"
        )
        title_label.pack(pady=(10, 8))
        
        # Control buttons frame (pack at bottom first to reserve space)
        controls_frame = ctk.CTkFrame(
            self.frame,
            fg_color="transparent",
            corner_radius=0,
            height=30  # Fixed height to ensure it stays visible
        )
        controls_frame.pack(side="bottom", fill="x", pady=(3, 8), padx=10)
        controls_frame.pack_propagate(False)  # Prevent shrinking
        
        # Create the DOS-style output area (fills remaining space)
        output_frame = ctk.CTkFrame(
            self.frame,
            fg_color="#000000",  # Black background like DOS
            border_color="#808080",
            border_width=2,
            corner_radius=0
        )
        output_frame.pack(fill="both", expand=True, pady=(3, 0), padx=15)
        
        # Create text widget with DOS styling
        self.text_widget = tk.Text(
            output_frame,
            bg="#000000",           # Black background
            fg="#00ff00",           # Green text (classic DOS)
            font=("Consolas", 12),  # Monospace font
            insertbackground="#00ff00",  # Green cursor
            selectbackground="#008000",  # Dark green selection
            selectforeground="#ffffff",  # White selected text
            wrap=tk.WORD,
            state=tk.DISABLED,      # Read-only by default
            relief="flat",
            borderwidth=0
        )
        
        # Create scrollbar with retro styling
        scrollbar = tk.Scrollbar(
            output_frame,
            orient="vertical",
            command=self.text_widget.yview,
            bg="#c0c0c0",
            troughcolor="#808080",
            activebackground="#d4d0c8"
        )
        
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Pack text widget and scrollbar
        scrollbar.pack(side="right", fill="y")
        self.text_widget.pack(side="left", fill="both", expand=True)
        
        # Clear button
        clear_btn = ctk.CTkButton(
            controls_frame,
            text="Clear",
            command=self.clear_output,
            width=70,
            height=22,
            corner_radius=0,
            fg_color="#c0c0c0",
            text_color="#000000",
            border_color="#808080",
            border_width=1,
            hover_color="#d4d0c8",
            font=ctk.CTkFont(family="MS Sans Serif", size=10)
        )
        clear_btn.pack(side="left")
        
        # Auto-scroll checkbox
        self.auto_scroll_var = tk.BooleanVar(value=True)
        auto_scroll_cb = ctk.CTkCheckBox(
            controls_frame,
            text="Auto-scroll",
            variable=self.auto_scroll_var,
            font=ctk.CTkFont(family="MS Sans Serif", size=10),
            text_color="#000000",
            fg_color="#c0c0c0",
            checkmark_color="#000000",
            border_color="#808080",
            hover_color="#d4d0c8",
            corner_radius=0,
            border_width=1
        )
        auto_scroll_cb.pack(side="right")
        
        # Initialize with welcome message
        self.append_output("Select maintenance tools and click RUN to begin...")
        self.append_output("")
    
    def append_output(self, text: str, color: Optional[str] = None):
        """
        Append text to the output display
        
        Args:
            text: Text to append
            color: Optional color override (hex format)
        """
        self.text_widget.configure(state=tk.NORMAL)
        
        # Configure color tags if needed
        if color:
            tag_name = f"color_{color.replace('#', '')}"
            self.text_widget.tag_configure(tag_name, foreground=color)
            self.text_widget.insert(tk.END, text + "\n", tag_name)
        else:
            self.text_widget.insert(tk.END, text + "\n")
        
        # Auto-scroll to bottom if enabled
        if self.auto_scroll_var.get():
            self.text_widget.see(tk.END)
        
        self.text_widget.configure(state=tk.DISABLED)
        
        # Force update to show text immediately
        self.text_widget.update_idletasks()
    
    def append_command(self, command: str):
        """Append a command line with special formatting"""
        self.append_output(f"C:\\> {command}", "#ffff00")  # Yellow for commands
    
    def append_success(self, text: str):
        """Append success message in green"""
        self.append_output(f"✓ {text}", "#00ff00")
    
    def append_error(self, text: str):
        """Append error message in red"""
        self.append_output(f"✗ {text}", "#ff0000")
    
    def append_warning(self, text: str):
        """Append warning message in yellow"""
        self.append_output(f"⚠ {text}", "#ffff00")
    
    def append_info(self, text: str):
        """Append info message in cyan"""
        self.append_output(f"ℹ {text}", "#00ffff")
    
    def append_separator(self):
        """Append a visual separator"""
        self.append_output("=" * 60, "#808080")
    
    def clear_output(self):
        """Clear all output"""
        self.text_widget.configure(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.configure(state=tk.DISABLED)
        
        # Re-add welcome message
        self.append_output("Output cleared - Ready for new commands")
        self.append_output("")
    
    def set_auto_scroll(self, enabled: bool):
        """Enable or disable auto-scrolling"""
        self.auto_scroll_var.set(enabled)
    
    def pack(self, **kwargs):
        """Pack the frame"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the frame"""
        self.frame.grid(**kwargs)
