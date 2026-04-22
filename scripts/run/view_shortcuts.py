
import os
import sys

def show_popup():
    content = r"""
 ┌───────────────────────────────────────────────────────────────────────────┐
 │                            SHORTCUTS MENU                                 │
 │                            (Cyberpunk Ed.)                                │
 ├───────────────────────────────────────────────────────────────────────────┤
 │  [ FUNCTION KEYS ]                                                        │
 │  F1        : Show this shortcuts help window                              │
 │  F2        : Toggle image preview mode (chafa/viu vs QuickLook)           │
 │  F3        : Toggle view mode (Full Path vs Filename)                     │
 │  F4        : Refresh file list                                            │
 │  F5        : Toggle bookmark on/off (Prompts for custom name)             │
 │  F6        : Rename bookmark custom name                                  │
 │                                                                           │
 │  [ CONTROL KEYS ]                                                         │
 │  Ctrl-C    : Copy full file path to clipboard                             │
 │  Ctrl-N    : Open file with Editor Chooser                                │
 │  Ctrl-O    : Open file location in Explorer                               │
 │  Ctrl-P    : Toggle preview window on/off                                 │
 │  Ctrl-R    : Run file with PowerShell Start-Process                       │
 │                                                                           │
 │  [ NAVIGATION & OTHER ]                                                   │
 │  Alt-Up    : Move bookmarked file up in order                             │
 │  Alt-Down  : Move bookmarked file down in order                           │
 │  Enter     : Show action menu (Editor/Folder/Run/Copy/Terminal)           │
 │  Tab       : Multi-select files                                           │
 │  ?         : Toggle the top help header                                   │
 └───────────────────────────────────────────────────────────────────────────┘
   Bookmarked files (marked with *) appear first in the list!
   
   [ Press ENTER to return ]
"""
    # Use ANSI to clear screen and print
    os.system('cls' if os.name == 'nt' else 'clear')
    print(content)
    
    # Wait for enter using direct console access
    try:
        con_path = 'CON' if os.name == 'nt' else '/dev/tty'
        with open(con_path, 'r') as f_in:
            f_in.readline()
    except:
        pass

if __name__ == "__main__":
    show_popup()
