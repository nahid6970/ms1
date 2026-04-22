
import os
import sys

def show_popup():
    # Width 77 includes borders
    inner_width = 75
    
    def line(text=""):
        return f" │ {text.ljust(inner_width)} │"

    def center(text=""):
        return f" │ {text.center(inner_width)} │"

    def divider():
        return f" ├{'─' * (inner_width + 2)}┤"

    content = [
        f" ┌{'─' * (inner_width + 2)}┐",
        center("SHORTCUTS MENU"),
        center("(Cyberpunk Ed.)"),
        divider(),
        line(" [ FUNCTION KEYS ]"),
        line(" F1         : Show this shortcuts help window"),
        line(" F2         : Toggle image preview mode (chafa/viu vs QuickLook)"),
        line(" F3         : Toggle view mode (Full Path vs Filename)"),
        line(" F4         : Refresh file list"),
        line(" F5         : Toggle bookmark on/off (Prompts for custom name)"),
        line(" F6         : Rename bookmark custom name"),
        line(),
        line(" [ CONTROL KEYS ]"),
        line(" Ctrl-C     : Copy full file path to clipboard"),
        line(" Ctrl-N     : Open file with Editor Chooser"),
        line(" Ctrl-O     : Open file location in Explorer"),
        line(" Ctrl-P     : Toggle preview window on/off"),
        line(" Ctrl-R     : Run file with PowerShell Start-Process"),
        line(),
        line(" [ NAVIGATION & OTHER ]"),
        line(" Alt-Up     : Move bookmarked file up in order"),
        line(" Alt-Down   : Move bookmarked file down in order"),
        line(" Enter      : Show action menu (Editor/Folder/Run/Copy/Terminal)"),
        line(" Tab        : Multi-select files"),
        line(" ?          : Toggle the top help header"),
        f" └{'─' * (inner_width + 2)}┘",
        "   Bookmarked files (marked with *) appear first in the list!",
        "",
        "   [ Press ENTER to return ]"
    ]

    # Use ANSI to clear screen and print
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n" + "\n".join(content))
    
    # Wait for enter
    try:
        con_path = 'CON' if os.name == 'nt' else '/dev/tty'
        with open(con_path, 'r') as f_in:
            f_in.readline()
    except:
        pass

if __name__ == "__main__":
    show_popup()
