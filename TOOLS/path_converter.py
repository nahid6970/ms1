import sys
import os
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QComboBox, QCheckBox, QFileDialog, QMessageBox, 
                             QFrame, QTextEdit, QGroupBox, QFormLayout, QRadioButton,
                             QButtonGroup, QListWidget, QSplitter,
                             QListWidgetItem)
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
        self.setGeometry(100, 100, 700, 400)  # Reduced from 900x700 to 700x400
        self.setFixedSize(700, 400)  # Make window non-resizable for compact design
        
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
        main_layout.setContentsMargins(20, 20, 20, 20)  # Reduced margins
        main_layout.setSpacing(15)  # Reduced spacing
        
        # Header
        header = QLabel("PATH_CONVERTER")
        header.setObjectName("HeaderLabel")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)
        
        # Input section
        input_group = QGroupBox("INPUT_PATH")
        input_layout = QVBoxLayout(input_group)
        
        # Input field with separator selector
        input_row = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Paste your path here...")
        self.input_field.textChanged.connect(self.on_input_changed)
        input_row.addWidget(self.input_field, 2)  # Give more space to input
        
        # Separator selector
        separator_label = QLabel("FORMAT:")
        separator_label.setObjectName("SectionLabel")
        input_row.addWidget(separator_label)
        
        self.separator_combo = QComboBox()
        self.separator_combo.addItem("/ (Forward)", "forward")
        self.separator_combo.addItem("// (Double Forward)", "double_forward") 
        self.separator_combo.addItem("\\ (Backslash)", "backslash")
        self.separator_combo.addItem("\\\\ (Double Back)", "double_backslash")
        self.separator_combo.addItem("WSL", "wsl")
        self.separator_combo.addItem("Android", "android")
        self.separator_combo.addItem("Escaped", "escaped")
        self.separator_combo.addItem("Raw String", "raw")
        self.separator_combo.addItem("URI", "uri")
        self.separator_combo.currentTextChanged.connect(self.on_format_changed)
        input_row.addWidget(self.separator_combo, 1)
        
        input_layout.addLayout(input_row)
        main_layout.addWidget(input_group)
        
        # Output section
        output_group = QGroupBox("CONVERTED_OUTPUT")
        output_layout = QVBoxLayout(output_group)
        
        # Output field with copy button
        output_row = QHBoxLayout()
        
        self.output_field = QLineEdit()
        self.output_field.setReadOnly(True)
        self.output_field.setPlaceholderText("Converted path will appear here...")
        self.output_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {CP_PANEL}; 
                color: {CP_GREEN}; 
                border: 1px solid {CP_GREEN}; 
                padding: 8px;
                font-size: 10pt;
                font-weight: bold;
            }}
        """)
        output_row.addWidget(self.output_field, 3)
        
        self.copy_output_btn = QPushButton("COPY")
        self.copy_output_btn.setObjectName("AccentButton")
        self.copy_output_btn.clicked.connect(self.copy_output_to_clipboard)
        output_row.addWidget(self.copy_output_btn)
        
        output_layout.addLayout(output_row)
        main_layout.addWidget(output_group)
        
        # Status
        self.status_label = QLabel("SYSTEM_READY >> Paste a path and select format")
        self.status_label.setObjectName("StatusLabel")
        main_layout.addWidget(self.status_label)
        
    def on_format_changed(self):
        """Convert path when format selection changes"""
        self.convert_path()
        
    def on_input_changed(self):
        """Convert path when input changes"""
        self.convert_path()
    
    def copy_output_to_clipboard(self):
        output_text = self.output_field.text()
        if output_text:
            clipboard = QApplication.clipboard()
            clipboard.setText(output_text)
            format_name = self.separator_combo.currentText().split(' ')[0]
            self.status_label.setText(f"COPIED >> {format_name} format copied to clipboard")
        else:
            self.status_label.setText("NO_OUTPUT >> Nothing to copy")
    
    def convert_path(self):
        input_path = self.input_field.text().strip()
        if not input_path:
            self.output_field.clear()
            return
        
        try:
            # Get selected format
            format_key = self.separator_combo.currentData()
            
            # Normalize the input path
            normalized = self.normalize_path(input_path)
            
            # Convert to selected format
            if format_key == "forward":
                converted = self.to_forward_slash_format(normalized)
            elif format_key == "double_forward":
                converted = self.to_double_forward_format(normalized)
            elif format_key == "backslash":
                converted = self.to_backslash_format(normalized)
            elif format_key == "double_backslash":
                converted = self.to_double_backslash_format(normalized)
            elif format_key == "wsl":
                converted = self.to_wsl_format(normalized)
            elif format_key == "android":
                converted = self.to_android_format(normalized)
            elif format_key == "escaped":
                converted = self.to_escaped_format(normalized)
            elif format_key == "raw":
                converted = self.to_raw_string_format(normalized)
            elif format_key == "uri":
                converted = self.to_uri_format(normalized)
            else:
                converted = normalized
            
            self.output_field.setText(converted)
            format_name = self.separator_combo.currentText().split(' ')[0]
            self.status_label.setText(f"CONVERTED >> {format_name} format ready")
            
        except Exception as e:
            self.status_label.setText(f"CONVERSION_ERROR >> {str(e)}")
            self.output_field.clear()
    
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