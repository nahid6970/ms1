"""
Rclone GUI - Cyberpunk Edition with PyQt6
High-performance UI with HTML/CSS styling
"""

import sys
import threading
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTabWidget, QPushButton, QLabel, 
                             QLineEdit, QRadioButton, QButtonGroup, QScrollArea,
                             QGridLayout, QComboBox, QFrame)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QFont


class CommandSignals(QObject):
    """Signals for thread-safe command execution"""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)


class RcloneGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RCLONE // CYBERPUNK INTERFACE")
        self.setGeometry(100, 100, 1400, 900)
        
        # Apply cyberpunk stylesheet
        self.setStyleSheet(self.get_cyberpunk_style())
        
        # Initialize variables
        self.init_variables()
        
        # Create UI
        self.create_ui()
        
        # Center window
        self.center_window()
    
    def get_cyberpunk_style(self):
        """Return cyberpunk-themed stylesheet"""
        return """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0e27, stop:1 #16213e);
            }
            
            QTabWidget::pane {
                border: 2px solid #00ff41;
                background: rgba(10, 14, 39, 0.95);
                border-radius: 8px;
            }
            
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a2e, stop:1 #16213e);
                color: #00ff41;
                padding: 12px 25px;
                margin: 2px;
                border: 2px solid #00ff41;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                font-weight: bold;
                text-transform: uppercase;
            }
            
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00ff41, stop:1 #00cc33);
                color: #0a0e27;
                border-bottom: 2px solid #00ff41;
            }
            
            QTabBar::tab:hover:!selected {
                background: rgba(0, 255, 65, 0.2);
                color: #00ffff;
            }
            
            QLabel {
                color: #00ff41;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                font-weight: bold;
            }
            
            QLabel[class="header"] {
                color: #00ffff;
                font-size: 16px;
                padding: 10px;
                border-bottom: 2px solid #ff00ff;
                text-transform: uppercase;
                letter-spacing: 2px;
            }
            
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e, stop:1 #16213e);
                color: #00ff41;
                border: 2px solid #00ff41;
                border-radius: 6px;
                padding: 8px 15px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                font-weight: bold;
                text-transform: uppercase;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ff41, stop:1 #00cc33);
                color: #0a0e27;
                border: 2px solid #00ffff;
                box-shadow: 0 0 20px #00ff41;
            }
            
            QPushButton:pressed {
                background: #00cc33;
                border: 2px solid #ff00ff;
            }
            
            QPushButton[class="active"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ff41, stop:1 #00cc33);
                color: #0a0e27;
                border: 2px solid #00ffff;
            }
            
            QPushButton[class="inactive"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff0055, stop:1 #cc0044);
                color: #ffffff;
                border: 2px solid #ff0055;
            }
            
            QPushButton[class="execute"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff00ff, stop:1 #cc00cc);
                color: #ffffff;
                border: 3px solid #ff00ff;
                padding: 12px 30px;
                font-size: 14px;
            }
            
            QPushButton[class="execute"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff00ff, stop:1 #ff66ff);
                box-shadow: 0 0 30px #ff00ff;
            }
            
            QPushButton[class="quick"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff6600, stop:1 #ff3300);
                color: #ffffff;
                border: 2px solid #ff6600;
                padding: 15px;
                font-size: 13px;
                min-height: 50px;
            }
            
            QPushButton[class="quick"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff9933, stop:1 #ff6600);
                box-shadow: 0 0 25px #ff6600;
            }
            
            QRadioButton {
                color: #00ff41;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                font-weight: bold;
                spacing: 8px;
            }
            
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #00ff41;
                border-radius: 10px;
                background: #1a1a2e;
            }
            
            QRadioButton::indicator:checked {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    fx:0.5, fy:0.5, stop:0 #00ff41, stop:1 #00cc33);
                border: 2px solid #00ffff;
            }
            
            QRadioButton::indicator:hover {
                border: 2px solid #00ffff;
                background: rgba(0, 255, 65, 0.2);
            }
            
            QLineEdit, QComboBox {
                background: rgba(26, 26, 46, 0.8);
                color: #00ffff;
                border: 2px solid #00ff41;
                border-radius: 5px;
                padding: 8px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                font-weight: bold;
            }
            
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #ff00ff;
                background: rgba(26, 26, 46, 1);
                box-shadow: 0 0 15px rgba(255, 0, 255, 0.5);
            }
            
            QComboBox::drop-down {
                border: none;
                background: #00ff41;
                width: 30px;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 8px solid #0a0e27;
                margin-right: 8px;
            }
            
            QComboBox QAbstractItemView {
                background: #1a1a2e;
                color: #00ff41;
                border: 2px solid #00ff41;
                selection-background-color: #00ff41;
                selection-color: #0a0e27;
            }
            
            QScrollArea {
                border: none;
                background: transparent;
            }
            
            QScrollBar:vertical {
                background: #1a1a2e;
                width: 12px;
                border: 1px solid #00ff41;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ff41, stop:1 #00cc33);
                border-radius: 5px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #00ffff;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QFrame[class="section"] {
                background: rgba(22, 33, 62, 0.6);
                border: 2px solid #00ff41;
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }
        """
    
    def init_variables(self):
        """Initialize all variables"""
        self.command = "ls"
        self.storage = ""
        self.from_path = ""
        self.to_path = ""
        
        self.filter_vars = {
            "transfer": "4",
            "include": "*.jpg",
            "exclude": "*.jpg",
            "maxage": "1d",
            "minage": "1d",
            "maxsize": "100M",
            "minsize": "100M",
            "grep": ""
        }
        
        self.additional_options = [
            ("Fast List", "--fast-list", True),
            ("Readable", "--human-readable", True),
            ("Acknowledge Abuse", "--drive-acknowledge-abuse", True),
            ("Progress", "-P", True),
            ("Dry Run", "--dry-run", False),
            ("Web Gui", "--rc-web-gui", False),
            ("VFS Cache", "--vfs-cache-mode writes", False),
            ("Verbose ++", "-vv", False),
            ("Verbose +", "-v", False),
            ("Log Level", "--log-level ERROR", False),
            ("Stats Oneline", "--stats-one-line", False),
            ("Trashed Only", "--drive-trashed-only", False),
            ("Shared With Me", "--drive-shared-with-me", False),
            ("Skip Dangling", "--drive-skip-dangling-shortcuts", False),
            ("Skip Shortcuts", "--drive-skip-shortcuts", False),
            ("Date Tree", "-D", False),
            ("Modified Time", "-t", False),
        ]
        
        self.extra_items = {
            "transfer": {"text": "Transfers", "prefix": "--transfers", "state": False},
            "include": {"text": "Include", "prefix": "--include", "state": False},
            "exclude": {"text": "Exclude", "prefix": "--exclude", "state": False},
            "maxage": {"text": "Max Age", "prefix": "--max-age", "state": False},
            "minage": {"text": "Min Age", "prefix": "--min-age", "state": False},
            "maxsize": {"text": "Max Size", "prefix": "--max-size", "state": False},
            "minsize": {"text": "Min Size", "prefix": "--min-size", "state": False},
        }
        
        self.common_paths = {
            "Songs_Cloud": "gu:/song",
            "Software_Cloud": "gu:/software",
            "MX_Cloud": "gu:/mx",
            "Desktop_Local": "C:/Users/nahid/Desktop",
            "Desktop_Cloud": "o0/Desktop",
            "Pictures_Local": "C:/Users/nahid/Pictures",
            "Pictures_Cloud": "o0:/Pictures",
            "Download_Rclone_C": "C:/rclone_download/",
            "Download_Rclone_D": "D:/rclone_download/"
        }
        
        self.quick_commands = [
            {"name": "msBackups ↑", "command": "rclone sync C:\\Users\\nahid\\ms\\msBackups\\ o0:\\msBackups\\ -P --check-first --transfers=10 --track-renames --fast-list"},
            {"name": "Song ↑", "command": "rclone sync D:\\song\\ gu:\\song\\ -P --check-first --transfers=10 --track-renames --fast-list"},
            {"name": "Software ↑", "command": "rclone sync D:\\software\\ gu:\\software\\ -P --check-first --transfers=10 --track-renames --fast-list"},
            {"name": "Software ↓", "command": "rclone sync gu:\\software\\ D:\\software\\ -P --check-first --transfers=10 --track-renames --fast-list"},
            {"name": "Pictures ↑", "command": "rclone sync C:\\Users\\nahid\\Pictures o0:\\Pictures -P --check-first --transfers=10 --track-renames --fast-list"}
        ]
        
        self.flag_buttons = []
        self.filter_buttons = {}
    
    def create_ui(self):
        """Create the main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Create tab widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Create tabs
        self.create_general_tab()
        self.create_quick_commands_tab()
    
    def create_general_tab(self):
        """Create general commands tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)
        
        # Command section
        self.create_command_section(scroll_layout)
        
        # Storage section
        self.create_storage_section(scroll_layout)
        
        # Path section
        self.create_path_section(scroll_layout)
        
        # Flags section
        self.create_flags_section(scroll_layout)
        
        # Filter section
        self.create_filter_section(scroll_layout)
        
        # Grep section
        self.create_grep_section(scroll_layout)
        
        # Action buttons
        self.create_action_buttons(scroll_layout)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        self.tabs.addTab(tab, "// GENERAL COMMANDS")
    
    def create_command_section(self, layout):
        """Create command selection section"""
        frame = QFrame()
        frame.setProperty("class", "section")
        frame_layout = QVBoxLayout(frame)
        
        header = QLabel(">> COMMAND SELECTION")
        header.setProperty("class", "header")
        frame_layout.addWidget(header)
        
        cmd_layout = QHBoxLayout()
        self.command_group = QButtonGroup()
        
        commands = ["ls", "copy", "sync", "tree", "ncdu", "size", "mount", "rcd"]
        for i, cmd in enumerate(commands):
            radio = QRadioButton(cmd.upper())
            radio.setChecked(cmd == "ls")
            radio.toggled.connect(lambda checked, c=cmd: self.set_command(c) if checked else None)
            self.command_group.addButton(radio, i)
            cmd_layout.addWidget(radio)
        
        cmd_layout.addStretch()
        frame_layout.addLayout(cmd_layout)
        layout.addWidget(frame)
    
    def create_storage_section(self, layout):
        """Create storage selection section"""
        frame = QFrame()
        frame.setProperty("class", "section")
        frame_layout = QVBoxLayout(frame)
        
        header = QLabel(">> STORAGE SELECTION")
        header.setProperty("class", "header")
        frame_layout.addWidget(header)
        
        self.storage_group = QButtonGroup()
        
        storage_groups = [
            ["N/A", "C:/", "D:/"],
            ["cgu:/", "gu:/", "g00:/"],
            ["g01:/", "g02:/", "g03:/", "g04:/", "g05:/"],
            ["g06:/", "g07:/", "g08:/", "g09:/", "g10:/"],
            ["g11:/", "g12:/", "g13:/", "g14:/", "g15:/"],
            ["o0:/", "ouk:/"],
            ["m0:/", "m1:/"]
        ]
        
        btn_id = 0
        for group in storage_groups:
            group_layout = QHBoxLayout()
            for storage in group:
                value = "" if storage == "N/A" else storage
                radio = QRadioButton(storage)
                radio.setChecked(storage == "N/A")
                radio.toggled.connect(lambda checked, v=value: self.set_storage(v) if checked else None)
                self.storage_group.addButton(radio, btn_id)
                group_layout.addWidget(radio)
                btn_id += 1
            group_layout.addStretch()
            frame_layout.addLayout(group_layout)
        
        layout.addWidget(frame)
    
    def create_path_section(self, layout):
        """Create path selection section"""
        frame = QFrame()
        frame.setProperty("class", "section")
        frame_layout = QVBoxLayout(frame)
        
        header = QLabel(">> PATH CONFIGURATION")
        header.setProperty("class", "header")
        frame_layout.addWidget(header)
        
        # From path
        from_layout = QHBoxLayout()
        from_layout.addWidget(QLabel("FROM:"))
        self.from_combo = QComboBox()
        self.from_combo.addItems(list(self.common_paths.keys()))
        self.from_combo.setEditable(True)
        self.from_combo.currentTextChanged.connect(self.update_from_path)
        from_layout.addWidget(self.from_combo, 1)
        frame_layout.addLayout(from_layout)
        
        # To path
        to_layout = QHBoxLayout()
        to_layout.addWidget(QLabel("TO:"))
        self.to_combo = QComboBox()
        self.to_combo.addItems(list(self.common_paths.keys()))
        self.to_combo.setEditable(True)
        self.to_combo.currentTextChanged.connect(self.update_to_path)
        to_layout.addWidget(self.to_combo, 1)
        frame_layout.addLayout(to_layout)
        
        layout.addWidget(frame)
    
    def create_flags_section(self, layout):
        """Create flags section"""
        frame = QFrame()
        frame.setProperty("class", "section")
        frame_layout = QVBoxLayout(frame)
        
        header = QLabel(">> MAIN FLAGS")
        header.setProperty("class", "header")
        frame_layout.addWidget(header)
        
        grid = QGridLayout()
        grid.setSpacing(8)
        
        for idx, (display_text, _, is_selected) in enumerate(self.additional_options):
            row = idx // 5
            col = idx % 5
            
            btn = QPushButton(display_text)
            btn.setProperty("class", "active" if is_selected else "inactive")
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda checked, i=idx: self.toggle_flag(i))
            btn.setStyleSheet(btn.styleSheet())  # Force style update
            
            grid.addWidget(btn, row, col)
            self.flag_buttons.append(btn)
        
        frame_layout.addLayout(grid)
        layout.addWidget(frame)
    
    def create_filter_section(self, layout):
        """Create filter section"""
        frame = QFrame()
        frame.setProperty("class", "section")
        frame_layout = QVBoxLayout(frame)
        
        header = QLabel(">> FILTER OPTIONS")
        header.setProperty("class", "header")
        frame_layout.addWidget(header)
        
        for key, item in self.extra_items.items():
            row_layout = QHBoxLayout()
            
            btn = QPushButton(item["text"])
            btn.setProperty("class", "inactive")
            btn.setMinimumWidth(150)
            btn.setMinimumHeight(35)
            btn.clicked.connect(lambda checked, k=key: self.toggle_filter(k))
            btn.setStyleSheet(btn.styleSheet())
            
            entry = QLineEdit(self.filter_vars[key])
            entry.textChanged.connect(lambda text, k=key: self.update_filter_var(k, text))
            
            row_layout.addWidget(btn)
            row_layout.addWidget(entry, 1)
            
            frame_layout.addLayout(row_layout)
            self.filter_buttons[key] = btn
        
        layout.addWidget(frame)
    
    def create_grep_section(self, layout):
        """Create grep section"""
        frame = QFrame()
        frame.setProperty("class", "section")
        frame_layout = QHBoxLayout(frame)
        
        frame_layout.addWidget(QLabel("GREP FILTER:"))
        self.grep_entry = QLineEdit()
        self.grep_entry.setPlaceholderText("Enter search pattern...")
        self.grep_entry.textChanged.connect(lambda text: self.update_filter_var("grep", text))
        frame_layout.addWidget(self.grep_entry, 1)
        
        layout.addWidget(frame)
    
    def create_action_buttons(self, layout):
        """Create action buttons"""
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        execute_btn = QPushButton("⚡ EXECUTE COMMAND")
        execute_btn.setProperty("class", "execute")
        execute_btn.setMinimumHeight(50)
        execute_btn.clicked.connect(self.execute_command)
        
        clear_btn = QPushButton("🗑 CLEAR TERMINAL")
        clear_btn.setMinimumHeight(50)
        clear_btn.clicked.connect(self.clear_terminal)
        
        btn_layout.addWidget(execute_btn)
        btn_layout.addWidget(clear_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
    
    def create_quick_commands_tab(self):
        """Create quick commands tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)
        
        header = QLabel(">> QUICK ACCESS COMMANDS")
        header.setProperty("class", "header")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll_layout.addWidget(header)
        
        for cmd_info in self.quick_commands:
            btn = QPushButton(f"⚡ {cmd_info['name']}")
            btn.setProperty("class", "quick")
            btn.clicked.connect(lambda checked, c=cmd_info['command']: self.execute_quick_command(c))
            scroll_layout.addWidget(btn)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        self.tabs.addTab(tab, "// QUICK COMMANDS")
    
    def set_command(self, cmd):
        """Set command"""
        self.command = cmd
    
    def set_storage(self, storage):
        """Set storage"""
        self.storage = storage
    
    def update_from_path(self, text):
        """Update from path"""
        if text in self.common_paths:
            self.from_path = self.common_paths[text]
            self.from_combo.setEditText(self.from_path)
        else:
            self.from_path = text
    
    def update_to_path(self, text):
        """Update to path"""
        if text in self.common_paths:
            self.to_path = self.common_paths[text]
            self.to_combo.setEditText(self.to_path)
        else:
            self.to_path = text
    
    def update_filter_var(self, key, value):
        """Update filter variable"""
        self.filter_vars[key] = value
    
    def toggle_flag(self, idx):
        """Toggle flag state"""
        display_text, actual_text, is_selected = self.additional_options[idx]
        new_state = not is_selected
        self.additional_options[idx] = (display_text, actual_text, new_state)
        
        btn = self.flag_buttons[idx]
        btn.setProperty("class", "active" if new_state else "inactive")
        btn.setStyleSheet(btn.styleSheet())
    
    def toggle_filter(self, key):
        """Toggle filter state"""
        item = self.extra_items[key]
        item["state"] = not item["state"]
        
        btn = self.filter_buttons[key]
        btn.setProperty("class", "active" if item["state"] else "inactive")
        btn.setStyleSheet(btn.styleSheet())
    
    def execute_command(self):
        """Execute rclone command"""
        command = ["rclone", self.command, self.storage, self.from_path, self.to_path]
        
        if self.command == "mount":
            mount_dir = f"c:/{self.storage.strip(':/')}/"
            command.append(mount_dir)
        
        for display_text, actual_text, is_selected in self.additional_options:
            if is_selected:
                command.append(actual_text)
        
        for key, item in self.extra_items.items():
            if item["state"]:
                command.append(f"{item['prefix']}={self.filter_vars[key]}")
        
        grep_text = self.filter_vars["grep"].strip()
        if grep_text:
            command.append(f"| grep -i {grep_text}")
        
        final_command = " ".join(command)
        print(f"\n{'='*60}")
        print(f"EXECUTING: {final_command}")
        print(f"{'='*60}\n")
        
        thread = threading.Thread(target=self._run_command, args=(final_command,))
        thread.daemon = True
        thread.start()
    
    def execute_quick_command(self, command):
        """Execute quick command"""
        print(f"\n{'='*60}")
        print(f"EXECUTING QUICK COMMAND: {command}")
        print(f"{'='*60}\n")
        
        thread = threading.Thread(target=self._run_command, args=(command,))
        thread.daemon = True
        thread.start()
    
    def _run_command(self, command):
        """Run command in subprocess"""
        try:
            process = subprocess.Popen(command, shell=True)
            process.wait()
            print("\n\033[92m✓ TASK COMPLETED\033[0m\n")
        except Exception as e:
            print(f"\n\033[91m✗ ERROR: {e}\033[0m\n")
    
    def clear_terminal(self):
        """Clear terminal"""
        subprocess.run("cls", shell=True)
    
    def center_window(self):
        """Center window on screen"""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)


def main():
    app = QApplication(sys.argv)
    
    # Set application-wide font
    font = QFont("Consolas", 10)
    app.setFont(font)
    
    window = RcloneGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
