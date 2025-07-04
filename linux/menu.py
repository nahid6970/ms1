import curses
import os
import subprocess
import threading
import time

# Define the menu structure
# Each menu item has:
# 'name': Display name
# 'type': 'menu' for a submenu, 'action' for an executable item
# 'action': (Optional) A function to call if 'type' is 'action'
# 'submenu': (Optional) A dictionary of submenu items if 'type' is 'menu'

MENUS = {
    "main": {
        "name": "Main Menu",
        "items": {
            "1": {"name": "Initial Setup", "type": "menu", "submenu": "initial_setup"},
            "2": {"name": "Application Setup", "type": "menu", "submenu": "application_setup"},
            "3": {"name": "Desktop Environments", "type": "menu", "submenu": "desktop_environments"},
            "0": {"name": "Exit", "type": "action", "action": "exit_program"},
        }
    },
    "initial_setup": {
        "name": "Initial Setup Menu",
        "items": {
            "1": {"name": "Example Initial Setup 1", "type": "action", "action": "example_initial_setup_1"},
            "2": {"name": "Example Initial Setup 2", "type": "action", "action": "example_initial_setup_2"},
            "0": {"name": "Back to Main Menu", "type": "action", "action": "go_back"},
        }
    },
    "application_setup": {
        "name": "Application Setup Menu",
        "items": {
            "1": {"name": "Example App Setup 1", "type": "action", "action": "example_app_setup_1"},
            "2": {"name": "Example App Setup 2", "type": "action", "action": "example_app_setup_2"},
            "0": {"name": "Back to Main Menu", "type": "action", "action": "go_back"},
        }
    },
    "desktop_environments": {
        "name": "Desktop Environments",
        "items": {
            "1": {"name": "Install Gnome", "type": "action", "action": "install_gnome"},
            "0": {"name": "Back to Main Menu", "type": "action", "action": "go_back"},
        }
    }
}

# Global state variables
current_menu_key = "main"
main_selected_row = 0
submenu_selected_row = 0
active_pane = "main" # "main" or "submenu"
menu_history = [] # Stack to keep track of menu navigation

# --- Action Functions ---
def _get_action_output_message(message):
    return message

def example_initial_setup_1():
    return _get_action_output_message("Executing Example Initial Setup 1...")

def example_initial_setup_2():
    return _get_action_output_message("Executing Example Initial Setup 2...")

def example_app_setup_1():
    return _get_action_output_message("Executing Example App Setup 1...")

def example_app_setup_2():
    return _get_action_output_message("Executing Example App Setup 2...")

def install_gnome():
    # This will use the live output display
    return None  # Signal that this should use live output

def execute_command_with_live_output(stdscr, command, title="Command Output"):
    """Execute a command and display live output in a popup window."""
    h, w = stdscr.getmaxyx()
    # Calculate position for the pop-up window
    popup_h = min(20, h - 4)  # Larger window for live output
    popup_w = min(80, w - 4)
    popup_y = (h - popup_h) // 2
    popup_x = (w - popup_w) // 2

    popup_win = curses.newwin(popup_h, popup_w, popup_y, popup_x)
    popup_win.box()
    popup_win.addstr(1, 2, title)
    popup_win.addstr(2, 2, "=" * (len(title)))
    popup_win.addstr(popup_h - 1, 2, "Press ESC to close when done...")
    popup_win.refresh()

    # Create a scrollable content area
    content_win = curses.newwin(popup_h - 5, popup_w - 4, popup_y + 3, popup_x + 2)
    content_win.scrollok(True)
    content_win.idlok(True)
    
    output_lines = []
    command_finished = False
    process = None
    
    def run_command():
        nonlocal command_finished, process
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            for line in iter(process.stdout.readline, ''):
                if line:
                    output_lines.append(line.rstrip())
            
            process.wait()
            if process.returncode == 0:
                output_lines.append("\n=== Command completed successfully ===")
            else:
                output_lines.append(f"\n=== Command failed with exit code {process.returncode} ===")
        except Exception as e:
            output_lines.append(f"\nError: {str(e)}")
        finally:
            command_finished = True
    
    # Start command in background thread
    thread = threading.Thread(target=run_command)
    thread.daemon = True
    thread.start()
    
    # Display loop
    scroll_pos = 0
    while True:
        # Clear content window
        content_win.clear()
        
        # Display output lines
        display_lines = output_lines[scroll_pos:scroll_pos + popup_h - 5]
        for i, line in enumerate(display_lines):
            if i < popup_h - 5:
                # Truncate line if too long
                display_line = line[:popup_w - 6] if len(line) > popup_w - 6 else line
                try:
                    content_win.addstr(i, 0, display_line)
                except curses.error:
                    pass  # Ignore errors from writing to window edges
        
        # Auto-scroll to bottom if new content is added
        if len(output_lines) > popup_h - 5:
            scroll_pos = max(0, len(output_lines) - (popup_h - 5))
        
        content_win.refresh()
        popup_win.refresh()
        
        # Handle input
        stdscr.timeout(100)  # Check for input every 100ms
        key = stdscr.getch()
        
        if key == 27:  # ESC key
            if command_finished:
                break
            else:
                # Ask for confirmation to terminate
                confirm_win = curses.newwin(5, 40, popup_y + popup_h//2, popup_x + popup_w//2 - 20)
                confirm_win.box()
                confirm_win.addstr(1, 2, "Command still running!")
                confirm_win.addstr(2, 2, "Press ESC again to terminate,")
                confirm_win.addstr(3, 2, "or any other key to continue")
                confirm_win.refresh()
                
                confirm_key = stdscr.getch()
                if confirm_key == 27:  # ESC again
                    if process and process.poll() is None:
                        process.terminate()
                        output_lines.append("\n=== Command terminated by user ===")
                    break
                
                del confirm_win
        elif key == curses.KEY_UP:
            scroll_pos = max(0, scroll_pos - 1)
        elif key == curses.KEY_DOWN:
            scroll_pos = min(len(output_lines) - 1, scroll_pos + 1)
        elif key == curses.KEY_PPAGE:  # Page Up
            scroll_pos = max(0, scroll_pos - (popup_h - 5))
        elif key == curses.KEY_NPAGE:  # Page Down
            scroll_pos = min(len(output_lines) - 1, scroll_pos + (popup_h - 5))
        
        # If command is finished and we haven't shown the completion message yet
        if command_finished and thread.is_alive():
            thread.join(timeout=0.1)
    
    # Clean up
    del content_win
    del popup_win
    stdscr.clear()
    stdscr.refresh()

def display_output_window(stdscr, message):
    """Display static output in a popup window."""
    h, w = stdscr.getmaxyx()
    # Calculate position for the pop-up window
    popup_h = min(10, h - 4) # Max 10 lines, or screen height - 4
    popup_w = min(60, w - 4) # Max 60 chars, or screen width - 4
    popup_y = (h - popup_h) // 2
    popup_x = (w - popup_w) // 2

    popup_win = curses.newwin(popup_h, popup_w, popup_y, popup_x)
    popup_win.box()
    popup_win.addstr(1, 1, "Action Output:")
    popup_win.addstr(2, 1, "-" * (popup_w - 2))

    # Display message, wrapping if necessary
    message_lines = []
    for line in message.split('\n'):
        while len(line) > popup_w - 4:
            message_lines.append(line[:popup_w - 4])
            line = line[popup_w - 4:]
        message_lines.append(line)

    for i, line in enumerate(message_lines):
        if i + 3 < popup_h - 1: # Ensure message fits within window
            popup_win.addstr(i + 3, 1, line)
        else:
            popup_win.addstr(popup_h - 2, 1, "... (message truncated)")
            break

    popup_win.addstr(popup_h - 1, 1, "Press ESC to continue...")
    popup_win.refresh()

    while True:
        key = stdscr.getch()
        if key == 27: # ESC key
            break
    stdscr.clear() # Clear the screen after closing popup
    stdscr.refresh()

def go_back(stdscr):
    global current_menu_key, active_pane, main_selected_row, submenu_selected_row
    if menu_history:
        current_menu_key = menu_history.pop()
        active_pane = "main" # Always go back to main pane when returning to parent menu
        main_selected_row = 0 # Reset selection in main menu
        submenu_selected_row = 0 # Reset selection in submenu
    else:
        # If no history, it means we are at the main menu and trying to go back
        # This case should ideally be handled by exit_program or ignored.
        pass

def exit_program(stdscr):
    global running
    running = False

# Map action names to functions
ACTION_FUNCTIONS = {
    "example_initial_setup_1": example_initial_setup_1,
    "example_initial_setup_2": example_initial_setup_2,
    "example_app_setup_1": example_app_setup_1,
    "example_app_setup_2": example_app_setup_2,
    "install_gnome": install_gnome,
    "go_back": go_back,
    "exit_program": exit_program,
}

# Commands that should use live output
LIVE_COMMANDS = {
    "install_gnome": ['sudo', 'pacman', '-S', 'gnome', 'gnome-shell', 'gdm'],
}

def draw_menu_pane(stdscr, menu_data, selected_row, start_y, start_x, is_active_pane):
    """Draws a single menu pane."""
    h, w = stdscr.getmaxyx()
    
    # Draw title
    title = menu_data["name"]
    stdscr.addstr(start_y, start_x, title, curses.A_BOLD)
    stdscr.addstr(start_y + 1, start_x, "=" * len(title))

    menu_items_list = list(menu_data["items"].values())
    menu_keys_list = list(menu_data["items"].keys())

    for idx, item in enumerate(menu_items_list):
        y = start_y + 3 + idx
        x = start_x
        if y < h: # Ensure we don't write past screen height
            display_text = f"{menu_keys_list[idx]}) {item['name']}"
            if idx == selected_row and is_active_pane:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(y, x, display_text)
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, display_text)

def main(stdscr):
    global current_menu_key, main_selected_row, submenu_selected_row, active_pane, running

    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(True) # Make getch non-blocking
    stdscr.timeout(100) # Refresh every 100ms to allow for dynamic updates

    running = True
    while running:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Calculate pane widths
        main_pane_width = w // 2
        submenu_pane_width = w - main_pane_width

        # Get current main menu items
        main_menu_data = MENUS["main"]
        main_menu_items_list = list(main_menu_data["items"].values())

        # Draw Main Menu (Left Pane)
        draw_menu_pane(stdscr, main_menu_data, main_selected_row, 0, 0, active_pane == "main")

        # Determine and draw Submenu (Right Pane)
        selected_main_item = main_menu_items_list[main_selected_row]
        if selected_main_item["type"] == "menu":
            submenu_key = selected_main_item["submenu"]
            submenu_data = MENUS[submenu_key]
            draw_menu_pane(stdscr, submenu_data, submenu_selected_row, 0, main_pane_width, active_pane == "submenu")
        
        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP:
            if active_pane == "main":
                main_selected_row = (main_selected_row - 1) % len(main_menu_items_list)
            elif active_pane == "submenu":
                selected_main_item = main_menu_items_list[main_selected_row]
                if selected_main_item["type"] == "menu":
                    submenu_key = selected_main_item["submenu"]
                    submenu_data = MENUS[submenu_key]
                    submenu_items_list = list(submenu_data["items"].values())
                    submenu_selected_row = (submenu_selected_row - 1) % len(submenu_items_list)
        elif key == curses.KEY_DOWN:
            if active_pane == "main":
                main_selected_row = (main_selected_row + 1) % len(main_menu_items_list)
            elif active_pane == "submenu":
                selected_main_item = main_menu_items_list[main_selected_row]
                if selected_main_item["type"] == "menu":
                    submenu_key = selected_main_item["submenu"]
                    submenu_data = MENUS[submenu_key]
                    submenu_items_list = list(submenu_data["items"].values())
                    submenu_selected_row = (submenu_selected_row + 1) % len(submenu_items_list)
        elif key == curses.KEY_RIGHT:
            if active_pane == "main":
                selected_main_item = main_menu_items_list[main_selected_row]
                if selected_main_item["type"] == "menu":
                    active_pane = "submenu"
                    submenu_selected_row = 0 # Reset submenu selection when entering
        elif key == curses.KEY_LEFT:
            if active_pane == "submenu":
                active_pane = "main"
        elif key == curses.KEY_ENTER or key in [10, 13]: # Enter key
            if active_pane == "main":
                selected_item = main_menu_items_list[main_selected_row]
                if selected_item["type"] == "menu":
                    # This case is handled by KEY_RIGHT, but also allow Enter
                    active_pane = "submenu"
                    submenu_selected_row = 0
                elif selected_item["type"] == "action":
                    action_func = ACTION_FUNCTIONS.get(selected_item["action"])
                    if action_func:
                        if selected_item["action"] == "go_back":
                            go_back(stdscr)
                        elif selected_item["action"] == "exit_program":
                            exit_program(stdscr)
                        else:
                            # Check if this action should use live output
                            if selected_item["action"] in LIVE_COMMANDS:
                                execute_command_with_live_output(
                                    stdscr, 
                                    LIVE_COMMANDS[selected_item["action"]],
                                    f"Executing: {selected_item['name']}"
                                )
                            else:
                                output_message = action_func()
                                if output_message:
                                    display_output_window(stdscr, output_message)
            elif active_pane == "submenu":
                selected_main_item = main_menu_items_list[main_selected_row]
                if selected_main_item["type"] == "menu":
                    submenu_key = selected_main_item["submenu"]
                    submenu_data = MENUS[submenu_key]
                    submenu_items_list = list(submenu_data["items"].values())
                    selected_submenu_item = submenu_items_list[submenu_selected_row]

                    if selected_submenu_item["type"] == "action":
                        action_func = ACTION_FUNCTIONS.get(selected_submenu_item["action"])
                        if action_func:
                            if selected_submenu_item["action"] == "go_back":
                                go_back(stdscr)
                            elif selected_submenu_item["action"] == "exit_program":
                                exit_program(stdscr)
                            else:
                                # Check if this action should use live output
                                if selected_submenu_item["action"] in LIVE_COMMANDS:
                                    execute_command_with_live_output(
                                        stdscr, 
                                        LIVE_COMMANDS[selected_submenu_item["action"]],
                                        f"Executing: {selected_submenu_item['name']}"
                                    )
                                else:
                                    output_message = action_func()
                                    if output_message:
                                        display_output_window(stdscr, output_message)
                                # After action, return to submenu view
                                active_pane = "submenu"
                                submenu_selected_row = 0 # Reset submenu selection
        elif key == ord('q') or key == ord('0'):
            if active_pane == "submenu":
                go_back(stdscr)
            elif active_pane == "main":
                exit_program(stdscr)

if __name__ == "__main__":
    curses.wrapper(main)