"""
Admin privileges and UAC elevation utilities for Windows Health Check Tool
"""

import ctypes
import sys
import os
from typing import Optional


def is_admin() -> bool:
    """
    Check if the current process is running with administrative privileges
    
    Returns:
        True if running as admin, False otherwise
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def elevate_privileges() -> bool:
    """
    Attempt to elevate privileges using UAC prompt
    
    Returns:
        True if elevation was successful or already elevated, False otherwise
    """
    if is_admin():
        return True
    
    try:
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            executable = sys.executable
            arguments = " ".join(sys.argv[1:])
        else:
            # Running as Python script - need to launch python.exe with script
            executable = sys.executable
            script_path = os.path.abspath(sys.argv[0])
            arguments = f'"{script_path}" ' + " ".join(sys.argv[1:])
        
        # Attempt to run with elevated privileges
        result = ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas", 
            executable, 
            arguments, 
            None, 
            1  # SW_NORMAL
        )
        
        # If successful, the new elevated process will start
        # and this process should exit
        if result > 32:  # Success
            sys.exit(0)
        else:
            return False
            
    except Exception as e:
        print(f"Failed to elevate privileges: {e}")
        return False


def check_and_elevate() -> bool:
    """
    Check admin status and elevate if necessary
    
    Returns:
        True if admin privileges are available, False if user declined
    """
    if is_admin():
        return True
    
    # Show a warning message before elevating
    import tkinter as tk
    from tkinter import messagebox
    
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    result = messagebox.askyesno(
        "Administrator Privileges Required",
        "This application requires administrator privileges to run Windows maintenance tools.\n\n"
        "Would you like to restart with administrator privileges?",
        icon="warning"
    )
    
    root.destroy()
    
    if result:
        return elevate_privileges()
    else:
        return False


def get_admin_status_message() -> str:
    """
    Get a message describing the current admin status
    
    Returns:
        Status message string
    """
    if is_admin():
        return "✓ Running with Administrator privileges"
    else:
        return "⚠ Not running as Administrator - elevation required for maintenance tools"


# Test function
def test_admin():
    """Test admin detection and elevation"""
    print(f"Is admin: {is_admin()}")
    print(f"Status: {get_admin_status_message()}")


if __name__ == "__main__":
    test_admin()
