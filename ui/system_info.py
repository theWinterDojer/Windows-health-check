"""
System Information Display Component
Provides Windows system details in retro styling
"""

import platform
import psutil
import customtkinter as ctk
from typing import Dict, Any


class SystemInfoPanel:
    """System information display panel with Windows 95 styling"""
    
    def __init__(self, parent):
        self.parent = parent
        self.info_data = self._gather_system_info()
        
        # Create the main frame with retro styling
        self.frame = ctk.CTkFrame(
            parent,
            fg_color="#c0c0c0",  # Windows 95 gray
            border_color="#808080",
            border_width=2,
            corner_radius=0  # Sharp corners for retro look
        )
        
        self._create_info_display()
    
    def _gather_system_info(self) -> Dict[str, Any]:
        """Gather current system information"""
        try:
            # Get OS information
            os_info = f"{platform.system()} {platform.release()}"
            if hasattr(platform, 'platform'):
                os_info += f" ({platform.platform().split('-')[0]})"
            
            # Get memory information
            memory = psutil.virtual_memory()
            memory_gb = round(memory.total / (1024**3), 1)
            memory_free_gb = round(memory.available / (1024**3), 1)
            memory_used_percent = memory.percent
            
            # Get disk information for C: drive
            try:
                disk = psutil.disk_usage('C:')
                disk_total_gb = round(disk.total / (1024**3), 1)
                disk_free_gb = round(disk.free / (1024**3), 1)
                disk_used_percent = round((disk.used / disk.total) * 100, 1)
            except:
                disk_total_gb = disk_free_gb = disk_used_percent = "N/A"
            
            # Get CPU information
            cpu_count = psutil.cpu_count()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            return {
                'os': os_info,
                'memory_total': memory_gb,
                'memory_free': memory_free_gb,
                'memory_used_percent': memory_used_percent,
                'disk_total': disk_total_gb,
                'disk_free': disk_free_gb,
                'disk_used_percent': disk_used_percent,
                'cpu_count': cpu_count,
                'cpu_percent': cpu_percent
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _create_info_display(self):
        """Create the system information display"""
        # Title
        title_label = ctk.CTkLabel(
            self.frame,
            text="System Information",
            font=ctk.CTkFont(family="MS Sans Serif", size=15, weight="bold"),
            text_color="#000000",
            fg_color="transparent"
        )
        title_label.pack(pady=(10, 15))
        
        # Create info text
        info_text = self._format_system_info()
        
        # Info display with monospace font
        info_label = ctk.CTkLabel(
            self.frame,
            text=info_text,
            font=ctk.CTkFont(family="Consolas", size=13),
            text_color="#000000",
            fg_color="transparent",
            justify="left"
        )
        info_label.pack(pady=(5, 15), padx=15)
    
    def _format_system_info(self) -> str:
        """Format system information for display"""
        if 'error' in self.info_data:
            return f"Error gathering system info: {self.info_data['error']}"
        
        info = self.info_data
        
        return (
            f"OS: {info['os']}\n"
            f"RAM: {info['memory_free']:.1f}GB free / {info['memory_total']:.1f}GB total "
            f"({100-info['memory_used_percent']:.1f}% free)\n"
            f"Disk C: {info['disk_free']:.1f}GB free / {info['disk_total']:.1f}GB total "
            f"({100-info['disk_used_percent']:.1f}% free)\n"
            f"CPU: {info['cpu_count']} cores ({info['cpu_percent']:.1f}% usage)"
        )
    
    def pack(self, **kwargs):
        """Pack the frame"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the frame"""
        self.frame.grid(**kwargs)
    
    def refresh(self):
        """Refresh system information"""
        self.info_data = self._gather_system_info()
        # Update the display
        for widget in self.frame.winfo_children():
            if isinstance(widget, ctk.CTkLabel) and "OS:" in widget.cget("text"):
                widget.configure(text=self._format_system_info())
                break
