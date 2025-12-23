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
    delete_clicked = pyqtSignal(int)

    def __init__(self, port, description="Flask App", parent=None):
        super().__init__(parent)
        self.port = port
        self.setObjectName("PortCard")
        self.setFixedHeight(70)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Port Info
        info_layout = QVBoxLayout()
        port_label = QLabel(f"Port: {port}")
        port_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 12px; color: #B0B0B0;")
        info_layout.addWidget(port_label)
        info_layout.addWidget(desc_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Status Badge
        self.status_label = QLabel("Checking...")
        self.status_label.setFixedSize(80, 24)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            border-radius: 12px;
            font-size: 10px;
            font-weight: bold;
            background-color: #333333;
            color: #FFFFFF;
        """)
        layout.addWidget(self.status_label)
        
        # Delete Button
        self.del_btn = QPushButton()
        self.del_btn.setIcon(qta.icon('fa5s.trash-alt', color='#666666'))
        self.del_btn.setIconSize(QSize(16, 16))
        self.del_btn.setFixedSize(32, 32)
        self.del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.del_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #666666;
                font-size: 16px;
                border: none;
            }
            QPushButton:hover {
                color: #FF5252;
            }
        """)
        self.del_btn.clicked.connect(lambda: self.delete_clicked.emit(self.port))
        layout.addWidget(self.del_btn)
        
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
        main_layout.setContentsMargins(30, 40, 30, 30)
        main_layout.setSpacing(25)

        # Header
        header_layout = QVBoxLayout()
        title = QLabel("Port Explorer")
        title.setStyleSheet("font-size: 32px; font-weight: 800; color: #FFFFFF;")
        subtitle = QLabel("Manage and discover free ports for your apps")
        subtitle.setStyleSheet("font-size: 14px; color: #888888;")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        main_layout.addLayout(header_layout)

        # Suggestion Section
        suggestion_box = QFrame()
        suggestion_box.setObjectName("SuggestionBox")
        
        # Add Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 100))
        suggestion_box.setGraphicsEffect(shadow)
        
        sugg_layout = QVBoxLayout(suggestion_box)
        sugg_layout.setContentsMargins(20, 20, 20, 20)
        
        sugg_header = QLabel("NEXT RECOMMENDED PORT")
        sugg_header.setStyleSheet("font-size: 10px; font-weight: bold; color: #7C4DFF; letter-spacing: 1px;")
        
        self.recommended_port_label = QLabel("----")
        self.recommended_port_label.setStyleSheet("font-size: 48px; font-weight: bold; color: #FFFFFF;")
        
        sugg_btn = QPushButton(" Suggest New Port")
        sugg_btn.setIcon(qta.icon('fa5s.redo-alt', color='white'))
        sugg_btn.setIconSize(QSize(14, 14))
        sugg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        sugg_btn.setFixedHeight(45)
        sugg_btn.setObjectName("PrimaryButton")
        sugg_btn.clicked.connect(self.suggest_port)
        
        sugg_layout.addWidget(sugg_header)
        sugg_layout.addWidget(self.recommended_port_label)
        sugg_layout.addWidget(sugg_btn)
        main_layout.addWidget(suggestion_box)

        # Input Section
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Enter port (e.g. 8080)")
        self.port_input.setFixedHeight(45)
        self.port_input.returnPressed.connect(self.add_manual_port)
        
        add_btn = QPushButton(" Add Port")
        add_btn.setIcon(qta.icon('fa5s.plus', color='white'))
        add_btn.setIconSize(QSize(12, 12))
        add_btn.setFixedHeight(45)
        add_btn.setFixedWidth(120)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setObjectName("SecondaryButton")
        add_btn.clicked.connect(self.add_manual_port)
        
        input_layout.addWidget(self.port_input)
        input_layout.addWidget(add_btn)
        main_layout.addWidget(input_container)

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
                    return json.load(f)
            except:
                return []
        return []

    def save_ports(self):
        with open(STORAGE_FILE, 'w') as f:
            json.dump(self.reserved_ports, f)

    def refresh_list(self):
        # Clear current list
        for i in reversed(range(self.list_layout.count())): 
            self.list_layout.itemAt(i).widget().setParent(None)

        for port in sorted(self.reserved_ports):
            card = PortCard(port)
            card.delete_clicked.connect(self.remove_port)
            self.list_layout.addWidget(card)

    def add_manual_port(self):
        port_text = self.port_input.text().strip()
        if not port_text.isdigit():
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid port number.")
            return
        
        port = int(port_text)
        if port in self.reserved_ports:
            QMessageBox.information(self, "Exists", "This port is already in your list.")
            return

        self.reserved_ports.append(port)
        self.save_ports()
        self.refresh_list()
        self.port_input.clear()
        self.suggest_port()

    def remove_port(self, port):
        if port in self.reserved_ports:
            self.reserved_ports.remove(port)
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
            if port not in self.reserved_ports and self.is_port_free(port):
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
