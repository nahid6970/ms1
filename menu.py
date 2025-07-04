import curses
import os
import subprocess

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
    }
}

# Global state variables
current_menu_key = "main"
main_selected_row = 0
submenu_selected_row = 0
active_pane = "main" # "main" or "submenu"
menu_history = [] # Stack to keep track of menu navigation

# --- Action Functions ---
def show_message(stdscr, message):
    stdscr.clear()
    stdscr.addstr(0, 0, message)
    stdscr.addstr(2, 0, "Press any key to continue...")
    stdscr.refresh()
    stdscr.getch()

def example_initial_setup_1(stdscr):
    show_message(stdscr, "Executing Example Initial Setup 1...")

def example_initial_setup_2(stdscr):
    show_message(stdscr, "Executing Example Initial Setup 2...")

def example_app_setup_1(stdscr):
    show_message(stdscr, "Executing Example App Setup 1...")

def example_app_setup_2(stdscr):
    show_message(stdscr, "Executing Example App Setup 2...")

def show_github_info(stdscr):
    stdscr.clear()
    content = MENUS["github_info"]["content"]
    # Display github info on the right side, where the submenu would be
    h, w = stdscr.getmaxyx()
    main_pane_width = w // 2
    for i, line in enumerate(content):
        stdscr.addstr(i, main_pane_width, line)
    stdscr.refresh()
    stdscr.getch()

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
    "show_github_info": show_github_info,
    "go_back": go_back,
    "exit_program": exit_program,
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
        # Special handling for github_info to display its content directly on the right pane
        elif selected_main_item["type"] == "action" and selected_main_item["action"] == "show_github_info":
            github_info_data = MENUS["github_info"]
            stdscr.addstr(0, main_pane_width, github_info_data["name"], curses.A_BOLD)
            stdscr.addstr(1, main_pane_width, "=" * len(github_info_data["name"]))
            for i, line in enumerate(github_info_data["content"]):
                stdscr.addstr(i + 3, main_pane_width, line)

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
                        action_func(stdscr)
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
                                action_func(stdscr)
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