import sys
import os
import json
import subprocess

# Suppress Qt font warnings
os.environ["QT_LOGGING_RULES"] = "qt.text.font.db=false"

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QGroupBox, QScrollArea,
                             QFormLayout, QFrame, QColorDialog)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor

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
AHK_OUTPUT = os.path.join(SCRIPT_DIR, "generate_AHK.ahk")

class RowWidget(QFrame):
    def __init__(self, data=None, on_remove=None, parent_app=None):
        super().__init__()
        self.parent_app = parent_app
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"border: 1px solid {CP_DIM}; background-color: {CP_PANEL}; margin-bottom: 5px;")
        self.on_remove = on_remove
        
        self.layout = QVBoxLayout(self)
        
        # Header: Title and Remove Row
        header_layout = QHBoxLayout()
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Row Title (e.g., Name/Label)")
        self.title_input.setText(data.get("title", "") if data else "")
        self.title_color = data.get("title_color", "FFCC00") if data else "FFCC00"
        self.title_text_color = data.get("title_text_color", "000000") if data else "000000"
        self.title_color_btn = QPushButton()
        self.title_color_btn.setFixedSize(50, 24)
        self.title_color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.title_color_btn.clicked.connect(self._pick_title_color)
        self.title_text_color_btn = QPushButton()
        self.title_text_color_btn.setFixedSize(50, 24)
        self.title_text_color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.title_text_color_btn.clicked.connect(self._pick_title_text_color)
        self._update_title_color_btn()
        self._update_title_text_color_btn()
        header_layout.addWidget(QLabel("TITLE:"))
        header_layout.addWidget(self.title_input)
        header_layout.addWidget(self.title_color_btn)
        header_layout.addWidget(self.title_text_color_btn)
        
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

    def _update_title_color_btn(self):
        c = self.title_color
        r, g, b = int(c[0:2],16), int(c[2:4],16), int(c[4:6],16)
        fg = "black" if (r*299+g*587+b*114)/1000 > 128 else "white"
        self.title_color_btn.setText(f"#{c}")
        self.title_color_btn.setStyleSheet(f"background-color: #{c}; color: {fg}; border: 1px solid #888; font-size: 7pt; font-weight: bold; padding: 0;")

    def _pick_title_color(self):
        color = QColorDialog.getColor(QColor(f"#{self.title_color}"))
        if color.isValid():
            self.title_color = color.name().upper().strip("#")
            self._update_title_color_btn()

    def _update_title_text_color_btn(self):
        c = self.title_text_color
        r, g, b = int(c[0:2],16), int(c[2:4],16), int(c[4:6],16)
        fg = "black" if (r*299+g*587+b*114)/1000 > 128 else "white"
        self.title_text_color_btn.setText(f"#{c}")
        self.title_text_color_btn.setStyleSheet(f"background-color: #{c}; color: {fg}; border: 1px solid #888; font-size: 7pt; font-weight: bold; padding: 0;")

    def _pick_title_text_color(self):
        color = QColorDialog.getColor(QColor(f"#{self.title_text_color}"))
        if color.isValid():
            self.title_text_color = color.name().upper().strip("#")
            self._update_title_text_color_btn()

    def refresh_widths(self):
        if not self.parent_app: return
        try:
            lw = int(self.parent_app.settings_panel.ui_label_w.text())
            tw = int(self.parent_app.settings_panel.ui_text_w.text())
            for i in range(self.btns_layout.count()):
                btn_frame = self.btns_layout.itemAt(i).widget()
                if btn_frame:
                    inputs = btn_frame.findChildren(QLineEdit)
                    if len(inputs) >= 2:
                        inputs[0].setFixedWidth(lw)
                        inputs[1].setFixedWidth(tw)
        except: pass

    def add_button_ui(self, b_data=None):
        btn_frame = QFrame()
        btn_frame.setFrameShape(QFrame.Shape.Panel)
        btn_frame.setStyleSheet(f"border: 1px dashed {CP_DIM}; padding: 2px;")
        blayout = QHBoxLayout(btn_frame)
        
        label_input = QLineEdit()
        label_input.setPlaceholderText("Label")
        label_input.setText(b_data.get("label", "") if b_data else "")
        
        text_input = QLineEdit()
        text_input.setPlaceholderText("Text")
        text_input.setText(b_data.get("text", "") if b_data else "")
        
        # BG Color Picker Button
        bg_btn = QPushButton("BG")
        bg_btn.setObjectName("bg_btn")
        bg_btn.setFixedWidth(35)
        bg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        bg_btn.color_val = b_data.get("color", "00CCFF") if b_data else "00CCFF"

        # TX Color Picker Button
        tx_btn = QPushButton("TX")
        tx_btn.setObjectName("tx_btn")
        tx_btn.setFixedWidth(35)
        tx_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        tx_btn.color_val = b_data.get("text_color", "000000") if b_data else "000000"

        def update_styles():
            bg_btn.setStyleSheet(f"background-color: #{bg_btn.color_val}; color: {'white' if bg_btn.color_val == '000000' else 'black'}; border: 1px solid white; font-size: 8pt; font-weight: bold;")
            tx_btn.setStyleSheet(f"background-color: #{tx_btn.color_val}; color: {'white' if tx_btn.color_val == '000000' else 'black'}; border: 1px solid white; font-size: 8pt; font-weight: bold;")
        
        def pick_bg():
            color = QColorDialog.getColor(QColor(f"#{bg_btn.color_val}"))
            if color.isValid():
                bg_btn.color_val = color.name().upper().strip("#")
                update_styles()

        def pick_tx():
            color = QColorDialog.getColor(QColor(f"#{tx_btn.color_val}"))
            if color.isValid():
                tx_btn.color_val = color.name().upper().strip("#")
                update_styles()

        bg_btn.clicked.connect(pick_bg)
        tx_btn.clicked.connect(pick_tx)
        update_styles()

        rem_btn = QPushButton("-")
        rem_btn.setFixedWidth(25)
        rem_btn.clicked.connect(lambda: btn_frame.deleteLater())

        blayout.addWidget(QLabel("L:"))
        blayout.addWidget(label_input)
        blayout.addWidget(QLabel("T:"))
        blayout.addWidget(text_input)
        blayout.addWidget(bg_btn)
        blayout.addWidget(tx_btn)
        blayout.addWidget(rem_btn)
        
        self.btns_layout.addWidget(btn_frame)
        self.refresh_widths()

    def remove_self(self):
        if self.on_remove:
            self.on_remove(self)

    def get_data(self):
        row_data = {
            "title": self.title_input.text(),
            "title_color": self.title_color,
            "title_text_color": self.title_text_color,
            "buttons": []
        }
        for i in range(self.btns_layout.count()):
            btn_frame = self.btns_layout.itemAt(i).widget()
            if btn_frame:
                inputs = btn_frame.findChildren(QLineEdit)
                bg = btn_frame.findChild(QPushButton, "bg_btn").color_val
                tx = btn_frame.findChild(QPushButton, "tx_btn").color_val
                row_data["buttons"].append({
                    "label": inputs[0].text(),
                    "text": inputs[1].text(),
                    "color": bg,
                    "text_color": tx
                })
        return row_data

class SettingsPanel(QGroupBox):
    def __init__(self, update_callback):
        super().__init__("SETTINGS")
        self.setVisible(False)
        self.layout = QFormLayout(self)
        
        self.auto_hide = QLineEdit("True")
        self.sleep_delay = QLineEdit("200")
        self.font_size = QLineEdit("12")
        self.ui_label_w = QLineEdit("80")
        self.ui_text_w = QLineEdit("200")
        self.title_h = QLineEdit("30")
        self.title_w = QLineEdit("200")
        self.btn_h = QLineEdit("30")
        self.btn_w = QLineEdit("100")
        
        self.ui_label_w.textChanged.connect(update_callback)
        self.ui_text_w.textChanged.connect(update_callback)

        def row(field1, *pairs):
            w = QWidget(); h = QHBoxLayout(w); h.setContentsMargins(0,0,0,0)
            h.addWidget(field1)
            for lbl, field in pairs:
                h.addWidget(QLabel(lbl)); h.addWidget(field)
            return w

        self.layout.addRow("Auto-Hide / Sleep (ms):", row(self.auto_hide, ("Sleep:", self.sleep_delay)))
        self.layout.addRow("Font Size:", self.font_size)
        self.layout.addRow("UI Label / Text Width:", row(self.ui_label_w, ("T:", self.ui_text_w)))
        self.layout.addRow("Title H / W:", row(self.title_h, ("W:", self.title_w)))
        self.layout.addRow("Button H / W:", row(self.btn_h, ("W:", self.btn_w)))

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
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(f"color: {CP_GREEN}; font-size: 9pt;")
        toolbar.addWidget(self.status_label)
        toolbar.addWidget(settings_btn)
        toolbar.addWidget(restart_btn)
        toolbar.addWidget(gen_btn)
        self.main_layout.addLayout(toolbar)

        # Settings Panel (Hidden by default)
        self.settings_panel = SettingsPanel(self.update_ui_widths)
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

    def update_ui_widths(self):
        for row in self.rows:
            row.refresh_widths()

    def add_row(self, data=None):
        row = RowWidget(data, on_remove=self.remove_row, parent_app=self)
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
                    rows_data = []
                    if isinstance(data, dict):
                        if "settings" in data:
                            s = data["settings"]
                            if "auto_hide" in s: self.settings_panel.auto_hide.setText(s["auto_hide"])
                            if "sleep_delay" in s: self.settings_panel.sleep_delay.setText(s["sleep_delay"])
                            if "font_size" in s: self.settings_panel.font_size.setText(s["font_size"])
                            if "ui_label_w" in s: self.settings_panel.ui_label_w.setText(s["ui_label_w"])
                            if "ui_text_w" in s: self.settings_panel.ui_text_w.setText(s["ui_text_w"])
                            if "title_h" in s: self.settings_panel.title_h.setText(s["title_h"])
                            if "title_w" in s: self.settings_panel.title_w.setText(s["title_w"])
                            if "btn_h" in s: self.settings_panel.btn_h.setText(s["btn_h"])
                            if "btn_w" in s: self.settings_panel.btn_w.setText(s["btn_w"])
                        rows_data = data.get("rows", [])
                    else:
                        rows_data = data
                    
                    for r_data in rows_data:
                        self.add_row(r_data)
            except Exception as e:
                print(f"Error loading config: {e}")
        else:
            # Default example
            self.add_row({"title": "Example Name", "buttons": [{"label": "en", "text": "Hello", "color": "00CCFF"}]})

    def save_config(self):
        data = {
            "settings": {
                "auto_hide": self.settings_panel.auto_hide.text(),
                "sleep_delay": self.settings_panel.sleep_delay.text(),
                "font_size": self.settings_panel.font_size.text(),
                "ui_label_w": self.settings_panel.ui_label_w.text(),
                "ui_text_w": self.settings_panel.ui_text_w.text(),
                "title_h": self.settings_panel.title_h.text(),
                "title_w": self.settings_panel.title_w.text(),
                "btn_h": self.settings_panel.btn_h.text(),
                "btn_w": self.settings_panel.btn_w.text()
            },
            "rows": [r.get_data() for r in self.rows]
        }
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
            tc = row.get("title_color", "FFCC00")
            ttc = row.get("title_text_color", "000000")
            ahk_code.append(f'myGui.SetFont("s12 Bold c{ttc}", "Jetbrainsmono nfp")')
            th = self.settings_panel.title_h.text() or "30"
            tw = self.settings_panel.title_w.text() or "200"
            bh = self.settings_panel.btn_h.text() or "30"
            bw = self.settings_panel.btn_w.text() or "100"
            ahk_code.append(f'myGui.Add("Text", "xm {y_pos} w{tw} h{th} +Border Center Background{tc}", "{title}")')
            ahk_code.append(f'myGui.SetFont("s12 Bold cDefault", "Jetbrainsmono nfp")')
            
            for btn in row["buttons"]:
                label = btn["label"]
                text = btn["text"].replace('"', '""') # AHK escape
                bg = btn.get("color", "00CCFF")
                fg = btn.get("text_color", "000000")
                ahk_code.append(f'btn := myGui.Add("Text", "x+5 yp w{bw} h{bh} +Border Center Background{bg}", "{label}")')
                ahk_code.append(f'btn.SetFont("c{fg}")')
                ahk_code.append(f'btn.OnEvent("Click", (*) => SendText("{text}"))')
                ahk_code.append(f'btn.OnEvent("ContextMenu", (*) => (A_Clipboard := "{text}"))')
            
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

        with open(AHK_OUTPUT, "w", encoding="utf-8-sig") as f:
            f.write("\n".join(ahk_code))
        
        self.status_label.setText(f"✔ Generated: {AHK_OUTPUT}")
        QTimer.singleShot(1000, lambda: self.status_label.setText(""))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
