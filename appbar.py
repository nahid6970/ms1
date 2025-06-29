
import ctypes
from ctypes import wintypes

# Constants for SHAppBarMessage
ABM_NEW = 0x00000000
ABM_REMOVE = 0x00000001
ABM_QUERYPOS = 0x00000002
ABM_SETPOS = 0x00000003
ABM_GETSTATE = 0x00000004
ABM_GETTASKBARPOS = 0x00000005
ABM_ACTIVATE = 0x00000006
ABM_GETAUTOHIDEBAR = 0x00000007
ABM_SETAUTOHIDEBAR = 0x00000008
ABM_WINDOWPOSCHANGED = 0x00000009
ABM_SETSTATE = 0x0000000A

# Constants for App Bar Edges
ABE_LEFT = 0
ABE_TOP = 1
ABE_RIGHT = 2
ABE_BOTTOM = 3

class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("hWnd", wintypes.HWND),
        ("uCallbackMessage", wintypes.UINT),
        ("uEdge", wintypes.UINT),
        ("rc", wintypes.RECT),
        ("lParam", wintypes.LPARAM),
    ]

def register_appbar(hwnd, u_callback_message):
    """Registers the window as an appbar."""
    abd = APPBARDATA()
    abd.cbSize = ctypes.sizeof(APPBARDATA)
    abd.hWnd = hwnd
    abd.uCallbackMessage = u_callback_message
    
    ctypes.windll.shell32.SHAppBarMessage(ABM_NEW, ctypes.byref(abd))
    return abd

def unregister_appbar(hwnd):
    """Unregisters the window as an appbar."""
    abd = APPBARDATA()
    abd.cbSize = ctypes.sizeof(APPBARDATA)
    abd.hWnd = hwnd
    
    ctypes.windll.shell32.SHAppBarMessage(ABM_REMOVE, ctypes.byref(abd))

def set_appbar_position(hwnd, edge, width, height, screen_width, screen_height):
    """Sets the position of the appbar."""
    abd = APPBARDATA()
    abd.cbSize = ctypes.sizeof(APPBARDATA)
    abd.hWnd = hwnd
    abd.uEdge = edge

    if edge == ABE_TOP:
        abd.rc.top = 0
        abd.rc.left = 0
        abd.rc.right = screen_width
        abd.rc.bottom = height
    elif edge == ABE_BOTTOM:
        abd.rc.top = screen_height - height
        abd.rc.left = 0
        abd.rc.right = screen_width
        abd.rc.bottom = screen_height
    
    ctypes.windll.shell32.SHAppBarMessage(ABM_QUERYPOS, ctypes.byref(abd))
    ctypes.windll.shell32.SHAppBarMessage(ABM_SETPOS, ctypes.byref(abd))
