import sys
import os
import json
import subprocess
import ctypes
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QLabel, QScrollArea, QFrame, QGraphicsDropShadowEffect, QSizePolicy, QMenu, QAction)
from PyQt5.QtCore import Qt, QSize, QPoint, QRect, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPainterPath, QColor, QFont, QIcon, QBrush, QImage, QPen, QCursor

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "gallery_config.json")

def load_images():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
    return []

def save_images(images):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(images, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

class CardWidget(QWidget):
    clicked = pyqtSignal()
    double_clicked = pyqtSignal()

    def __init__(self, path=None, is_add_btn=False, width=200, height=350, parent=None):
        super().__init__(parent)
        self.path = path
        self.is_add_btn = is_add_btn
        self.w = width
        self.h = height
        self.is_selected = False
        self.setFixedSize(self.w, self.h)
        self.setCursor(Qt.PointingHandCursor)
        
        # Cache image if it's a file
        self.pixmap = None
        if not self.is_add_btn and self.path and os.path.exists(self.path):
            self.load_image()

    def load_image(self):
        # Load and crop/resize to fill
        img = QImage(self.path)
        if img.isNull(): return
        
        # Calculate aspect ratios to crop center
        target_ratio = self.w / self.h
        img_ratio = img.width() / img.height()
        
        if img_ratio > target_ratio:
            # Image is wider than target
            new_h = self.h
            new_w = int(new_h * img_ratio)
        else:
            # Image is taller/same
            new_w = self.w
            new_h = int(new_w / img_ratio)
            
        scaled = img.scaled(new_w, new_h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        
        # Center crop
        x = (scaled.width() - self.w) // 2
        y = (scaled.height() - self.h) // 2
        self.pixmap = QPixmap.fromImage(scaled.copy(x, y, self.w, self.h))

    def set_selected(self, selected):
        if self.is_selected != selected:
            self.is_selected = selected
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Rounded Rect Path
        path = QPainterPath()
        radius = 20
        rect = QRect(0, 0, self.w, self.h)
        path.addRoundedRect(0, 0, self.w, self.h, radius, radius)
        
        # Clip
        painter.setClipPath(path)
        
        if self.is_add_btn:
            # Draw Add Button Background
            painter.fillRect(rect, QColor("#151515"))
            
            # Draw + Symbol
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#00ffff")) # Cyan Accent
            
            # Plus dims
            pw, ph = 6, 40
            cx, cy = self.w // 2, self.h // 2
            painter.drawRect(cx - pw//2, cy - ph//2, pw, ph) # Vert
            painter.drawRect(cx - ph//2, cy - pw//2, ph, pw) # Horz
            
            # Text
            painter.setPen(QColor("#888888"))
            font = QFont("Segoe UI", 10, QFont.Bold)
            painter.setFont(font)
            text_rect = QRect(0, cy + 30, self.w, 30)
            painter.drawText(text_rect, Qt.AlignCenter, "ADD IMAGE")
            
        else:
            if self.pixmap:
                painter.drawPixmap(0, 0, self.pixmap)
            else:
                painter.fillRect(rect, QColor("#220000"))
                painter.setPen(QColor("#ff5555"))
                painter.drawText(rect, Qt.AlignCenter, "ERROR")

        # Draw Border if selected (Overlay)
        painter.setClipping(False) # Disable clip to draw border 'on top' cleanly
        
        if self.is_selected:
            painter.setBrush(Qt.NoBrush)
            pen = QColor("#ffffff") # White border for selection
            pen_width = 4
            painter.setPen(QPen(pen, pen_width))
            # Adjust rect for border width
            border_rect = QRect(pen_width//2, pen_width//2, self.w - pen_width, self.h - pen_width)
            painter.drawRoundedRect(border_rect, radius, radius)

    def contextMenuEvent(self, event):
        if not self.path or self.is_add_btn: return
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555555;
                font-family: 'Segoe UI';
                font-size: 10pt;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #3d3d3d;
            }
        """)
        
        edit_action = QAction("Edit with Microsoft Photos", self)
        edit_action.triggered.connect(self.edit_image)
        menu.addAction(edit_action)
        
        wallpaper_action = QAction("Set as Wallpaper", self)
        wallpaper_action.triggered.connect(self.set_wallpaper)
        menu.addAction(wallpaper_action)
        
        menu.exec_(event.globalPos())

    def edit_image(self):
        # Try to open explicitly with Microsoft Photos via protocol handler
        try:
            # This opens the image in Microsoft Photos Viewer where edit is one click away
            subprocess.run(f'start ms-photos:viewer?fileName="{os.path.abspath(self.path)}"', shell=True)
        except Exception as e:
            print(f"Error opening photos: {e}")
            # Fallback to default edit verb
            try:
                os.startfile(self.path, 'edit')
            except:
                pass

    def set_wallpaper(self):
        try:
            full_path = os.path.abspath(self.path)
            # SPI_SETDESKWALLPAPER = 20
            # SPIF_UPDATEINIFILE = 0x01
            # SPIF_SENDCHANGE = 0x02
            ctypes.windll.user32.SystemParametersInfoW(20, 0, full_path, 3)
        except Exception as e:
            print(f"Error setting wallpaper: {e}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()


    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit()

class GalleryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_paths = load_images()
        self.cards = []
        self.current_idx = 0 # 0 is Add Button
        self.is_loading = False

        # Window Setup
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Dimensions
        screen = QApplication.primaryScreen().geometry()
        self.sw, self.sh = screen.width(), screen.height()
        
        target_h = int(self.sh * 0.45)
        # Reduced width to leave gaps on sides
        self.win_w = int(self.sw * 0.94) 
        self.win_h = target_h
        
        self.setGeometry((self.sw - self.win_w) // 2, (self.sh - self.win_h) // 2, self.win_w, self.win_h)
        
        # Card Dims (Phone Ratio 9:16)
        self.card_h = int(target_h * 0.75)
        self.card_w = int(self.card_h * (9/16))
        
        # Main Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Background Strip (Gradient + Transparency + Border)
        self.central_widget.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(45, 45, 45, 230), stop:1 rgba(15, 15, 15, 240));
            border: 1px solid rgba(150, 150, 150, 100);
            border-radius: 15px;
        """)
        
        self.layout_main = QHBoxLayout(self.central_widget)
        self.layout_main.setContentsMargins(20, 0, 20, 0)
        self.layout_main.setAlignment(Qt.AlignCenter)
        
        # Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.scroll_layout = QHBoxLayout(self.scroll_content)
        # Removed massive centering padding, just normal padding
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(20)
        self.scroll_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.scroll.setWidget(self.scroll_content)
        self.layout_main.addWidget(self.scroll)
        
        self.render_cards()
        self.update_selection()
        
    def render_cards(self):
        # Clear existing
        for i in reversed(range(self.scroll_layout.count())): 
            self.scroll_layout.itemAt(i).widget().setParent(None)
        
        self.cards = []
        
        # Image Cards
        for i, path in enumerate(self.image_paths):
            card = CardWidget(path=path, width=self.card_w, height=self.card_h)
            idx = i
            card.clicked.connect(lambda index=idx: self.set_index(index))
            card.double_clicked.connect(lambda p=path: self.launch_chrome(p))
            self.scroll_layout.addWidget(card)
            self.cards.append(card)

    def set_index(self, idx):
        if not self.cards: return
        if idx < 0: idx = 0
        if idx >= len(self.cards): idx = len(self.cards) - 1
        
        self.current_idx = idx
        self.update_selection()
        
    def update_selection(self):
        for i, card in enumerate(self.cards):
            card.set_selected(i == self.current_idx)
            
        # Scroll logic
        if not self.cards: return
        
        item_width = self.card_w + 20
        target_x = self.current_idx * item_width
        
        # Center the selected item in the view if possible
        # viewport_center = self.scroll.viewport().width() / 2
        # scroll_target = target_x - viewport_center + (self.card_w / 2)
        
        # But user didn't want it starting in middle. 
        # Standard behavior: scroll to keep item in view
        
        hbar = self.scroll.horizontalScrollBar()
        current_scroll = hbar.value()
        viewport_w = self.scroll.viewport().width()
        
        # Ensure visible
        card_start = target_x
        card_end = target_x + self.card_w
        
        # Simple Logic: If card is overlapping left edge, scroll to it.
        # If card is overlapping right edge, scroll to it.
        
        target_val = current_scroll
        
        if card_start < current_scroll:
            target_val = card_start
        elif card_end > current_scroll + viewport_w:
            target_val = card_end - viewport_w
        
        # Also handle "Center focus" style if desired, but user complained about "starting from middle".
        # "Starting from middle" likely meant the empty padding.
        # I will enforce centering ONLY if it doesn't create empty space at start? 
        # For now, let's stick to "ensure visible" minimum scrolling which is less jarring.
        # Actually for a carousel, centering the active item is nicer.
        # Let's try centering but clamp to bounds.
        
        center_target = target_x - (viewport_w / 2) + (self.card_w / 2)
        target_val = max(0, min(center_target, hbar.maximum()))

        self.anim = QPropertyAnimation(hbar, b"value")
        self.anim.setDuration(300)
        self.anim.setStartValue(current_scroll)
        self.anim.setEndValue(int(target_val))
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

    def keyPressEvent(self, event):
        if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_A:
            self.add_images_dialog()
            return

        if event.key() == Qt.Key_Left:
            self.set_index(self.current_idx - 1)
        elif event.key() == Qt.Key_Right:
            self.set_index(self.current_idx + 1)
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.activate_current()
        elif event.key() == Qt.Key_Escape:
            self.close()
            
    def activate_current(self):
        if 0 <= self.current_idx < len(self.image_paths):
            path = self.image_paths[self.current_idx]
            self.launch_chrome(path)
            
    def add_images_dialog(self):
        from PyQt5.QtWidgets import QFileDialog
        files, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if files:
            new_paths = [f for f in files if f not in self.image_paths]
            self.image_paths.extend(new_paths)
            save_images(self.image_paths)
            self.render_cards()
            # Select first new image
            self.set_index(len(self.cards) - len(new_paths))

    def launch_chrome(self, path):
        try:
            # Use start commmand for windows for default browser or chrome specifically if path known
            # 'start chrome "path"'
            subprocess.run(f'start chrome "{path}"', shell=True)
            self.close() # Close launcher on launch?
        except Exception as e:
            print(f"Error launching: {e}")

    def focusOutEvent(self, event):
        # Close on focus loss (launcher behavior)
        if not self.isActiveWindow():
             self.close()
        super().focusOutEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GalleryWindow()
    window.show()
    # Force focus
    window.activateWindow()
    window.raise_()
    sys.exit(app.exec_())
