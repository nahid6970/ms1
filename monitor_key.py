import tkinter as tk
from pynput import keyboard
import threading
import time

class FloatingKeyDisplay:
    def __init__(self):
        # Create the main window
        self.root = tk.Tk()
        self.root.title("")
        
        # Remove window decorations (no title bar, borders, etc.)
        self.root.overrideredirect(True)
        
        # Position window at top-right corner, close to screen edge
        self.root.geometry("+{}+{}".format(
            self.root.winfo_screenwidth() - 200, 10
        ))
        
        # Make window stay on top and semi-transparent
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.8)
        
        # Make window background transparent
        self.root.configure(bg='black')
        
        # Create label to display key presses - just text floating
        self.key_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="black",
            justify="right",
            anchor="e",
            padx=15,
            pady=8
        )
        self.key_label.pack()
        
        # Track modifier states
        self.modifiers = {
            'ctrl': False,
            'alt': False,
            'shift': False,
            'cmd': False
        }
        
        # Store current pressed keys
        self.current_keys = set()
        
        # Hide window initially
        self.root.withdraw()
        
        # Auto-hide timer
        self.hide_timer = None
        
        # Start keyboard listener in separate thread
        self.listener_thread = threading.Thread(target=self.start_listener, daemon=True)
        self.listener_thread.start()
        
        # Right-click to exit
        self.key_label.bind("<Button-3>", self.on_right_click)
        
    def start_listener(self):
        """Start the keyboard listener"""
        with keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        ) as listener:
            listener.join()
    
    def on_press(self, key):
        """Handle key press events"""
        key_name = self.get_key_name(key)
        
        # Update modifier states
        if key_name.lower() in ['ctrl', 'control']:
            self.modifiers['ctrl'] = True
        elif key_name.lower() == 'alt':
            self.modifiers['alt'] = True
        elif key_name.lower() == 'shift':
            self.modifiers['shift'] = True
        elif key_name.lower() in ['cmd', 'command']:
            self.modifiers['cmd'] = True
        
        # Add key to current pressed keys
        self.current_keys.add(key_name)
        
        # Update display
        self.update_display()
    
    def on_release(self, key):
        """Handle key release events"""
        key_name = self.get_key_name(key)
        
        # Update modifier states
        if key_name.lower() in ['ctrl', 'control']:
            self.modifiers['ctrl'] = False
        elif key_name.lower() == 'alt':
            self.modifiers['alt'] = False
        elif key_name.lower() == 'shift':
            self.modifiers['shift'] = False
        elif key_name.lower() in ['cmd', 'command']:
            self.modifiers['cmd'] = False
        
        # Remove key from current pressed keys
        self.current_keys.discard(key_name)
        
        # Update display
        self.update_display()
    
    def get_key_name(self, key):
        """Convert key object to readable string"""
        try:
            if hasattr(key, 'char') and key.char is not None:
                return key.char.upper()
            else:
                # Special keys
                key_str = str(key).replace('Key.', '')
                
                # Handle common special keys
                key_mappings = {
                    'space': 'SPACE',
                    'enter': 'ENTER',
                    'tab': 'TAB',
                    'backspace': 'BACKSPACE',
                    'delete': 'DELETE',
                    'esc': 'ESC',
                    'up': '↑',
                    'down': '↓',
                    'left': '←',
                    'right': '→',
                    'ctrl_l': 'CTRL',
                    'ctrl_r': 'CTRL',
                    'alt_l': 'ALT',
                    'alt_r': 'ALT',
                    'shift_l': 'SHIFT',
                    'shift_r': 'SHIFT',
                    'cmd': 'CMD',
                    'page_up': 'PGUP',
                    'page_down': 'PGDN',
                    'home': 'HOME',
                    'end': 'END',
                    'insert': 'INS',
                    'f1': 'F1', 'f2': 'F2', 'f3': 'F3', 'f4': 'F4',
                    'f5': 'F5', 'f6': 'F6', 'f7': 'F7', 'f8': 'F8',
                    'f9': 'F9', 'f10': 'F10', 'f11': 'F11', 'f12': 'F12'
                }
                
                return key_mappings.get(key_str.lower(), key_str.upper())
        except:
            return str(key)
    
    def update_display(self):
        """Update the display with current key combination"""
        if not self.current_keys:
            # Hide window when no keys pressed
            self.root.after(0, self.hide_window)
        else:
            # Build modifier string
            modifiers_text = []
            if self.modifiers['ctrl']:
                modifiers_text.append('CTRL')
            if self.modifiers['alt']:
                modifiers_text.append('ALT')
            if self.modifiers['shift']:
                modifiers_text.append('SHIFT')
            if self.modifiers['cmd']:
                modifiers_text.append('CMD')
            
            # Get non-modifier keys
            other_keys = []
            for key in self.current_keys:
                if key.upper() not in ['CTRL', 'ALT', 'SHIFT', 'CMD', 'CONTROL', 'COMMAND']:
                    other_keys.append(key)
            
            # Combine modifiers and other keys
            all_keys = modifiers_text + other_keys
            display_text = ' + '.join(all_keys)
            
            # Show window and update text
            self.root.after(0, lambda: self.show_window(display_text))
    
    def show_window(self, text):
        """Show the floating text window"""
        self.key_label.config(text=text)
        
        # Update window size and position based on text width
        self.root.update_idletasks()  # Update geometry calculations
        text_width = self.key_label.winfo_reqwidth()
        
        # Position close to right edge with minimal gap
        x_pos = self.root.winfo_screenwidth() - text_width - 10
        self.root.geometry(f"+{x_pos}+10")
        
        self.root.deiconify()  # Show window
        
        # Cancel any existing hide timer
        if self.hide_timer:
            self.root.after_cancel(self.hide_timer)
    
    def hide_window(self):
        """Hide the floating window after a delay"""
        if self.hide_timer:
            self.root.after_cancel(self.hide_timer)
        
        # Hide after 500ms of no key presses
        self.hide_timer = self.root.after(500, lambda: self.root.withdraw())
    
    def on_right_click(self, event):
        """Handle right-click to exit"""
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Start the application"""
        print("🎹 Floating Key Display started!")
        print("📍 Key presses will appear as floating text on screen")
        print("🖱️  Right-click the text to exit")
        print("❌ Close this terminal to stop the program")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nExiting...")

if __name__ == "__main__":
    # Check if required modules are available
    try:
        import pynput
    except ImportError:
        print("Error: pynput module is required.")
        print("Install it using: pip install pynput")
        exit(1)
    
    # Create and run the monitor
    display = FloatingKeyDisplay()
    display.run()