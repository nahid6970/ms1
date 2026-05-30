import sys
import os
import ctypes
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QMenu, QDialog, QLabel, QSpinBox, 
                             QFormLayout, QHBoxLayout, QComboBox)
from PyQt6.QtCore import Qt, QPoint, QMetaObject, Q_ARG, pyqtSlot, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QConicalGradient, QFontDatabase
from pynput import mouse as pmouse

# CYBERPUNK THEME PALETTE
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"

MOUSEEVENTF_WHEEL = 0x0800

class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_scroll=3, current_font_family="Consolas", current_font_size=10):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setStyleSheet(f"""
            QDialog {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: '{current_font_family}'; font-size: {current_font_size}pt; }}
            QSpinBox, QComboBox {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;
            }}
            QPushButton {{
                background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 6px 12px; font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW};
            }}
        """)
        layout = QFormLayout(self)
        
        self.spin_scroll = QSpinBox()
        self.spin_scroll.setRange(1, 20)
        self.spin_scroll.setValue(current_scroll)
        layout.addRow("Scroll Speed:", self.spin_scroll)
        
        self.combo_font = QComboBox()
        # Curated list of clean standard fonts to prevent lag and crash
        families = ["Consolas", "Arial", "Courier New", "Segoe UI", "Georgia", "Times New Roman", "JetBrains Mono", "Cascadia Code", "Impact", "Verdana"]
        if current_font_family not in families:
            families.append(current_font_family)
        self.combo_font.addItems(families)
        idx = self.combo_font.findText(current_font_family, Qt.MatchFlag.MatchExactly)
        if idx >= 0:
            self.combo_font.setCurrentIndex(idx)
        layout.addRow("Font Family:", self.combo_font)
        
        self.spin_font_size = QSpinBox()
        self.spin_font_size.setRange(6, 24)
        self.spin_font_size.setValue(current_font_size)
        layout.addRow("Font Size:", self.spin_font_size)
        
        btn_box = QHBoxLayout()
        save = QPushButton("SAVE")
        save.clicked.connect(self.accept)
        cancel = QPushButton("CANCEL")
        cancel.clicked.connect(self.reject)
        btn_box.addWidget(save)
        btn_box.addWidget(cancel)
        layout.addRow(btn_box)

class MouseWheelGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scroll_speed = 3
        self.font_family = "Consolas"
        self.font_size = 10
        self._suppress_next_scroll = False
        self.border_offset = 0.0
        self.init_ui()
        self._start_global_wheel_listener()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_border_animation)
        self.timer.start(30)

    def _start_global_wheel_listener(self):
        def on_scroll(x, y, dx, dy):
            if self._suppress_next_scroll:
                self._suppress_next_scroll = False
                return
            QMetaObject.invokeMethod(self, "_move_to_cursor",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(int, x), Q_ARG(int, y))
        listener = pmouse.Listener(on_scroll=on_scroll)
        listener.daemon = True
        listener.start()

    def _handle_drag_press(self, event):
        self._drag_pos = event.globalPosition().toPoint()

    def _handle_drag_move(self, event):
        if self._drag_pos:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    @pyqtSlot(int, int)
    def _move_to_cursor(self, x, y):
        self.move(x - self.width() // 2, y - self.height() // 2)
        
    def apply_styles(self):
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: '{self.font_family}'; font-size: {self.font_size}pt; }}
            QPushButton {{
                background-color: {CP_DIM};
                border: 1px solid {CP_DIM};
                color: {CP_CYAN};
                font-weight: bold;
                font-size: {self.font_size - 1 if self.font_size > 7 else self.font_size}pt;
                padding: 4px;
                border-radius: 2px;
            }}
            QPushButton:hover {{
                background-color: #2a2a2a;
                border: 1px solid {CP_YELLOW};
                color: {CP_YELLOW};
            }}
            QPushButton:pressed {{
                background-color: {CP_YELLOW};
                color: black;
            }}
        """)

    def init_ui(self):
        self.setWindowTitle("Scroll Tool")
        
        # Stays on top, frameless option or just a clean floating toolbar?
        # Let's make it tool-window type so it has a thin title bar and stays on top, easy to move around.
        # Use WindowDoesNotAcceptFocus in Qt flags as well
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool | Qt.WindowType.WindowDoesNotAcceptFocus | Qt.WindowType.FramelessWindowHint)
        
        # Apply Cyberpunk styling
        self.apply_styles()
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Drag handle
        self._drag_handle = QWidget()
        self._drag_handle.setFixedHeight(10)
        self._drag_handle.setCursor(Qt.CursorShape.SizeAllCursor)
        self._drag_handle.setStyleSheet(f"background-color: {CP_DIM}; border-radius: 2px;")
        self._drag_pos = None
        self._drag_handle.mousePressEvent = self._handle_drag_press
        self._drag_handle.mouseMoveEvent = self._handle_drag_move
        layout.addWidget(self._drag_handle)
        
        # Up button
        self.btn_up = QPushButton("▲")
        self.btn_up.setToolTip("Scroll Up (Right-click for options)")
        self.btn_up.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_up.clicked.connect(self.scroll_up)
        self.btn_up.setAutoRepeat(True)
        self.btn_up.setAutoRepeatDelay(300)
        self.btn_up.setAutoRepeatInterval(60)
        self.btn_up.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.btn_up.customContextMenuRequested.connect(self.show_context_menu)
        
        # Down button
        self.btn_down = QPushButton("▼")
        self.btn_down.setToolTip("Scroll Down (Right-click for options)")
        self.btn_down.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_down.clicked.connect(self.scroll_down)
        self.btn_down.setAutoRepeat(True)
        self.btn_down.setAutoRepeatDelay(300)
        self.btn_down.setAutoRepeatInterval(60)
        self.btn_down.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.btn_down.customContextMenuRequested.connect(self.show_context_menu)
        
        # Settings button
        self.btn_settings = QPushButton("⚙")
        self.btn_settings.setToolTip("Settings")
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.clicked.connect(self.open_settings)

        
        layout.addWidget(self.btn_up)
        layout.addWidget(self.btn_down)
        layout.addWidget(self.btn_settings)
        
        # Keep window size minimal
        self.setFixedSize(44, 104)

    def showEvent(self, event):
        super().showEvent(event)
        # Apply WS_EX_NOACTIVATE so Windows doesn't activate this window on click
        hwnd = int(self.winId())
        GWL_EXSTYLE = -20
        WS_EX_NOACTIVATE = 0x08000000
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE)

        
    def scroll_up(self):
        self.perform_scroll("up")
        
    def scroll_down(self):
        self.perform_scroll("down")
        
    def perform_scroll(self, direction):
        # We need to hide the window temporarily so the mouse event hits the window underneath.
        # To avoid flickering or UI lag, we do hide, call mouse_event, and show.
        self.hide()
        # Process events to make sure window is hidden
        QApplication.processEvents()
        
        # Simulate scroll
        # 120 is one standard scroll unit.
        delta = 120 * self.scroll_speed
        if direction == "down":
            delta = -delta
            
        self._suppress_next_scroll = True
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, delta, 0)
        
        # Show window again
        self.show()
        
    def show_context_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {CP_PANEL};
                color: {CP_TEXT};
                border: 1px solid {CP_CYAN};
            }}
            QMenu::item:selected {{
                background-color: {CP_CYAN};
                color: {CP_BG};
            }}
        """)
        
        settings_action = menu.addAction("⚙ SETTINGS")
        restart_action = menu.addAction("↺ RESTART")
        exit_action = menu.addAction("❌ EXIT")
        
        # Map menu to screen coordinates
        sender = self.sender()
        global_pos = sender.mapToGlobal(pos)
        action = menu.exec(global_pos)
        
        if action == settings_action:
            self.open_settings()
        elif action == restart_action:
            self.restart_app()
        elif action == exit_action:
            QApplication.quit()
            
    def open_settings(self):
        dialog = SettingsDialog(self, self.scroll_speed, self.font_family, self.font_size)
        if dialog.exec():
            self.scroll_speed = dialog.spin_scroll.value()
            self.font_family = dialog.combo_font.currentText()
            self.font_size = dialog.spin_font_size.value()
            self.apply_styles()
            
    def restart_app(self):
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def update_border_animation(self):
        self.border_offset = (self.border_offset + 3) % 360
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        pen_width = 3
        rect = self.rect().adjusted(1, 1, -2, -2)
        
        gradient = QConicalGradient(self.width() / 2.0, self.height() / 2.0, self.border_offset)
        gradient.setColorAt(0.0, QColor("#00F0FF"))    # Cyan
        gradient.setColorAt(0.25, QColor("#FF007F"))   # Magenta/Pink
        gradient.setColorAt(0.5, QColor("#FCEE0A"))    # Yellow
        gradient.setColorAt(0.75, QColor("#00FF66"))   # Green
        gradient.setColorAt(1.0, QColor("#00F0FF"))    # Cyan
        
        pen = QPen(gradient, pen_width)
        painter.setPen(pen)
        painter.drawRect(rect)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MouseWheelGUI()
    window.show()
    sys.exit(app.exec())
