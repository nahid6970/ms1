import sys
import json
import socket
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QListWidget, QListWidgetItem, QFrame, QMessageBox,
                             QScrollArea, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QIcon
import qtawesome as qta


# --- Constants & Config ---
STORAGE_FILE = "ports.json"
DEFAULT_START_PORT = 5000

class PortCard(QFrame):
    save_requested = pyqtSignal(int, str)
    delete_clicked = pyqtSignal(int)

    def __init__(self, port, description="Flask App", parent=None):
        super().__init__(parent)
        self.port = port
        self.description = description
        self.setObjectName("PortCard")
        self.setFixedHeight(50)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 5, 15, 5)
        
        # Port Info
        info_layout = QHBoxLayout()
        port_label = QLabel(f"{port}")
        port_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #7C4DFF; min-width: 50px;")
        
        self.desc_input = QLineEdit(description)
        self.desc_input.setPlaceholderText("App name...")
        self.desc_input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                border-bottom: 1px solid transparent;
                color: #FFFFFF;
                font-size: 13px;
                padding: 2px;
            }
            QLineEdit:focus {
                border-bottom: 1px solid #7C4DFF;
                background: #252525;
            }
        """)
        self.desc_input.editingFinished.connect(lambda: self.save_requested.emit(self.port, self.desc_input.text()))

        info_layout.addWidget(port_label)
        info_layout.addSpacing(20)
        info_layout.addWidget(self.desc_input)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Action Buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(5)

        # Edit Button
        self.edit_btn = QPushButton()
        self.edit_btn.setIcon(qta.icon('fa5s.edit', color='#888888'))
        self.edit_btn.setIconSize(QSize(14, 14))
        self.edit_btn.setFixedSize(30, 30)
        self.edit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_btn.setStyleSheet("QPushButton { background: transparent; border: none; } QPushButton:hover { background: #333333; border-radius: 15px; }")
        self.edit_btn.clicked.connect(lambda: self.desc_input.setFocus())
        
        # Delete Button
        self.del_btn = QPushButton()
        self.del_btn.setIcon(qta.icon('fa5s.trash-alt', color='#666666'))
        self.del_btn.setIconSize(QSize(14, 14))
        self.del_btn.setFixedSize(30, 30)
        self.del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.del_btn.setStyleSheet("QPushButton { background: transparent; border: none; } QPushButton:hover { background: #C62828; border-radius: 15px; }")
        self.del_btn.clicked.connect(lambda: self.delete_clicked.emit(self.port))

        actions_layout.addWidget(self.edit_btn)
        actions_layout.addWidget(self.del_btn)
        
        # Status Badge
        self.status_label = QLabel("Checking...")
        self.status_label.setFixedSize(70, 24)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            border-radius: 12px;
            font-size: 9px;
            font-weight: bold;
            background-color: #333333;
            color: #FFFFFF;
        """)
        
        layout.addWidget(self.status_label)
        layout.addLayout(actions_layout)
        
        self.update_status()

    def update_status(self):
        is_free = self.check_port(self.port)
        if is_free:
            self.status_label.setText("IDLE")
            self.status_label.setStyleSheet("background-color: #2E7D32; color: white; border-radius: 12px; font-weight: bold;")
        else:
            self.status_label.setText("IN USE")
            self.status_label.setStyleSheet("background-color: #C62828; color: white; border-radius: 12px; font-weight: bold;")

    def check_port(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0

class PortFinderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Port Explorer")
        self.setMinimumSize(500, 700)
        self.reserved_ports = self.load_ports()
        
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 25, 20, 20)
        main_layout.setSpacing(15)

        # Header
        header_layout = QVBoxLayout()
        title = QLabel("Port Explorer")
        title.setStyleSheet("font-size: 24px; font-weight: 800; color: #FFFFFF;")
        subtitle = QLabel("Manage and discover free ports")
        subtitle.setStyleSheet("font-size: 12px; color: #888888;")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        main_layout.addLayout(header_layout)

        # Suggestion Section
        suggestion_box = QFrame()
        suggestion_box.setObjectName("SuggestionBox")
        suggestion_box.setFixedHeight(120)
        
        # Add Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 100))
        suggestion_box.setGraphicsEffect(shadow)
        
        sugg_layout = QVBoxLayout(suggestion_box)
        sugg_layout.setContentsMargins(15, 10, 15, 10)
        sugg_layout.setSpacing(5)
        
        sugg_header = QLabel("NEXT RECOMMENDED")
        sugg_header.setStyleSheet("font-size: 9px; font-weight: bold; color: #7C4DFF; letter-spacing: 1px;")
        
        self.recommended_port_label = QLabel("----")
        self.recommended_port_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #FFFFFF;")
        
        sugg_btn = QPushButton(" Suggest New Port")
        sugg_btn.setIcon(qta.icon('fa5s.redo-alt', color='white'))
        sugg_btn.setIconSize(QSize(14, 14))
        sugg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        sugg_btn.setFixedHeight(35)
        sugg_btn.setObjectName("PrimaryButton")
        sugg_btn.clicked.connect(self.suggest_port)
        
        sugg_layout.addWidget(sugg_header)
        sugg_layout.addWidget(self.recommended_port_label)
        sugg_layout.addWidget(sugg_btn)
        main_layout.addWidget(suggestion_box)

        # Input Section
        input_container = QWidget()
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(10)
        
        row1 = QHBoxLayout()
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Port")
        self.port_input.setFixedHeight(35)
        self.port_input.returnPressed.connect(self.add_manual_port)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("App Name")
        self.name_input.setFixedHeight(35)
        self.name_input.returnPressed.connect(self.add_manual_port)
        
        row1.addWidget(self.port_input)
        row1.addWidget(self.name_input)

        add_btn = QPushButton(" Add Port")
        add_btn.setIcon(qta.icon('fa5s.plus', color='white'))
        add_btn.setIconSize(QSize(12, 12))
        add_btn.setFixedHeight(35)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setObjectName("SecondaryButton")
        add_btn.clicked.connect(self.add_manual_port)
        
        input_layout.addLayout(row1)
        input_layout.addWidget(add_btn)
        main_layout.addWidget(input_container)
        
        # Spacer for managed ports
        main_layout.addSpacing(10)

        # List Section
        list_header = QLabel("MANAGED PORTS")
        list_header.setStyleSheet("font-size: 11px; font-weight: bold; color: #666666; letter-spacing: 1px;")
        main_layout.addWidget(list_header)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        
        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(10)
        
        self.scroll_area.setWidget(self.list_container)
        main_layout.addWidget(self.scroll_area)

        self.refresh_list()
        self.suggest_port()

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0F0F0F;
            }
            #SuggestionBox {
                background-color: #1A1A1A;
                border-radius: 15px;
                border: 1px solid #2A2A2A;
            }
            #PortCard {
                background-color: #1A1A1A;
                border-radius: 12px;
                border: 1px solid #252525;
            }
            #PortCard:hover {
                background-color: #222222;
                border-color: #333333;
            }
            QLineEdit {
                background-color: #1A1A1A;
                border: 1px solid #2A2A2A;
                border-radius: 8px;
                color: #FFFFFF;
                padding-left: 15px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #7C4DFF;
            }
            #PrimaryButton {
                background-color: #7C4DFF;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            #PrimaryButton:hover {
                background-color: #6C3EEB;
            }
            #SecondaryButton {
                background-color: #2A2A2A;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            #SecondaryButton:hover {
                background-color: #353535;
            }
            QScrollBar:vertical {
                border: none;
                background: #0F0F0F;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #333333;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

    def load_ports(self):
        if os.path.exists(STORAGE_FILE):
            try:
                with open(STORAGE_FILE, 'r') as f:
                    data = json.load(f)
                    # Support legacy format (list of ints) and new format (dict)
                    if isinstance(data, list):
                        return {str(p): "Flask App" for p in data}
                    return data
            except:
                return {}
        return {}

    def save_ports(self):
        with open(STORAGE_FILE, 'w') as f:
            json.dump(self.reserved_ports, f, indent=4)

    def refresh_list(self):
        # Clear current list
        for i in reversed(range(self.list_layout.count())): 
            widget = self.list_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Sort numeric keys
        sorted_ports = sorted(self.reserved_ports.items(), key=lambda x: int(x[0]))
        for port_str, desc in sorted_ports:
            card = PortCard(int(port_str), desc)
            card.delete_clicked.connect(self.remove_port)
            card.save_requested.connect(self.update_port_name)
            self.list_layout.addWidget(card)

    def add_manual_port(self):
        port_text = self.port_input.text().strip()
        name_text = self.name_input.text().strip() or "Flask App"
        
        if not port_text.isdigit():
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid port number.")
            return
        
        if port_text in self.reserved_ports:
            QMessageBox.information(self, "Exists", "This port is already in your list.")
            return

        self.reserved_ports[port_text] = name_text
        self.save_ports()
        self.refresh_list()
        self.port_input.clear()
        self.name_input.clear()
        self.suggest_port()

    def update_port_name(self, port, name):
        self.reserved_ports[str(port)] = name
        self.save_ports()

    def remove_port(self, port):
        port_str = str(port)
        if port_str in self.reserved_ports:
            del self.reserved_ports[port_str]
            self.save_ports()
            self.refresh_list()
            self.suggest_port()

    def is_port_free(self, port):
        # Check system usage
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                result = s.connect_ex(('localhost', port))
                return result != 0
        except:
            return True

    def suggest_port(self):
        port = DEFAULT_START_PORT
        while True:
            # Check if it's in our manual list OR if it's currently used by system
            if str(port) not in self.reserved_ports and self.is_port_free(port):
                self.recommended_port_label.setText(str(port))
                break
            port += 1
            if port > 65535:
                self.recommended_port_label.setText("NONE")
                break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion") # Consistent look across OS
    
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = PortFinderApp()
    window.show()
    sys.exit(app.exec())
