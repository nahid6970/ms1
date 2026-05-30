import sys
import os
import ctypes
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QMenu, QDialog, QLabel, QSpinBox, 
                             QFormLayout, QHBoxLayout)
from PyQt6.QtCore import Qt, QPoint, QMetaObject, Q_ARG, pyqtSlot
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
    def __init__(self, parent=None, current_scroll=3):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setStyleSheet(f"""
            QDialog {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QSpinBox {{
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
        self.spin = QSpinBox()
        self.spin.setRange(1, 20)
        self.spin.setValue(current_scroll)
        layout.addRow("Scroll Speed:", self.spin)
        
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
        self._suppress_next_scroll = False
        self.init_ui()
        self._start_global_wheel_listener()

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

    @pyqtSlot(int, int)
    def _move_to_cursor(self, x, y):
        self.move(x - self.width() // 2, y - self.height() // 2)
        
    def init_ui(self):
        self.setWindowTitle("Scroll Tool")
        
        # Stays on top, frameless option or just a clean floating toolbar?
        # Let's make it tool-window type so it has a thin title bar and stays on top, easy to move around.
        # Use WindowDoesNotAcceptFocus in Qt flags as well
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool | Qt.WindowType.WindowDoesNotAcceptFocus | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        
        # Apply Cyberpunk styling
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QPushButton {{
                background-color: {CP_DIM};
                border: 1px solid {CP_DIM};
                color: {CP_CYAN};
                font-weight: bold;
                font-size: 9pt;
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
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
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

        
        layout.addWidget(self.btn_up)
        layout.addWidget(self.btn_down)
        
        # Keep window size minimal
        self.setFixedSize(44, 60)

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
        dialog = SettingsDialog(self, self.scroll_speed)
        if dialog.exec():
            self.scroll_speed = dialog.spin.value()
            
    def restart_app(self):
        os.execv(sys.executable, [sys.executable] + sys.argv)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MouseWheelGUI()
    window.show()
    sys.exit(app.exec())
