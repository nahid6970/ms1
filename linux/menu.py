import curses
import os
import subprocess
import threading
import time
import pty
import select
import termios
import tty
import signal
import sys

# Define the menu structure
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
            "1": {"name": "Update System", "type": "action", "action": "update_system"},
            "2": {"name": "Install Base Tools", "type": "action", "action": "install_base_tools"},
            "0": {"name": "Back to Main Menu", "type": "action", "action": "go_back"},
        }
    },
    "application_setup": {
        "name": "Application Setup Menu",
        "items": {
            "1": {"name": "Install Firefox", "type": "action", "action": "install_firefox"},
            "2": {"name": "Install VS Code", "type": "action", "action": "install_vscode"},
            "0": {"name": "Back to Main Menu", "type": "action", "action": "go_back"},
        }
    },
    "desktop_environments": {
        "name": "Desktop Environments",
        "items": {
            "1": {"name": "Install Gnome", "type": "action", "action": "install_gnome"},
            "2": {"name": "Install KDE", "type": "action", "action": "install_kde"},
            "3": {"name": "Install XFCE", "type": "action", "action": "install_xfce"},
            "0": {"name": "Back to Main Menu", "type": "action", "action": "go_back"},
        }
    }
}

# Commands that require live output (interactive commands)
LIVE_COMMANDS = {
    "install_gnome": ["sudo", "pacman", "-S", "--needed", "gnome", "gnome-shell", "gdm"],
    "install_kde": ["sudo", "pacman", "-S", "--needed", "plasma", "kde-applications"],
    "install_xfce": ["sudo", "pacman", "-S", "--needed", "xfce4", "xfce4-goodies"],
    "update_system": ["sudo", "pacman", "-Syu"],
    "install_firefox": ["sudo", "pacman", "-S", "--needed", "firefox"],
    "install_vscode": ["sudo", "pacman", "-S", "--needed", "code"],
    "install_base_tools": ["sudo", "pacman", "-S", "--needed", "git", "vim", "htop", "wget", "curl"],
}

# Global state variables
current_menu_key = "main"
main_selected_row = 0
submenu_selected_row = 0
active_pane = "main"
menu_history = []
running = True

class InteractiveTerminal:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.output_lines = []
        self.scroll_pos = 0
        self.process = None
        self.master_fd = None
        self.command_finished = False
        self.exit_code = None
        
    def execute_command(self, command, title="Command Output"):
        """Execute a command with full interactive support including password prompts."""
        h, w = self.stdscr.getmaxyx()
        
        # Create popup window
        popup_h = min(24, h - 2)
        popup_w = min(100, w - 2)
        popup_y = (h - popup_h) // 2
        popup_x = (w - popup_w) // 2
        
        self.popup_win = curses.newwin(popup_h, popup_w, popup_y, popup_x)
        self.popup_win.box()
        self.popup_win.addstr(1, 2, title[:popup_w-4])
        self.popup_win.addstr(2, 2, "=" * min(len(title), popup_w-4))
        
        # Create content window
        self.content_win = curses.newwin(popup_h - 6, popup_w - 4, popup_y + 3, popup_x + 2)
        self.content_win.scrollok(True)
        self.content_win.idlok(True)
        
        # Create input area
        self.input_win = curses.newwin(2, popup_w - 4, popup_y + popup_h - 4, popup_x + 2)
        self.input_win.box()
        
        # Status line
        self.status_line = popup_y + popup_h - 2
        
        try:
            # Use pty for full interactive support
            self.master_fd, slave_fd = pty.openpty()
            
            # Start process with pty
            self.process = subprocess.Popen(
                command,
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                preexec_fn=os.setsid,
                close_fds=True
            )
            
            os.close(slave_fd)  # Close slave fd in parent process
            
            # Make master fd non-blocking
            import fcntl
            flags = fcntl.fcntl(self.master_fd, fcntl.F_GETFL)
            fcntl.fcntl(self.master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            
            self._run_interactive_loop()
            
        except Exception as e:
            self.output_lines.append(f"Error starting command: {str(e)}")
            self._display_final_output()
        finally:
            self._cleanup()
    
    def _run_interactive_loop(self):
        """Main loop for handling interactive command execution."""
        input_buffer = ""
        password_mode = False
        
        # Set up curses for non-blocking input
        self.stdscr.nodelay(True)
        self.stdscr.timeout(50)  # 50ms timeout
        
        while True:
            # Check if process is still running
            if self.process.poll() is not None:
                self.command_finished = True
                self.exit_code = self.process.returncode
                break
            
            # Read from command output
            try:
                if self.master_fd:
                    ready, _, _ = select.select([self.master_fd], [], [], 0.01)
                    if ready:
                        data = os.read(self.master_fd, 1024).decode('utf-8', errors='replace')
                        if data:
                            self._process_output(data)
                            # Check for password prompt
                            last_line = self.output_lines[-1] if self.output_lines else ""
                            if any(prompt in last_line.lower() for prompt in ['password', 'passwort', '[sudo]']):
                                password_mode = True
            except (OSError, IOError):
                pass
            
            # Handle user input
            try:
                key = self.stdscr.getch()
                if key != -1:  # Key was pressed
                    if key == 27:  # ESC key
                        if self._handle_escape():
                            break
                    elif key == curses.KEY_UP:
                        self._scroll_up()
                    elif key == curses.KEY_DOWN:
                        self._scroll_down()
                    elif key == curses.KEY_PPAGE:
                        self._page_up()
                    elif key == curses.KEY_NPAGE:
                        self._page_down()
                    elif key in [curses.KEY_ENTER, 10, 13]:  # Enter key
                        self._send_input(input_buffer + '\n')
                        input_buffer = ""
                        password_mode = False
                    elif key == curses.KEY_BACKSPACE or key == 127:
                        if input_buffer:
                            input_buffer = input_buffer[:-1]
                    elif key == 3:  # Ctrl+C
                        self._send_signal(signal.SIGINT)
                    elif 32 <= key <= 126:  # Printable characters
                        input_buffer += chr(key)
            except curses.error:
                pass
            
            # Update display
            self._update_display(input_buffer, password_mode)
        
        # Show final result
        self._display_final_output()
    
    def _process_output(self, data):
        """Process output from the command."""
        lines = data.split('\n')
        
        if not self.output_lines:
            self.output_lines.append("")
        
        # Add first line to last existing line
        self.output_lines[-1] += lines[0]
        
        # Add remaining lines
        for line in lines[1:]:
            self.output_lines.append(line)
        
        # Auto-scroll to bottom
        content_height = self.content_win.getmaxyx()[0]
        if len(self.output_lines) > content_height:
            self.scroll_pos = len(self.output_lines) - content_height
    
    def _send_input(self, text):
        """Send input to the command."""
        if self.master_fd:
            try:
                os.write(self.master_fd, text.encode('utf-8'))
            except (OSError, IOError):
                pass
    
    def _send_signal(self, sig):
        """Send signal to the process."""
        if self.process:
            try:
                os.killpg(os.getpgid(self.process.pid), sig)
            except (OSError, ProcessLookupError):
                pass
    
    def _update_display(self, input_buffer="", password_mode=False):
        """Update the display with current output and input."""
        # Clear windows
        self.content_win.clear()
        self.input_win.clear()
        
        # Display output
        content_height = self.content_win.getmaxyx()[0]
        content_width = self.content_win.getmaxyx()[1]
        
        start_line = max(0, self.scroll_pos)
        end_line = min(len(self.output_lines), start_line + content_height)
        
        for i, line in enumerate(self.output_lines[start_line:end_line]):
            try:
                # Truncate line if too long
                display_line = line[:content_width] if len(line) > content_width else line
                self.content_win.addstr(i, 0, display_line)
            except curses.error:
                pass
        
        # Display input area
        self.input_win.box()
        if password_mode:
            self.input_win.addstr(0, 2, " Password Input ")
            display_input = "*" * len(input_buffer)
        else:
            self.input_win.addstr(0, 2, " Input ")
            display_input = input_buffer
        
        try:
            self.input_win.addstr(1, 1, f"> {display_input}")
        except curses.error:
            pass
        
        # Display status
        status_text = "ESC: Exit | ↑↓: Scroll | Enter: Send | Ctrl+C: Interrupt"
        if self.command_finished:
            status_text = f"Command finished (exit code: {self.exit_code}) | ESC: Close"
        
        try:
            self.stdscr.addstr(self.status_line, 2, status_text[:self.popup_win.getmaxyx()[1]-4])
        except curses.error:
            pass
        
        # Refresh windows
        self.content_win.refresh()
        self.input_win.refresh()
        self.popup_win.refresh()
        self.stdscr.refresh()
    
    def _scroll_up(self):
        self.scroll_pos = max(0, self.scroll_pos - 1)
    
    def _scroll_down(self):
        content_height = self.content_win.getmaxyx()[0]
        max_scroll = max(0, len(self.output_lines) - content_height)
        self.scroll_pos = min(max_scroll, self.scroll_pos + 1)
    
    def _page_up(self):
        content_height = self.content_win.getmaxyx()[0]
        self.scroll_pos = max(0, self.scroll_pos - content_height)
    
    def _page_down(self):
        content_height = self.content_win.getmaxyx()[0]
        max_scroll = max(0, len(self.output_lines) - content_height)
        self.scroll_pos = min(max_scroll, self.scroll_pos + content_height)
    
    def _handle_escape(self):
        """Handle ESC key press."""
        if self.command_finished:
            return True
        
        # Show confirmation dialog
        h, w = self.stdscr.getmaxyx()
        dialog_h, dialog_w = 7, 50
        dialog_y = (h - dialog_h) // 2
        dialog_x = (w - dialog_w) // 2
        
        dialog_win = curses.newwin(dialog_h, dialog_w, dialog_y, dialog_x)
        dialog_win.box()
        dialog_win.addstr(1, 2, "Command is still running!")
        dialog_win.addstr(2, 2, "")
        dialog_win.addstr(3, 2, "ESC again: Terminate command")
        dialog_win.addstr(4, 2, "Any other key: Continue")
        dialog_win.refresh()
        
        key = self.stdscr.getch()
        del dialog_win
        
        if key == 27:  # ESC again
            self._send_signal(signal.SIGTERM)
            time.sleep(0.5)
            if self.process.poll() is None:
                self._send_signal(signal.SIGKILL)
            return True
        
        return False
    
    def _display_final_output(self):
        """Display final command result."""
        if self.command_finished:
            if self.exit_code == 0:
                self.output_lines.append("\n=== Command completed successfully ===")
            else:
                self.output_lines.append(f"\n=== Command failed with exit code {self.exit_code} ===")
        else:
            self.output_lines.append("\n=== Command was terminated ===")
        
        # Wait for user to press ESC
        while True:
            self._update_display()
            key = self.stdscr.getch()
            if key == 27:  # ESC
                break
            elif key == curses.KEY_UP:
                self._scroll_up()
            elif key == curses.KEY_DOWN:
                self._scroll_down()
            elif key == curses.KEY_PPAGE:
                self._page_up()
            elif key == curses.KEY_NPAGE:
                self._page_down()
    
    def _cleanup(self):
        """Clean up resources."""
        if self.master_fd:
            try:
                os.close(self.master_fd)
            except OSError:
                pass
        
        if self.process:
            try:
                if self.process.poll() is None:
                    self.process.terminate()
                    self.process.wait(timeout=2)
            except:
                pass
        
        # Clear screen
        self.stdscr.clear()
        self.stdscr.refresh()

def display_simple_message(stdscr, message):
    """Display a simple message in a popup."""
    h, w = stdscr.getmaxyx()
    popup_h = min(10, h - 4)
    popup_w = min(60, w - 4)
    popup_y = (h - popup_h) // 2
    popup_x = (w - popup_w) // 2

    popup_win = curses.newwin(popup_h, popup_w, popup_y, popup_x)
    popup_win.box()
    popup_win.addstr(1, 1, "Message:")
    popup_win.addstr(2, 1, "-" * (popup_w - 2))

    # Display message
    message_lines = message.split('\n')
    for i, line in enumerate(message_lines):
        if i + 3 < popup_h - 1:
            popup_win.addstr(i + 3, 1, line[:popup_w-2])

    popup_win.addstr(popup_h - 1, 1, "Press ESC to continue...")
    popup_win.refresh()

    while True:
        key = stdscr.getch()
        if key == 27:  # ESC
            break
    
    stdscr.clear()
    stdscr.refresh()

def go_back():
    global current_menu_key, active_pane, main_selected_row, submenu_selected_row
    if menu_history:
        current_menu_key = menu_history.pop()
        active_pane = "main"
        main_selected_row = 0
        submenu_selected_row = 0

def exit_program():
    global running
    running = False

# Simple action functions
def simple_action(message):
    return message

# Action function mapping
ACTION_FUNCTIONS = {
    "go_back": go_back,
    "exit_program": exit_program,
}

def draw_menu_pane(stdscr, menu_data, selected_row, start_y, start_x, is_active_pane):
    """Draw a menu pane."""
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
        if y < h:
            display_text = f"{menu_keys_list[idx]}) {item['name']}"
            if idx == selected_row and is_active_pane:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(y, x, display_text)
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, display_text)

def main(stdscr):
    global current_menu_key, main_selected_row, submenu_selected_row, active_pane, running

    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    running = True
    while running:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Calculate pane widths
        main_pane_width = w // 2
        submenu_pane_width = w - main_pane_width

        # Get current main menu
        main_menu_data = MENUS["main"]
        main_menu_items_list = list(main_menu_data["items"].values())

        # Draw main menu
        draw_menu_pane(stdscr, main_menu_data, main_selected_row, 0, 0, active_pane == "main")

        # Draw submenu if applicable
        selected_main_item = main_menu_items_list[main_selected_row]
        if selected_main_item["type"] == "menu":
            submenu_key = selected_main_item["submenu"]
            submenu_data = MENUS[submenu_key]
            draw_menu_pane(stdscr, submenu_data, submenu_selected_row, 0, main_pane_width, active_pane == "submenu")

        stdscr.refresh()
        key = stdscr.getch()

        # Handle navigation
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
                    submenu_selected_row = 0
                    
        elif key == curses.KEY_LEFT:
            if active_pane == "submenu":
                active_pane = "main"
                
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if active_pane == "main":
                selected_item = main_menu_items_list[main_selected_row]
                if selected_item["type"] == "menu":
                    active_pane = "submenu"
                    submenu_selected_row = 0
                elif selected_item["type"] == "action":
                    if selected_item["action"] == "go_back":
                        go_back()
                    elif selected_item["action"] == "exit_program":
                        exit_program()
                        
            elif active_pane == "submenu":
                selected_main_item = main_menu_items_list[main_selected_row]
                if selected_main_item["type"] == "menu":
                    submenu_key = selected_main_item["submenu"]
                    submenu_data = MENUS[submenu_key]
                    submenu_items_list = list(submenu_data["items"].values())
                    selected_submenu_item = submenu_items_list[submenu_selected_row]

                    if selected_submenu_item["type"] == "action":
                        action_name = selected_submenu_item["action"]
                        
                        if action_name == "go_back":
                            go_back()
                        elif action_name == "exit_program":
                            exit_program()
                        elif action_name in LIVE_COMMANDS:
                            # Execute with interactive terminal
                            terminal = InteractiveTerminal(stdscr)
                            terminal.execute_command(
                                LIVE_COMMANDS[action_name],
                                f"Executing: {selected_submenu_item['name']}"
                            )
                        else:
                            # Simple action
                            display_simple_message(stdscr, f"Executed: {selected_submenu_item['name']}")
                            
        elif key == ord('q') or key == ord('0'):
            if active_pane == "submenu":
                go_back()
            elif active_pane == "main":
                exit_program()

if __name__ == "__main__":
    curses.wrapper(main)