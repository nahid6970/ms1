import sys
import os
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTextEdit, QGroupBox, QFormLayout, QRadioButton,
                             QButtonGroup, QCheckBox, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QClipboard

# CYBERPUNK THEME PALETTE
CP_BG = "#050505"           # Main Window Background
CP_PANEL = "#111111"        # Panel/Input Background
CP_YELLOW = "#FCEE0A"       # Accent: Yellow
CP_CYAN = "#00F0FF"         # Accent: Cyan
CP_RED = "#FF003C"          # Accent: Red
CP_GREEN = "#00ff21"        # Accent: Green
CP_ORANGE = "#ff934b"       # Accent: Orange
CP_DIM = "#3a3a3a"          # Dimmed/Borders/Inactive
CP_TEXT = "#E0E0E0"         # Primary Text
CP_SUBTEXT = "#808080"      # Secondary Text

class PathConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PATH_CONVERTER // CYBER_QT")
        self.setGeometry(100, 100, 900, 700)
        
        # Apply cyberpunk theme
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ 
                color: {CP_TEXT}; 
                font-family: 'Consolas'; 
                font-size: 10pt; 
                background-color: {CP_BG};
            }}
            
            QLineEdit, QTextEdit {{
                background-color: {CP_PANEL}; 
                color: {CP_CYAN}; 
                border: 1px solid {CP_DIM}; 
                padding: 6px;
                selection-background-color: {CP_CYAN}; 
                selection-color: {CP_BG};
            }}
            QLineEdit:focus, QTextEdit:focus {{ 
                border: 1px solid {CP_CYAN}; 
            }}
            
            QPushButton {{
                background-color: {CP_DIM}; 
                border: 1px solid {CP_DIM}; 
                color: white; 
                padding: 8px 16px; 
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #2a2a2a; 
                border: 1px solid {CP_YELLOW}; 
                color: {CP_YELLOW};
            }}
            QPushButton:pressed {{
                background-color: {CP_YELLOW};
                color: {CP_BG};
            }}
            
            QPushButton#AccentButton {{
                background-color: {CP_PANEL}; 
                border: 2px solid {CP_GREEN}; 
                color: {CP_GREEN}; 
                padding: 10px 20px; 
                font-size: 11pt;
                font-weight: bold;
            }}
            QPushButton#AccentButton:hover {{
                background-color: {CP_GREEN}; 
                color: {CP_BG};
            }}
            
            QPushButton#CopyButton {{
                background-color: {CP_PANEL}; 
                border: 1px solid {CP_ORANGE}; 
                color: {CP_ORANGE}; 
                padding: 6px 12px; 
                font-weight: bold;
            }}
            QPushButton#CopyButton:hover {{
                background-color: {CP_ORANGE}; 
                color: {CP_BG};
            }}
            
            QGroupBox {{
                border: 1px solid {CP_DIM}; 
                margin-top: 12px; 
                padding-top: 15px; 
                font-weight: bold; 
                color: {CP_YELLOW};
            }}
            QGroupBox::title {{ 
                subcontrol-origin: margin; 
                subcontrol-position: top left; 
                padding: 0 8px; 
            }}
            
            QRadioButton {{
                color: {CP_TEXT};
                spacing: 8px;
            }}
            QRadioButton::indicator {{
                width: 14px;
                height: 14px;
                border: 1px solid {CP_DIM};
                background: {CP_PANEL};
                border-radius: 7px;
            }}
            QRadioButton::indicator:checked {{
                background: {CP_CYAN};
                border-color: {CP_CYAN};
            }}
            
            QCheckBox {{
                color: {CP_TEXT};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
                border: 1px solid {CP_DIM};
                background: {CP_PANEL};
            }}
            QCheckBox::indicator:checked {{
                background: {CP_YELLOW};
                border-color: {CP_YELLOW};
            }}
            
            QLabel#HeaderLabel {{
                color: {CP_GREEN};
                font-size: 18pt;
                font-weight: bold;
            }}
            QLabel#SectionLabel {{
                color: {CP_CYAN};
                font-weight: bold;
            }}
            QLabel#StatusLabel {{
                color: {CP_ORANGE};
                font-size: 9pt;
            }}
            
            QFrame#Separator {{
                background-color: {CP_DIM};
                max-height: 1px;
            }}
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        
        # Header
        header = QLabel("PATH_CONVERTER")
        header.setObjectName("HeaderLabel")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)
        
        # Input section
        input_group = QGroupBox("INPUT_PATH")
        input_layout = QVBoxLayout(input_group)
        
        input_label = QLabel("PASTE_YOUR_PATH:")
        input_label.setObjectName("SectionLabel")
        input_layout.addWidget(input_label)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("C:\\Users\\example\\file.txt or /home/user/file.txt")
        self.input_field.textChanged.connect(self.on_input_changed)
        input_layout.addWidget(self.input_field)
        
        # Quick actions
        quick_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("CLEAR")
        self.clear_btn.clicked.connect(self.clear_input)
        quick_layout.addWidget(self.clear_btn)
        
        self.paste_btn = QPushButton("PASTE")
        self.paste_btn.clicked.connect(self.paste_from_clipboard)
        quick_layout.addWidget(self.paste_btn)
        
        self.convert_btn = QPushButton("CONVERT_ALL")
        self.convert_btn.setObjectName("AccentButton")
        self.convert_btn.clicked.connect(self.convert_all_formats)
        quick_layout.addWidget(self.convert_btn)
        
        quick_layout.addStretch()
        input_layout.addLayout(quick_layout)
        
        main_layout.addWidget(input_group)
        
        # Separator
        separator = QFrame()
        separator.setObjectName("Separator")
        separator.setFrameShape(QFrame.Shape.HLine)
        main_layout.addWidget(separator)
        
        # Settings section
        settings_group = QGroupBox("ADVANCED_FORMATS")
        settings_layout = QVBoxLayout(settings_group)
        
        settings_info = QLabel("Enable additional format outputs:")
        settings_info.setStyleSheet(f"color: {CP_SUBTEXT}; font-size: 9pt;")
        settings_layout.addWidget(settings_info)
        
        # Checkboxes for additional formats
        checkbox_layout = QHBoxLayout()
        
        self.format_checkboxes = {}
        additional_formats = [
            ("ANDROID", "android"),
            ("WSL", "wsl"),
            ("ESCAPED", "escaped"),
            ("RAW_STRING", "raw"),
            ("URI", "uri")
        ]
        
        for title, key in additional_formats:
            checkbox = QCheckBox(title)
            checkbox.stateChanged.connect(self.update_format_visibility)
            self.format_checkboxes[key] = checkbox
            checkbox_layout.addWidget(checkbox)
        
        checkbox_layout.addStretch()
        settings_layout.addLayout(checkbox_layout)
        main_layout.addWidget(settings_group)
        
        # Output formats section
        output_group = QGroupBox("OUTPUT_FORMATS")
        output_layout = QVBoxLayout(output_group)
        
        # Create format outputs
        self.format_outputs = {}
        self.format_frames = {}
        
        # Default formats (always visible)
        default_formats = [
            ("FORWARD_SLASH", "Forward slash (C:/path/to/file)", "forward"),
            ("DOUBLE_FORWARD", "Double forward slash (C://path//to//file)", "double_forward"),
            ("BACKSLASH", "Backslash (C:\\path\\to\\file)", "backslash"),
            ("DOUBLE_BACKSLASH", "Double backslash (C:\\\\path\\\\to\\\\file)", "double_backslash")
        ]
        
        # Additional formats (toggleable)
        additional_format_details = [
            ("ANDROID", "Android format (/storage/emulated/0/path)", "android"),
            ("WSL", "WSL format (/mnt/c/path/to/file)", "wsl"),
            ("ESCAPED", "Escaped format (C:\\\\\\\\path\\\\\\\\to\\\\\\\\file)", "escaped"),
            ("RAW_STRING", "Python raw string (r'C:\\path\\to\\file')", "raw"),
            ("URI", "File URI (file:///C:/path/to/file)", "uri")
        ]
        
        all_formats = default_formats + additional_format_details
        
        for title, description, key in all_formats:
            format_frame = self.create_format_output(title, description, key)
            self.format_frames[key] = format_frame
            output_layout.addWidget(format_frame)
            
            # Hide additional formats by default
            if key in self.format_checkboxes:
                format_frame.setVisible(False)
        
        main_layout.addWidget(output_group)
        
        # Status
        self.status_label = QLabel("SYSTEM_READY >> Paste a path to begin conversion")
        self.status_label.setObjectName("StatusLabel")
        main_layout.addWidget(self.status_label)
        
    def create_format_output(self, title, description, key):
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(5)
        
        # Title and copy button
        header_layout = QHBoxLayout()
        
        title_label = QLabel(f"{title}:")
        title_label.setObjectName("SectionLabel")
        header_layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"color: {CP_SUBTEXT}; font-size: 9pt;")
        header_layout.addWidget(desc_label)
        
        header_layout.addStretch()
        
        copy_btn = QPushButton("COPY")
        copy_btn.setObjectName("CopyButton")
        copy_btn.clicked.connect(lambda: self.copy_to_clipboard(key))
        header_layout.addWidget(copy_btn)
        
        layout.addLayout(header_layout)
        
        # Output field
        output_field = QLineEdit()
        output_field.setReadOnly(True)
        output_field.setPlaceholderText("Converted path will appear here...")
        self.format_outputs[key] = output_field
        layout.addWidget(output_field)
        
        return frame
    
    def update_format_visibility(self):
        """Show/hide format outputs based on checkbox states"""
        for key, checkbox in self.format_checkboxes.items():
            if key in self.format_frames:
                self.format_frames[key].setVisible(checkbox.isChecked())
        
        # Update status
        visible_count = sum(1 for cb in self.format_checkboxes.values() if cb.isChecked())
        total_formats = 4 + visible_count  # 4 default + additional
        self.status_label.setText(f"FORMAT_DISPLAY >> Showing {total_formats} formats")
    
    def on_input_changed(self):
        input_path = self.input_field.text().strip()
        if input_path:
            self.convert_all_formats()
        else:
            self.clear_all_outputs()
    
    def clear_input(self):
        self.input_field.clear()
        self.clear_all_outputs()
        self.status_label.setText("INPUT_CLEARED >> Ready for new path")
    
    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        if text:
            self.input_field.setText(text)
            self.status_label.setText("PATH_PASTED >> Auto-converting formats")
        else:
            self.status_label.setText("CLIPBOARD_EMPTY >> No text to paste")
    
    def clear_all_outputs(self):
        for output_field in self.format_outputs.values():
            output_field.clear()
    
    def convert_all_formats(self):
        input_path = self.input_field.text().strip()
        if not input_path:
            self.status_label.setText("NO_INPUT >> Enter a path to convert")
            return
        
        try:
            # Normalize the input path
            normalized = self.normalize_path(input_path)
            
            # Convert to different formats
            conversions = {
                "forward": self.to_forward_slash_format(normalized),
                "double_forward": self.to_double_forward_format(normalized),
                "backslash": self.to_backslash_format(normalized),
                "double_backslash": self.to_double_backslash_format(normalized),
                "android": self.to_android_format(normalized),
                "wsl": self.to_wsl_format(normalized),
                "escaped": self.to_escaped_format(normalized),
                "raw": self.to_raw_string_format(normalized),
                "uri": self.to_uri_format(normalized)
            }
            
            # Update output fields
            for key, converted_path in conversions.items():
                if key in self.format_outputs:
                    self.format_outputs[key].setText(converted_path)
            
            self.status_label.setText("CONVERSION_COMPLETE >> All formats generated")
            
        except Exception as e:
            self.status_label.setText(f"CONVERSION_ERROR >> {str(e)}")
    
    def normalize_path(self, path):
        """Normalize path separators and clean up the path"""
        # Remove quotes if present
        path = path.strip('\'"')
        
        # Handle raw strings
        if path.startswith(('r"', "r'")):
            path = path[2:-1]
        
        # Handle file URIs
        if path.startswith('file:///'):
            path = path[8:]  # Remove file:///
            if len(path) > 1 and path[1] == ':':  # Windows drive
                path = path.replace('/', '\\')
        elif path.startswith('file://'):
            path = path[7:]  # Remove file://
        
        # Normalize separators
        path = path.replace('\\\\', '\\').replace('//', '/')
        
        return path
    
    def to_forward_slash_format(self, path):
        """Convert to forward slash format (C:/path/to/file)"""
        forward_path = path.replace('\\', '/')
        
        # Handle WSL paths
        if forward_path.startswith('/mnt/'):
            parts = forward_path.split('/')
            if len(parts) >= 3:
                drive = parts[2].upper()
                remaining = '/'.join(parts[3:])
                forward_path = f"{drive}:/{remaining}"
        
        # Keep Windows drive letters but use forward slashes
        if len(forward_path) > 1 and forward_path[1] == ':':
            return forward_path
        
        # Handle Linux paths - assume they need a drive letter
        if forward_path.startswith('/') and not (len(forward_path) > 1 and forward_path[1] == ':'):
            forward_path = f"C:{forward_path}"
        
        return forward_path
    
    def to_double_forward_format(self, path):
        """Convert to double forward slash format (C://path//to//file)"""
        single_forward = self.to_forward_slash_format(path)
        return single_forward.replace('/', '//')
    
    def to_backslash_format(self, path):
        """Convert to backslash format (C:\\path\\to\\file)"""
        backslash_path = path.replace('/', '\\')
        
        # Handle WSL paths
        if backslash_path.startswith('\\mnt\\'):
            parts = backslash_path.split('\\')
            if len(parts) >= 3:
                drive = parts[2].upper()
                remaining = '\\'.join(parts[3:])
                backslash_path = f"{drive}:\\{remaining}"
        
        # Handle Linux/Android paths
        elif backslash_path.startswith('\\') and not (len(backslash_path) > 1 and backslash_path[1] == ':'):
            backslash_path = f"C:{backslash_path}"
        
        return backslash_path
    
    def to_double_backslash_format(self, path):
        """Convert to double backslash format (C:\\\\path\\\\to\\\\file)"""
        single_backslash = self.to_backslash_format(path)
        return single_backslash.replace('\\', '\\\\')
    
    def to_linux_format(self, path):
        """Convert to Linux format with forward slashes"""
        linux_path = path.replace('\\', '/')
        
        # Handle Windows drive letters
        if len(linux_path) > 1 and linux_path[1] == ':':
            # Convert C:/... to /c/...
            drive = linux_path[0].lower()
            remaining = linux_path[3:] if len(linux_path) > 3 else ""
            linux_path = f"/{drive}/{remaining}"
        
        # Ensure it starts with /
        if not linux_path.startswith('/'):
            linux_path = '/' + linux_path
        
        return linux_path
    
    def to_android_format(self, path):
        """Convert to Android format"""
        android_path = self.to_linux_format(path)
        
        # If it looks like an external storage path, use Android convention
        if not android_path.startswith('/storage/') and not android_path.startswith('/sdcard/'):
            # Remove drive letter paths and use Android external storage
            if android_path.startswith('/c/') or android_path.startswith('/d/'):
                remaining = '/'.join(android_path.split('/')[2:])
                android_path = f"/storage/emulated/0/{remaining}"
            elif not android_path.startswith('/'):
                android_path = f"/storage/emulated/0/{android_path}"
        
        return android_path
    
    def to_escaped_format(self, path):
        """Convert to escaped format for strings"""
        backslash_path = self.to_backslash_format(path)
        return backslash_path.replace('\\', '\\\\\\\\')  # Quadruple escape for string literals
    
    def to_raw_string_format(self, path):
        """Convert to Python raw string format"""
        backslash_path = self.to_backslash_format(path)
        return f"r'{backslash_path}'"
    
    def to_forward_slash_format(self, path):
        """Convert to forward slash format (Windows with forward slashes)"""
        forward_path = path.replace('\\', '/')
        
        # Keep Windows drive letters but use forward slashes
        if len(forward_path) > 1 and forward_path[1] == ':':
            return forward_path
        
        # Handle other formats
        return self.to_windows_format(path).replace('\\', '/')
    
    def to_wsl_format(self, path):
        """Convert to WSL format"""
        wsl_path = path.replace('\\', '/')
        
        # Handle Windows drive letters
        if len(wsl_path) > 1 and wsl_path[1] == ':':
            drive = wsl_path[0].lower()
            remaining = wsl_path[3:] if len(wsl_path) > 3 else ""
            wsl_path = f"/mnt/{drive}/{remaining}"
        
        # Ensure it starts with /
        if not wsl_path.startswith('/'):
            wsl_path = '/' + wsl_path
        
        return wsl_path
    
    def to_uri_format(self, path):
        """Convert to file URI format"""
        forward_path = self.to_forward_slash_format(path)
        
        # Ensure it starts with a drive letter for Windows
        if not (len(forward_path) > 1 and forward_path[1] == ':'):
            forward_path = f"C:/{forward_path.lstrip('/')}"
        
        return f"file:///{forward_path}"
    
    def copy_to_clipboard(self, format_key):
        if format_key in self.format_outputs:
            text = self.format_outputs[format_key].text()
            if text:
                clipboard = QApplication.clipboard()
                clipboard.setText(text)
                self.status_label.setText(f"COPIED >> {format_key.upper()} format copied to clipboard")
            else:
                self.status_label.setText("NO_OUTPUT >> Nothing to copy")

def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Path Converter")
    app.setApplicationVersion("1.0")
    
    window = PathConverter()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()