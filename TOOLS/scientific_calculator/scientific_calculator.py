import sys
import os
import math
import json
import ast
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                             QGroupBox, QFormLayout, QTabWidget, QDialog, 
                             QComboBox, QSpinBox, QCheckBox, QListWidget, 
                             QGridLayout, QScrollArea, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QFont, QCursor, QIcon, QDoubleValidator, QIntValidator

# CYBERPUNK COLOR PALETTES
CP_BG = "#050505"           # Main Window Background
CP_PANEL = "#111111"        # Panel/Input Background
CP_DIM = "#3a3a3a"          # Dimmed/Borders/Inactive
CP_TEXT = "#E0E0E0"         # Primary Text
CP_SUBTEXT = "#808080"      # Secondary Text

# Accent choices
ACCENTS = {
    "Cyan": "#00F0FF",
    "Yellow": "#FCEE0A",
    "Red": "#FF003C",
    "Green": "#00ff21",
    "Orange": "#ff934b"
}

# MATPLOTLIB SETUP
try:
    import matplotlib
    matplotlib.use('QtAgg')
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# SETTINGS MANAGER
class Settings:
    def __init__(self):
        self.filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')
        self.data = {
            "accent_name": "Cyan",
            "accent_color": "#00F0FF",
            "font_size": 10,
            "sound_enabled": True
        }
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
            except Exception:
                pass

    def save(self):
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

# SAFE MATHEMATICAL EVALUATION ENGINE
class ScientificEngine:
    ALLOWED_NAMES = {
        'pi', 'e', 'tau', 'sin', 'cos', 'tan', 'asin', 'acos', 'atan',
        'sinh', 'cosh', 'tanh', 'asinh', 'acosh', 'atanh', 'sqrt', 'cbrt',
        'log', 'ln', 'log2', 'log10', 'exp', 'pow', 'factorial', 'abs',
        'ceil', 'floor', 'x', 'y'
    }

    def __init__(self):
        self.is_degrees = True

    def _wrap_deg(self, f):
        return lambda x: f(math.radians(x))

    def _wrap_deg_inv(self, f):
        return lambda x: math.degrees(f(x))

    def get_safe_dict(self, x_val=None, y_val=None):
        # Base math functions
        safe_dict = {
            'pi': math.pi,
            'e': math.e,
            'tau': math.tau,
            'sinh': math.sinh,
            'cosh': math.cosh,
            'tanh': math.tanh,
            'asinh': math.asinh,
            'acosh': math.acosh,
            'atanh': math.atanh,
            'sqrt': math.sqrt,
            'cbrt': lambda v: math.copysign(abs(v) ** (1/3), v) if v < 0 else v ** (1/3),
            'log': math.log10, # default log is log10 in calculator standard
            'ln': math.log,
            'log2': math.log2,
            'log10': math.log10,
            'exp': math.exp,
            'pow': math.pow,
            'factorial': math.factorial,
            'abs': abs,
            'ceil': math.ceil,
            'floor': math.floor,
        }

        # Trigonometry based on Mode (Degrees vs Radians)
        if self.is_degrees:
            safe_dict['sin'] = self._wrap_deg(math.sin)
            safe_dict['cos'] = self._wrap_deg(math.cos)
            safe_dict['tan'] = self._wrap_deg(math.tan)
            safe_dict['asin'] = self._wrap_deg_inv(math.asin)
            safe_dict['acos'] = self._wrap_deg_inv(math.acos)
            safe_dict['atan'] = self._wrap_deg_inv(math.atan)
        else:
            safe_dict['sin'] = math.sin
            safe_dict['cos'] = math.cos
            safe_dict['tan'] = math.tan
            safe_dict['asin'] = math.asin
            safe_dict['acos'] = math.acos
            safe_dict['atan'] = math.atan

        if x_val is not None:
            safe_dict['x'] = x_val
        if y_val is not None:
            safe_dict['y'] = y_val

        return safe_dict

    def validate(self, expr_str):
        if "__" in expr_str:
            return False
        try:
            tree = ast.parse(expr_str, mode='eval')
        except SyntaxError:
            return False

        allowed_nodes = {
            ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Constant,
            ast.Name, ast.Call, ast.Load,
            ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow, ast.USub, ast.UAdd
        }

        for node in ast.walk(tree):
            if type(node) not in allowed_nodes:
                return False
            if isinstance(node, ast.Name):
                if node.id not in self.ALLOWED_NAMES:
                    return False
        return True

    def evaluate(self, expr_str, x_val=None, y_val=None):
        # Normalize multiplication (replace standard math signs if any)
        # We also replace visual power symbol '^' with Python's '**'
        norm_expr = expr_str.replace('^', '**')
        
        if not self.validate(norm_expr):
            raise ValueError("Forbidden syntax or terms detected.")
        
        compiled = compile(norm_expr, '<string>', 'eval')
        context = self.get_safe_dict(x_val, y_val)
        res = eval(compiled, {"__builtins__": None}, context)
        return res

# CUSTOM CYBERPUNK BUTTON
class CyberButton(QPushButton):
    def __init__(self, text, accent_color, parent=None, is_action=False):
        super().__init__(text, parent)
        self.accent = accent_color
        self.is_action = is_action
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.update_style()

    def update_accent(self, color):
        self.accent = color
        self.update_style()

    def update_style(self):
        if self.is_action:
            bg = CP_PANEL
            text_color = self.accent
            border = self.accent
            hover_bg = self.accent
            hover_text = "#000000"
        else:
            bg = CP_DIM
            text_color = "#FFFFFF"
            border = CP_DIM
            hover_bg = "#2a2a2a"
            hover_text = self.accent

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {text_color};
                border: 1px solid {border};
                padding: 10px;
                font-family: 'Consolas';
                font-size: 10pt;
                font-weight: bold;
                border-radius: 0px;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
                color: {hover_text};
                border: 1px solid {self.accent};
            }}
            QPushButton:pressed {{
                background-color: {self.accent};
                color: #000000;
            }}
        """)

# CUSTOM CYBERPUNK DUAL-LINE DISPLAY
class CyberDisplay(QFrame):
    def __init__(self, accent_color, parent=None):
        super().__init__(parent)
        self.accent = accent_color
        self.init_ui()

    def init_ui(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.setSpacing(4)

        # Top formula line
        self.formula_label = QLabel("")
        self.formula_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.formula_label.setStyleSheet(f"color: {CP_SUBTEXT}; font-family: 'Consolas'; font-size: 10pt;")
        
        # Primary input/result line
        self.display_input = QLineEdit("0")
        self.display_input.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.display_input.setReadOnly(True)
        self.display_input.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        
        self.layout.addWidget(self.formula_label)
        self.layout.addWidget(self.display_input)
        self.update_accent(self.accent)

    def update_accent(self, color):
        self.accent = color
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CP_PANEL};
                border: 1px solid {CP_DIM};
            }}
            QFrame:hover, QFrame:focus-within {{
                border: 1px solid {self.accent};
            }}
        """)
        self.display_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: transparent;
                color: {self.accent};
                border: none;
                font-family: 'Consolas';
                font-size: 18pt;
                font-weight: bold;
            }}
        """)

    def set_formula(self, text):
        self.formula_label.setText(text)

    def get_formula(self):
        return self.formula_label.text()

    def set_value(self, text):
        self.display_input.setText(text)

    def get_value(self):
        return self.display_input.text()

# MATPLOTLIB CANVAS STYLED FOR CYBERPUNK
class GraphingCanvas(FigureCanvas):
    def __init__(self, accent_color, width=5, height=4, dpi=100):
        self.accent = accent_color
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor=CP_BG)
        self.ax = self.fig.add_subplot(111, facecolor=CP_BG)
        
        super().__init__(self.fig)
        self.update_style()

    def update_accent(self, color):
        self.accent = color
        self.update_style()

    def update_style(self):
        self.ax.set_facecolor(CP_BG)
        self.fig.set_facecolor(CP_BG)
        
        # Configure axes spine colors
        for spine in self.ax.spines.values():
            spine.set_color(CP_DIM)
            spine.set_linewidth(1)

        # Configure labels & grid colors
        self.ax.tick_params(colors=CP_TEXT, labelsize=9)
        self.ax.xaxis.label.set_color(self.accent)
        self.ax.yaxis.label.set_color(self.accent)
        
        self.ax.grid(True, color=CP_DIM, linestyle='--', linewidth=0.5)
        self.fig.tight_layout()
        self.draw()

    def plot_equation(self, x_vals, y_vals, title=""):
        self.ax.clear()
        self.update_style()
        
        if len(x_vals) > 0 and len(y_vals) > 0:
            # Multi-layered glowing neon trace line effect
            self.ax.plot(x_vals, y_vals, color=self.accent, linewidth=4, alpha=0.15)
            self.ax.plot(x_vals, y_vals, color=self.accent, linewidth=2, alpha=0.4)
            self.ax.plot(x_vals, y_vals, color=self.accent, linewidth=1.2, alpha=1.0)
            
        self.ax.set_title(title, color=self.accent, fontsize=10, family='sans-serif', fontweight='bold')
        self.draw()

# 64-BIT GRID WIDGET
class BitGridWidget(QWidget):
    # Fires when any bit toggles, sending the updated decimal value
    from PyQt6.QtCore import pyqtSignal
    valueChanged = pyqtSignal(int)

    def __init__(self, accent_color, parent=None):
        super().__init__(parent)
        self.accent = accent_color
        self.val = 0
        self.bit_buttons = []
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create a grid of 8 rows and 8 columns (64 bits, from 63 down to 0)
        for row in range(8):
            row_label = QLabel(f"B{63 - row*8:02d}..{56 - row*8:02d}:")
            row_label.setStyleSheet(f"color: {CP_SUBTEXT}; font-family: 'Consolas'; font-size: 8pt; font-weight: bold;")
            layout.addWidget(row_label, row, 0)
            
            for col in range(8):
                bit_idx = 63 - (row * 8 + col)
                btn = QPushButton("0")
                btn.setFixedSize(QSize(28, 28))
                btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                btn.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
                
                # Capture bit_idx using default argument in lambda
                btn.clicked.connect(lambda checked, idx=bit_idx: self.toggle_bit(idx))
                
                layout.addWidget(btn, row, col + 1)
                self.bit_buttons.append((bit_idx, btn))
        
        # Sort buttons list so index matches array index (0 to 63)
        self.bit_buttons.sort(key=lambda x: x[0])
        self.update_visuals()

    def update_accent(self, color):
        self.accent = color
        self.update_visuals()

    def toggle_bit(self, idx):
        self.val ^= (1 << idx)
        self.update_visuals()
        self.valueChanged.emit(self.val)

    def set_value(self, value):
        # Mask to 64-bit unsigned representation
        self.val = value & 0xFFFFFFFFFFFFFFFF
        self.update_visuals()

    def update_visuals(self):
        for idx, btn in self.bit_buttons:
            bit_state = (self.val >> idx) & 1
            btn.setText(str(bit_state))
            
            if bit_state == 1:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {self.accent};
                        color: #000000;
                        border: 1px solid {self.accent};
                        font-family: 'Consolas';
                        font-weight: bold;
                        border-radius: 0px;
                    }}
                    QPushButton:hover {{
                        background-color: #ffffff;
                        border-color: #ffffff;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {CP_PANEL};
                        color: {CP_SUBTEXT};
                        border: 1px solid {CP_DIM};
                        font-family: 'Consolas';
                        border-radius: 0px;
                    }}
                    QPushButton:hover {{
                        background-color: {CP_DIM};
                        color: #ffffff;
                        border-color: {self.accent};
                    }}
                """)

# SETTINGS DIALOG
class SettingsDialog(QDialog):
    def __init__(self, settings_obj, parent=None):
        super().__init__(parent)
        self.settings = settings_obj
        self.setWindowTitle("SYSTEM CONFIGURATION")
        self.resize(350, 200)
        self.init_ui()

    def init_ui(self):
        # Window properties
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {CP_BG};
                border: 2px solid {self.settings.data["accent_color"]};
            }}
            QWidget {{
                color: {CP_TEXT};
                font-family: 'Consolas';
                font-size: 10pt;
            }}
            QLabel {{
                font-weight: bold;
            }}
        """)

        layout = QVBoxLayout(self)

        group = QGroupBox("PARAMETERS")
        group.setStyleSheet(f"""
            QGroupBox {{
                border: 1px solid {CP_DIM};
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                color: {self.settings.data["accent_color"]};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }}
        """)
        
        form = QFormLayout(group)

        # Accent color selection
        self.accent_combo = QComboBox()
        self.accent_combo.addItems(list(ACCENTS.keys()))
        self.accent_combo.setCurrentText(self.settings.data["accent_name"])
        self.accent_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {CP_PANEL};
                color: {self.settings.data["accent_color"]};
                border: 1px solid {CP_DIM};
                padding: 4px;
            }}
        """)
        form.addRow("ACCENT CORE:", self.accent_combo)

        # Font size input
        self.font_spin = QSpinBox()
        self.font_spin.setRange(8, 16)
        self.font_spin.setValue(self.settings.data["font_size"])
        self.font_spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {CP_PANEL};
                color: {self.settings.data["accent_color"]};
                border: 1px solid {CP_DIM};
                padding: 4px;
            }}
        """)
        form.addRow("FONT SIZE:", self.font_spin)

        # Audio effects
        self.audio_check = QCheckBox()
        self.audio_check.setChecked(self.settings.data["sound_enabled"])
        self.audio_check.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
                border: 1px solid {CP_DIM};
                background: {CP_PANEL};
            }}
            QCheckBox::indicator:checked {{
                background: {self.settings.data["accent_color"]};
                border-color: {self.settings.data["accent_color"]};
            }}
        """)
        form.addRow("AUDIO FX:", self.audio_check)

        layout.addWidget(group)

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("SAVE")
        self.save_btn.clicked.connect(self.save_settings)
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CP_DIM};
                color: #FFFFFF;
                border: 1px solid {CP_DIM};
                padding: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.settings.data["accent_color"]};
                color: #000000;
                border: 1px solid {self.settings.data["accent_color"]};
            }}
        """)
        
        self.cancel_btn = QPushButton("CANCEL")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {CP_SUBTEXT};
                border: 1px solid {CP_DIM};
                padding: 6px;
            }}
            QPushButton:hover {{
                color: #FFFFFF;
                border: 1px solid #FFFFFF;
            }}
        """)
        
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def save_settings(self):
        self.settings.data["accent_name"] = self.accent_combo.currentText()
        self.settings.data["accent_color"] = ACCENTS[self.accent_combo.currentText()]
        self.settings.data["font_size"] = self.font_spin.value()
        self.settings.data["sound_enabled"] = self.audio_check.isChecked()
        self.settings.save()
        self.accept()

# MAIN WINDOW APPLICATION
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.engine = ScientificEngine()
        self.calc_memory = 0.0
        self.history_items = []
        self.clear_on_next_input = False
        
        self.setWindowTitle("NEO-CALC // COGNITIVE COMPUTER v1.0")
        self.resize(920, 720)
        self.init_ui()

    def init_ui(self):
        # Apply window theme style
        self.setStyleSheet(f"QMainWindow {{ background-color: {CP_BG}; }}")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(10)

        # --- HEADER UTILITY ROW ---
        header_layout = QHBoxLayout()
        
        # Blinking / Active LED status dot
        self.led_indicator = QLabel("●")
        self.led_indicator.setStyleSheet(f"color: {self.settings.data['accent_color']}; font-size: 14pt;")
        self.led_timer = QTimer()
        self.led_timer.timeout.connect(self.toggle_led)
        self.led_timer.start(800)
        
        title_label = QLabel("NEO-CALC // MULTI-THREAD SYSTEM")
        title_label.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {self.settings.data['accent_color']}; letter-spacing: 2px;")
        
        header_layout.addWidget(self.led_indicator)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        # RESTART BUTTON
        self.restart_btn = QPushButton("↺ RESTART")
        self.restart_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.restart_btn.clicked.connect(self.restart_app)
        header_layout.addWidget(self.restart_btn)

        # SETTINGS BUTTON
        self.settings_btn = QPushButton("⚙ SETTINGS")
        self.settings_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.settings_btn.clicked.connect(self.open_settings)
        header_layout.addWidget(self.settings_btn)
        
        main_layout.addLayout(header_layout)

        # --- CORE WORKSPACE TAB LAYOUT ---
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.setup_scientific_tab()
        self.setup_graphing_tab()
        self.setup_converter_tab()

        # Bottom status notification bar
        self.status_bar = QLabel("SYSTEM STATUS: ONLINE // RAD MODE INACTIVE")
        self.status_bar.setStyleSheet(f"color: {CP_SUBTEXT}; font-family: 'Consolas'; font-size: 8pt; border-top: 1px solid {CP_DIM}; padding-top: 5px;")
        main_layout.addWidget(self.status_bar)

        self.apply_global_theme()

    def toggle_led(self):
        curr_style = self.led_indicator.styleSheet()
        if "color: transparent" in curr_style:
            self.led_indicator.setStyleSheet(f"color: {self.settings.data['accent_color']}; font-size: 14pt;")
        else:
            self.led_indicator.setStyleSheet("color: transparent; font-size: 14pt;")

    def apply_global_theme(self):
        accent = self.settings.data["accent_color"]
        size = self.settings.data["font_size"]
        
        # Stylize TabWidget
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {CP_DIM};
                background: {CP_BG};
            }}
            QTabBar::tab {{
                background: {CP_PANEL};
                color: {CP_SUBTEXT};
                border: 1px solid {CP_DIM};
                padding: 8px 16px;
                font-family: 'Consolas';
                font-weight: bold;
                font-size: 10pt;
            }}
            QTabBar::tab:selected {{
                background: {CP_BG};
                color: {accent};
                border-bottom: 2px solid {accent};
                border-top: 1px solid {accent};
            }}
            QTabBar::tab:hover {{
                color: {accent};
            }}
        """)

        # Stylize standard inputs and header buttons
        header_btn_style = f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {CP_DIM};
                color: {CP_TEXT};
                padding: 4px 10px;
                font-family: 'Consolas';
                font-weight: bold;
                font-size: 9pt;
            }}
            QPushButton:hover {{
                border: 1px solid {accent};
                color: {accent};
            }}
        """
        self.restart_btn.setStyleSheet(header_btn_style)
        self.settings_btn.setStyleSheet(header_btn_style)

        # Update displays & custom widgets
        self.display.update_accent(accent)
        for btn in self.calc_buttons:
            btn.update_accent(accent)

        if MATPLOTLIB_AVAILABLE:
            self.canvas.update_accent(accent)

        # Update graphing inputs
        graph_input_style = f"""
            QLineEdit, QSpinBox {{
                background-color: {CP_PANEL};
                color: {accent};
                border: 1px solid {CP_DIM};
                padding: 4px;
                font-family: 'Consolas';
            }}
            QLineEdit:focus, QSpinBox:focus {{
                border: 1px solid {accent};
            }}
        """
        self.graph_expr.setStyleSheet(graph_input_style)
        self.graph_xmin.setStyleSheet(graph_input_style)
        self.graph_xmax.setStyleSheet(graph_input_style)
        self.graph_plot_btn.update_accent(accent)
        self.graph_clear_btn.update_accent(accent)

        # Update base converter elements
        conv_style = f"""
            QLineEdit {{
                background-color: {CP_PANEL};
                color: {accent};
                border: 1px solid {CP_DIM};
                padding: 6px;
                font-family: 'Consolas';
                font-size: 11pt;
                font-weight: bold;
            }}
            QLineEdit:focus {{
                border: 1px solid {accent};
            }}
            QLabel {{
                font-family: 'Consolas';
                font-weight: bold;
                color: {CP_TEXT};
            }}
        """
        self.hex_input.setStyleSheet(conv_style)
        self.dec_input.setStyleSheet(conv_style)
        self.oct_input.setStyleSheet(conv_style)
        self.bin_input.setStyleSheet(conv_style)
        self.bit_grid.update_accent(accent)
        
        for btn in self.conv_operators:
            btn.update_accent(accent)

        # Update history styling
        self.history_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {CP_PANEL};
                border: 1px solid {CP_DIM};
                color: {CP_TEXT};
                font-family: 'Consolas';
                font-size: 9pt;
                padding: 5px;
            }}
            QListWidget::item {{
                border-bottom: 1px solid {CP_DIM};
                padding: 4px;
            }}
            QListWidget::item:hover {{
                background-color: {CP_DIM};
                color: {accent};
            }}
            QListWidget::item:selected {{
                background-color: {accent};
                color: #000000;
            }}
        """)
        
        self.history_clear.setStyleSheet(header_btn_style)

        # Update status message
        mode = "DEG" if self.engine.is_degrees else "RAD"
        self.update_status(f"SYSTEM ACCENT COMPILATION: SUCCESS // {mode} MODE ACTIVE")

    def update_status(self, text):
        self.status_bar.setText(f"SYSTEM STATUS: {text}")

    def open_settings(self):
        dlg = SettingsDialog(self.settings, self)
        if dlg.exec():
            self.apply_global_theme()

    def restart_app(self):
        # Native restart implementation to re-execute process
        os.execv(sys.executable, [sys.executable] + sys.argv)

    # =========================================================================
    # SCIENTIFIC TAB SETUP & FUNCTIONS
    # =========================================================================
    def setup_scientific_tab(self):
        tab = QWidget()
        self.tabs.addTab(tab, "⚙ SCIENTIFIC ENGINE")

        layout = QHBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Main Calculator Grid (Left Side)
        calc_layout = QVBoxLayout()
        calc_layout.setSpacing(6)
        
        # Display Box
        self.display = CyberDisplay(self.settings.data["accent_color"])
        calc_layout.addWidget(self.display)

        # Keyboard Grid
        grid_layout = QGridLayout()
        grid_layout.setSpacing(4)
        
        # Button matrix definition
        # Format: (Text, Row, Col, ColumnSpan, RowSpan, IsAction)
        buttons = [
            # Row 0
            ("sin", 0, 0, 1, 1, False),
            ("cos", 0, 1, 1, 1, False),
            ("tan", 0, 2, 1, 1, False),
            ("C", 0, 3, 1, 1, True),
            ("⌫", 0, 4, 1, 1, True),
            ("mod", 0, 5, 1, 1, False),
            ("MC", 0, 6, 1, 1, True),

            # Row 1
            ("sinh", 1, 0, 1, 1, False),
            ("cosh", 1, 1, 1, 1, False),
            ("tanh", 1, 2, 1, 1, False),
            ("7", 1, 3, 1, 1, False),
            ("8", 1, 4, 1, 1, False),
            ("9", 1, 5, 1, 1, False),
            ("/", 1, 6, 1, 1, True),

            # Row 2
            ("asin", 2, 0, 1, 1, False),
            ("acos", 2, 1, 1, 1, False),
            ("atan", 2, 2, 1, 1, False),
            ("4", 2, 3, 1, 1, False),
            ("5", 2, 4, 1, 1, False),
            ("6", 2, 5, 1, 1, False),
            ("*", 2, 6, 1, 1, True),

            # Row 3
            ("ln", 3, 0, 1, 1, False),
            ("log", 3, 1, 1, 1, False),
            ("sqrt", 3, 2, 1, 1, False),
            ("1", 3, 3, 1, 1, False),
            ("2", 3, 4, 1, 1, False),
            ("3", 3, 5, 1, 1, False),
            ("-", 3, 6, 1, 1, True),

            # Row 4
            ("x^y", 4, 0, 1, 1, False),
            ("x^2", 4, 1, 1, 1, False),
            ("x!", 4, 2, 1, 1, False),
            ("0", 4, 3, 1, 1, False),
            (".", 4, 4, 1, 1, False),
            ("+/-", 4, 5, 1, 1, False),
            ("+", 4, 6, 1, 1, True),

            # Row 5
            ("pi", 5, 0, 1, 1, False),
            ("e", 5, 1, 1, 1, False),
            ("abs", 5, 2, 1, 1, False),
            ("MS", 5, 3, 1, 1, True),
            ("MR", 5, 4, 1, 1, True),
            ("M+", 5, 5, 1, 1, True),
            ("M-", 5, 6, 1, 1, True),

            # Row 6
            ("rand", 6, 0, 1, 1, False),
            ("(", 6, 1, 1, 1, False),
            (")", 6, 2, 1, 1, False),
            ("DEG/RAD", 6, 3, 1, 1, True),
            ("=", 6, 4, 1, 3, True)
        ]

        self.calc_buttons = []
        for btn_info in buttons:
            text = btn_info[0]
            r = btn_info[1]
            c = btn_info[2]
            row_span = btn_info[3]
            col_span = btn_info[4]
            is_action = btn_info[5] if len(btn_info) > 5 else False

            btn = CyberButton(text, self.settings.data["accent_color"], is_action=is_action)
            btn.clicked.connect(lambda checked, t=text: self.on_calc_btn_clicked(t))
            grid_layout.addWidget(btn, r, c, row_span, col_span)
            self.calc_buttons.append(btn)

        calc_layout.addLayout(grid_layout)
        layout.addLayout(calc_layout, stretch=3)

        # Expression History Panel (Right Side)
        hist_layout = QVBoxLayout()
        hist_layout.setSpacing(6)
        
        hist_header = QHBoxLayout()
        hist_title = QLabel("MATRIX LOG HISTORY")
        hist_title.setStyleSheet("font-family: 'Consolas'; font-weight: bold; color: #FFFFFF;")
        
        self.history_clear = QPushButton("CLEAR LOG")
        self.history_clear.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.history_clear.clicked.connect(self.clear_history)
        
        hist_header.addWidget(hist_title)
        hist_header.addStretch()
        hist_header.addWidget(self.history_clear)
        hist_layout.addLayout(hist_header)

        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self.on_history_item_clicked)
        hist_layout.addWidget(self.history_list)

        layout.addLayout(hist_layout, stretch=1)

    def on_calc_btn_clicked(self, text):
        # Audio feedback trigger simulation
        if self.settings.data["sound_enabled"]:
            # PyQt6 core has no quick beep without external, standard system beep is suitable
            QApplication.beep()

        current_val = self.display.get_value()
        current_formula = self.display.get_formula()

        if text == "C":
            self.display.set_value("0")
            self.display.set_formula("")
            self.clear_on_next_input = False
            self.update_status("REGISTERS WIPED CLEAN")
        
        elif text == "⌫":
            if len(current_val) > 1:
                self.display.set_value(current_val[:-1])
            else:
                self.display.set_value("0")
            self.clear_on_next_input = False

        elif text == "DEG/RAD":
            self.engine.is_degrees = not self.engine.is_degrees
            mode = "DEG" if self.engine.is_degrees else "RAD"
            self.update_status(f"TRIGONOMETRIC CORE SWITCHED: {mode} ACTIVE")
            # Refresh stylesheet tab border or label if necessary
            self.apply_global_theme()

        elif text in ("MC", "MR", "M+", "M-", "MS"):
            self.handle_memory(text, current_val)

        elif text == "=":
            # Reconstruct complete equation expression
            expr_to_eval = current_formula + current_val
            try:
                # Replace special representations with machine expressions
                eval_expr = expr_to_eval
                # Perform calculation
                res = self.engine.evaluate(eval_expr)
                
                # Format floating output to prevent extremely long precision strings
                if isinstance(res, float):
                    if res.is_integer():
                        res_str = str(int(res))
                    else:
                        res_str = f"{res:.10g}"
                else:
                    res_str = str(res)

                self.display.set_formula("")
                self.display.set_value(res_str)
                
                # Add to history matrix
                log_entry = f"{expr_to_eval} = {res_str}"
                self.history_items.append(log_entry)
                self.history_list.insertItem(0, log_entry) # newest at top
                
                self.clear_on_next_input = True
                self.update_status("CALCULATION COMPLETED")
            except Exception as e:
                self.display.set_value("ERROR")
                self.clear_on_next_input = True
                self.update_status(f"MATH ERROR: {str(e)}")

        elif text == "+/-":
            if current_val != "0" and not current_val.startswith("ERROR"):
                if current_val.startswith("-"):
                    self.display.set_value(current_val[1:])
                else:
                    self.display.set_value("-" + current_val)

        elif text in ("+", "-", "*", "/", "mod"):
            op_map = {"mod": "%"}
            op_symbol = op_map.get(text, text)
            
            # If there's an error, reset formula
            if "ERROR" in current_val:
                self.display.set_value("0")
                return

            self.display.set_formula(current_formula + current_val + " " + op_symbol + " ")
            self.clear_on_next_input = True

        elif text in ("sin", "cos", "tan", "sinh", "cosh", "tanh", "asin", "acos", "atan", "sinh", "cosh", "tanh", "asinh", "acosh", "atanh", "sqrt", "ln", "log", "abs", "factorial"):
            # Wrap current text or insert command
            if current_val == "0" or self.clear_on_next_input:
                self.display.set_value(f"{text}(")
                self.clear_on_next_input = False
            else:
                self.display.set_value(f"{text}({current_val})")

        elif text == "x^y":
            self.display.set_formula(current_formula + current_val + " ^ ")
            self.clear_on_next_input = True

        elif text == "x^2":
            if current_val != "0":
                self.display.set_value(f"({current_val})^2")
            else:
                self.display.set_value("0")

        elif text == "x!":
            self.display.set_value(f"factorial({current_val})")

        elif text == "rand":
            # Generate random value in range [0, 1)
            val = str(round(math.random() if hasattr(math, 'random') else os.urandom(1)[0]/256, 6)) # safe random fallback
            import random
            val = f"{random.random():.6f}"
            self.display.set_value(val)
            self.clear_on_next_input = False

        else:
            # Number inputs, constants, and dots
            if self.clear_on_next_input or current_val == "0":
                self.display.set_value(text)
                self.clear_on_next_input = False
            else:
                # Limit dots
                if text == "." and "." in current_val:
                    return
                self.display.set_value(current_val + text)

    def handle_memory(self, action, value):
        try:
            num = float(value)
        except ValueError:
            num = 0.0

        if action == "MC":
            self.calc_memory = 0.0
            self.update_status("MEMORY CLEARED")
        elif action == "MR":
            # Display memory value
            if self.calc_memory.is_integer():
                self.display.set_value(str(int(self.calc_memory)))
            else:
                self.display.set_value(f"{self.calc_memory:.10g}")
            self.clear_on_next_input = True
            self.update_status(f"MEMORY RECALLED: {self.calc_memory}")
        elif action == "MS":
            self.calc_memory = num
            self.update_status(f"MEMORY STORED: {self.calc_memory}")
        elif action == "M+":
            self.calc_memory += num
            self.update_status(f"MEMORY ADDED: {self.calc_memory}")
        elif action == "M-":
            self.calc_memory -= num
            self.update_status(f"MEMORY SUBTRACTED: {self.calc_memory}")

    def on_history_item_clicked(self, item):
        # Extract formula / result from history
        parts = item.text().split(" = ")
        if len(parts) == 2:
            self.display.set_formula("")
            self.display.set_value(parts[1])
            self.clear_on_next_input = True
            self.update_status("LOADED ITEM FROM HISTORICAL MATRIX")

    def clear_history(self):
        self.history_items.clear()
        self.history_list.clear()
        self.update_status("HISTORICAL LOG CRUSHED")

    # =========================================================================
    # GRAPHING TAB SETUP & FUNCTIONS
    # =========================================================================
    def setup_graphing_tab(self):
        tab = QWidget()
        self.tabs.addTab(tab, "📈 WAVEFORM GRAPHING")

        layout = QHBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Plot Config Panels (Left Side)
        control_panel = QGroupBox("PLOT VECTORS")
        control_panel.setStyleSheet(f"""
            QGroupBox {{
                border: 1px solid {CP_DIM};
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                color: {self.settings.data["accent_color"]};
            }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
        """)
        form = QFormLayout(control_panel)

        # Function Input
        self.graph_expr = QLineEdit("sin(x)")
        form.addRow("f(x) =", self.graph_expr)

        # Range Inputs
        self.graph_xmin = QLineEdit("-10")
        self.graph_xmax = QLineEdit("10")
        form.addRow("X MIN:", self.graph_xmin)
        form.addRow("X MAX:", self.graph_xmax)

        # Draw / Clear buttons
        self.graph_plot_btn = CyberButton("RENDER WAVE", self.settings.data["accent_color"], is_action=True)
        self.graph_plot_btn.clicked.connect(self.plot_graph)
        form.addRow(self.graph_plot_btn)

        self.graph_clear_btn = CyberButton("CLEAR PANEL", self.settings.data["accent_color"], is_action=False)
        self.graph_clear_btn.clicked.connect(self.clear_graph)
        form.addRow(self.graph_clear_btn)

        layout.addWidget(control_panel, stretch=1)

        # Plot Canvas Container (Right Side)
        canvas_container = QFrame()
        canvas_container.setFrameShape(QFrame.Shape.StyledPanel)
        canvas_container.setStyleSheet(f"background-color: {CP_BG}; border: 1px solid {CP_DIM};")
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(2, 2, 2, 2)

        if MATPLOTLIB_AVAILABLE:
            self.canvas = GraphingCanvas(self.settings.data["accent_color"])
            canvas_layout.addWidget(self.canvas)
        else:
            lbl = QLabel("MATPLOTLIB CORE ENGINE OFFLINE\nCANNOT INITIALIZE GRAPHING CANVAS")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("color: #FF003C; font-family: 'Consolas'; font-weight: bold;")
            canvas_layout.addWidget(lbl)

        layout.addWidget(canvas_container, stretch=3)

    def plot_graph(self):
        if not MATPLOTLIB_AVAILABLE:
            QMessageBox.critical(self, "SYSTEM FAULT", "Matplotlib engine is not present.")
            return

        expr = self.graph_expr.text()
        
        try:
            xmin = float(self.graph_xmin.text())
            xmax = float(self.graph_xmax.text())
        except ValueError:
            self.update_status("PLOT FAULT: INVALID RANGE BOUNDARIES")
            return

        if xmin >= xmax:
            self.update_status("PLOT FAULT: MIN LIMIT GREATER THAN MAX")
            return

        # Generate X data points (1000 points for smoothness)
        import numpy as np
        x_vals = np.linspace(xmin, xmax, 1000)
        y_vals = []
        
        errors = 0
        valid_x = []
        valid_y = []

        for x in x_vals:
            try:
                # Evaluate expression using engine context
                val = self.engine.evaluate(expr, x_val=x)
                # Keep float real outputs
                if isinstance(val, (int, float)) and not math.isnan(val) and not math.isinf(val):
                    valid_x.append(x)
                    valid_y.append(val)
            except Exception:
                errors += 1

        if len(valid_x) == 0:
            self.update_status("PLOT FAULT: EXPRESSION NOT MATH EVALUATABLE")
            return

        self.canvas.plot_equation(valid_x, valid_y, title=f"y = {expr}")
        self.update_status(f"WAVE PLOTTED: {len(valid_x)} VECTORS (ERRORS BLOCKED: {errors})")

    def clear_graph(self):
        if MATPLOTLIB_AVAILABLE:
            self.canvas.plot_equation([], [], "CANVAS CLEARED")
            self.update_status("CANVAS RESET SUCCESSFULLY")

    # =========================================================================
    # BASE CONVERTER (PROGRAMMER) TAB
    # =========================================================================
    def setup_converter_tab(self):
        tab = QWidget()
        self.tabs.addTab(tab, "💻 BINARY BASE CONVERTER")

        layout = QHBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Input Base Fields (Left)
        fields_panel = QWidget()
        fields_layout = QVBoxLayout(fields_panel)
        fields_layout.setContentsMargins(0, 0, 0, 0)
        
        group_base = QGroupBox("REGISTER NUMERICS")
        group_base.setStyleSheet(f"""
            QGroupBox {{
                border: 1px solid {CP_DIM};
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                color: {self.settings.data["accent_color"]};
            }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
        """)
        
        form = QFormLayout(group_base)

        self.hex_input = QLineEdit("0")
        self.dec_input = QLineEdit("0")
        self.oct_input = QLineEdit("0")
        self.bin_input = QLineEdit("0")

        # Connect slots for editing bases
        self.hex_input.textEdited.connect(lambda text: self.on_base_edited(text, 16))
        self.dec_input.textEdited.connect(lambda text: self.on_base_edited(text, 10))
        self.oct_input.textEdited.connect(lambda text: self.on_base_edited(text, 8))
        self.bin_input.textEdited.connect(lambda text: self.on_base_edited(text, 2))

        form.addRow("HEX (Hexadecimal):", self.hex_input)
        form.addRow("DEC (Decimal):", self.dec_input)
        form.addRow("OCT (Octal):", self.oct_input)
        form.addRow("BIN (Binary):", self.bin_input)

        fields_layout.addWidget(group_base)

        # Bitwise Operator Keyboard panel
        bit_op_group = QGroupBox("BITWISE COMMANDS")
        bit_op_group.setStyleSheet(f"""
            QGroupBox {{
                border: 1px solid {CP_DIM};
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                color: {self.settings.data["accent_color"]};
            }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
        """)
        grid = QGridLayout(bit_op_group)
        grid.setSpacing(4)

        operators = [
            ("NOT (~)", "NOT"),
            ("AND (&)", "AND"),
            ("OR (|)", "OR"),
            ("XOR (^)", "XOR"),
            ("LSH (<<)", "LSH"),
            ("RSH (>>)", "RSH"),
            ("2's Comp", "COMP"),
            ("CLR", "CLR")
        ]

        self.conv_operators = []
        for idx, (label, action) in enumerate(operators):
            btn = CyberButton(label, self.settings.data["accent_color"], is_action=True)
            btn.clicked.connect(lambda checked, act=action: self.on_bitwise_op(act))
            row = idx // 2
            col = idx % 2
            grid.addWidget(btn, row, col)
            self.conv_operators.append(btn)

        fields_layout.addWidget(bit_op_group)
        layout.addWidget(fields_panel, stretch=1)

        # Bit grid visual representation (Right)
        right_panel = QGroupBox("64-BIT REGISTRY VECTOR")
        right_panel.setStyleSheet(f"""
            QGroupBox {{
                border: 1px solid {CP_DIM};
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                color: {self.settings.data["accent_color"]};
            }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)

        self.bit_grid = BitGridWidget(self.settings.data["accent_color"])
        self.bit_grid.valueChanged.connect(self.on_grid_bit_toggled)
        right_layout.addWidget(self.bit_grid)
        right_layout.addStretch()

        layout.addWidget(right_panel, stretch=1)

        # State storage for bitwise operations
        self.bitwise_operand = None
        self.bitwise_operator = None

    def update_base_fields(self, val):
        # Update inputs with value formatting (Masked to 64-bit unsigned)
        unsigned_val = val & 0xFFFFFFFFFFFFFFFF
        
        # Hex (formatted upper case with no 0x prefix)
        self.hex_input.setText(f"{unsigned_val:X}")
        # Dec (standard string)
        self.dec_input.setText(str(unsigned_val))
        # Oct (octal digits)
        self.oct_input.setText(f"{unsigned_val:o}")
        # Bin (grouped binary spacing optional, but flat string keeps it clean)
        self.bin_input.setText(f"{unsigned_val:b}")
        
        self.bit_grid.set_value(unsigned_val)

    def on_base_edited(self, text, base):
        if not text:
            self.update_base_fields(0)
            return

        try:
            # Parse based on context base
            val = int(text, base)
            self.update_base_fields(val)
            self.update_status(f"VAL UPDATED FROM BASE {base}")
        except ValueError:
            # Keep display, but warn status
            self.update_status(f"INPUT FAULT: INVALID BASE {base} VALUE")

    def on_grid_bit_toggled(self, val):
        self.update_base_fields(val)

    def on_bitwise_op(self, action):
        current_val = self.bit_grid.val
        
        if action == "CLR":
            self.update_base_fields(0)
            self.bitwise_operand = None
            self.bitwise_operator = None
            self.update_status("CONVERTER REGISTER FLUSHED")
            
        elif action == "NOT":
            # 64-bit bitwise NOT
            new_val = (~current_val) & 0xFFFFFFFFFFFFFFFF
            self.update_base_fields(new_val)
            self.update_status("BITWISE NOT COMPLETED")
            
        elif action == "COMP":
            # Two's complement negation: ~val + 1
            new_val = (-current_val) & 0xFFFFFFFFFFFFFFFF
            self.update_base_fields(new_val)
            self.update_status("2'S COMPLEMENT COMPLETED")
            
        elif action in ("AND", "OR", "XOR"):
            self.bitwise_operand = current_val
            self.bitwise_operator = action
            self.update_base_fields(0) # Clear field for next input
            self.update_status(f"OPERAND A LOADED. INPUT B AND PRESS OPERATION AGAIN TO FINISH")
            
        elif action in ("LSH", "RSH"):
            # Simple shift by 1 bit for immediate feedback
            if action == "LSH":
                new_val = (current_val << 1) & 0xFFFFFFFFFFFFFFFF
                self.update_status("SHIFTED REGISTER LEFT 1 BIT")
            else:
                new_val = (current_val >> 1) & 0xFFFFFFFFFFFFFFFF
                self.update_status("SHIFTED REGISTER RIGHT 1 BIT")
            self.update_base_fields(new_val)

        # Check if operand was set, and this is the second press to compute result
        if action == self.bitwise_operator and self.bitwise_operand is not None:
            val_a = self.bitwise_operand
            val_b = current_val
            
            if action == "AND":
                res = val_a & val_b
            elif action == "OR":
                res = val_a | val_b
            elif action == "XOR":
                res = val_a ^ val_b
            else:
                res = 0

            self.update_base_fields(res)
            self.bitwise_operand = None
            self.bitwise_operator = None
            self.update_status(f"BITWISE EVALUATION: SUCCESS")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
