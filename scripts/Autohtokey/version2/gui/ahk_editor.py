import sys
import os
import json
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QGroupBox, QScrollArea,
                             QFormLayout, QMessageBox, QFrame)
from PyQt6.QtCore import Qt

# CYBERPUNK THEME PALETTE (from THEME_GUIDE.md)
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_GREEN = "#00ff21"
CP_ORANGE = "#ff934b"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"
CP_SUBTEXT = "#808080"

# Relative paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "ahk_config.json")
AHK_OUTPUT = os.path.join(SCRIPT_DIR, "Bio_Generated.ahk")

class RowWidget(QFrame):
    def __init__(self, data=None, on_remove=None):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"border: 1px solid {CP_DIM}; background-color: {CP_PANEL}; margin-bottom: 5px;")
        self.on_remove = on_remove
        
        self.layout = QVBoxLayout(self)
        
        # Header: Title and Remove Row
        header_layout = QHBoxLayout()
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Row Title (e.g., Name/Label)")
        self.title_input.setText(data.get("title", "") if data else "")
        header_layout.addWidget(QLabel("TITLE:"))
        header_layout.addWidget(self.title_input)
        
        remove_row_btn = QPushButton("×")
        remove_row_btn.setFixedWidth(30)
        remove_row_btn.setStyleSheet(f"background-color: {CP_RED}; color: white; font-weight: bold;")
        remove_row_btn.clicked.connect(self.remove_self)
        header_layout.addWidget(remove_row_btn)
        self.layout.addLayout(header_layout)

        # Buttons Area
        self.btns_container = QWidget()
        self.btns_layout = QVBoxLayout(self.btns_container)
        self.layout.addWidget(self.btns_container)
        
        add_btn_btn = QPushButton("+ ADD ACTION BUTTON")
        add_btn_btn.clicked.connect(lambda: self.add_button_ui())
        self.layout.addWidget(add_btn_btn)

        if data and "buttons" in data:
            for b in data["buttons"]:
                self.add_button_ui(b)
        else:
            # Default empty button
            self.add_button_ui()

    def add_button_ui(self, b_data=None):
        btn_frame = QFrame()
        btn_frame.setFrameShape(QFrame.Shape.Panel)
        btn_frame.setStyleSheet(f"border: 1px dashed {CP_DIM}; padding: 2px;")
        blayout = QHBoxLayout(btn_frame)
        
        label_input = QLineEdit()
        label_input.setPlaceholderText("Btn Label (e.g., en)")
        label_input.setText(b_data.get("label", "") if b_data else "")
        
        text_input = QLineEdit()
        text_input.setPlaceholderText("Send Text")
        text_input.setText(b_data.get("text", "") if b_data else "")
        
        color_input = QLineEdit()
        color_input.setPlaceholderText("Color (Hex)")
        color_input.setText(b_data.get("color", "00CCFF") if b_data else "00CCFF")
        color_input.setFixedWidth(80)

        rem_btn = QPushButton("-")
        rem_btn.setFixedWidth(25)
        rem_btn.clicked.connect(lambda: btn_frame.deleteLater())

        blayout.addWidget(QLabel("Label:"))
        blayout.addWidget(label_input)
        blayout.addWidget(QLabel("Text:"))
        blayout.addWidget(text_input)
        blayout.addWidget(QLabel("Hex:"))
        blayout.addWidget(color_input)
        blayout.addWidget(rem_btn)
        
        self.btns_layout.addWidget(btn_frame)

    def remove_self(self):
        if self.on_remove:
            self.on_remove(self)

    def get_data(self):
        row_data = {
            "title": self.title_input.text(),
            "buttons": []
        }
        for i in range(self.btns_layout.count()):
            btn_frame = self.btns_layout.itemAt(i).widget()
            if btn_frame:
                inputs = btn_frame.findChildren(QLineEdit)
                # Order of QLineEdit: Label, Text, Color
                row_data["buttons"].append({
                    "label": inputs[0].text(),
                    "text": inputs[1].text(),
                    "color": inputs[2].text().strip("#")
                })
        return row_data

class SettingsPanel(QGroupBox):
    def __init__(self):
        super().__init__("SETTINGS")
        self.setVisible(False)
        self.layout = QFormLayout(self)
        self.layout.addRow("Auto-Hide GUI:", QLineEdit("True"))
        self.layout.addRow("Sleep Delay (ms):", QLineEdit("200"))
        self.layout.addRow("Font Size:", QLineEdit("12"))

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberAHK Generator")
        self.resize(1000, 800)
        self.rows = []

        # Global Theme Application
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QScrollArea {{ background: transparent; border: none; }}
            QLineEdit {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;
            }}
            QLineEdit:focus {{ border: 1px solid {CP_CYAN}; }}
            QPushButton {{
                background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 6px 12px; font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW};
            }}
            QGroupBox {{
                border: 1px solid {CP_DIM}; margin-top: 10px; padding-top: 10px; font-weight: bold; color: {CP_YELLOW};
            }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
        """)

        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)

        # Toolbar
        toolbar = QHBoxLayout()
        add_row_btn = QPushButton("+ NEW ROW")
        add_row_btn.clicked.connect(self.add_row)
        
        gen_btn = QPushButton("GENERATE AHK")
        gen_btn.setStyleSheet(f"background-color: {CP_GREEN}; color: black;")
        gen_btn.clicked.connect(self.generate_ahk)

        restart_btn = QPushButton("RESTART APP")
        restart_btn.clicked.connect(self.restart_app)

        settings_btn = QPushButton("SETTINGS")
        settings_btn.clicked.connect(self.toggle_settings)

        toolbar.addWidget(add_row_btn)
        toolbar.addStretch()
        toolbar.addWidget(settings_btn)
        toolbar.addWidget(restart_btn)
        toolbar.addWidget(gen_btn)
        self.main_layout.addLayout(toolbar)

        # Settings Panel (Hidden by default)
        self.settings_panel = SettingsPanel()
        self.main_layout.addWidget(self.settings_panel)

        # Content Area (Scrollable)
        self.scroll = QScrollArea()
        self.scroll_content = QWidget()
        self.rows_layout = QVBoxLayout(self.scroll_content)
        self.rows_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        self.scroll.setWidgetResizable(True)
        self.main_layout.addWidget(self.scroll)

        self.load_config()

    def add_row(self, data=None):
        row = RowWidget(data, on_remove=self.remove_row)
        self.rows.append(row)
        self.rows_layout.addWidget(row)

    def remove_row(self, row_widget):
        self.rows.remove(row_widget)
        row_widget.deleteLater()

    def toggle_settings(self):
        self.settings_panel.setVisible(not self.settings_panel.isVisible())

    def restart_app(self):
        os.execv(sys.executable, ['python'] + sys.argv)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for r_data in data:
                        self.add_row(r_data)
            except Exception as e:
                print(f"Error loading config: {e}")
        else:
            # Default example
            self.add_row({"title": "Example Name", "buttons": [{"label": "en", "text": "Hello", "color": "00CCFF"}]})

    def save_config(self):
        data = [r.get_data() for r in self.rows]
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def generate_ahk(self):
        self.save_config()
        data = [r.get_data() for r in self.rows]
        
        ahk_code = [
            "#Requires AutoHotkey v2.0",
            "",
            'myGui := Gui("+AlwaysOnTop", "Generated Keyboard")',
            'myGui.SetFont("s12 Bold", "Jetbrainsmono nfp")',
            "myGui.MarginX := 20",
            "myGui.MarginY := 20",
            ""
        ]

        for i, row in enumerate(data):
            y_pos = "ym" if i == 0 else "y+5"
            title = row["title"]
            ahk_code.append(f'; {title}')
            
            # Title button/label
            ahk_code.append(f'myGui.Add("Text", "xm {y_pos} w200 +Border Center BackgroundFFCC00", "{title}")')
            
            for btn in row["buttons"]:
                label = btn["label"]
                text = btn["text"].replace('"', '""') # AHK escape
                color = btn["color"]
                ahk_code.append(f'myGui.Add("Text", "x+5 yp w100 +Border Center Background{color}", "{label}") .OnEvent("Click", (*) => SendText("{text}"))')
            
            ahk_code.append("")

        ahk_code.extend([
            "myGui.Show()",
            'myGui.OnEvent("Close", (*) => ExitApp())',
            "",
            "; Function to send text and briefly hide the GUI",
            "SendText(text) {",
            "    myGui.Hide()",
            "    Sleep(200)",
            "    Send(text)",
            "    Sleep(200)",
            "    myGui.Show()",
            "}"
        ])

        with open(AHK_OUTPUT, "w", encoding="utf-16-sig") as f:
            f.write("\n".join(ahk_code))
        
        QMessageBox.information(self, "Success", f"AHK Script generated at:\n{AHK_OUTPUT}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
