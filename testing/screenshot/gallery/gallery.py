import sys
import os
import json
import subprocess
import ctypes
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QLabel, QScrollArea, QFrame, QGraphicsDropShadowEffect, QSizePolicy, QMenu, QAction)
from PyQt5.QtCore import Qt, QSize, QPoint, QRect, QPropertyAnimation, QEasingCurve, pyqtSignal, QTimer
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
    delete_triggered = pyqtSignal()

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
        
        # Prevent main window from closing when menu opens
        main_win = self.window()
        if hasattr(main_win, 'block_close'):
            main_win.block_close = True
        
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
        
        menu.addSeparator()
        
        delete_action = QAction("Delete from Gallery", self)
        delete_action.triggered.connect(self.delete_triggered.emit)
        menu.addAction(delete_action)
        
        menu.exec_(event.globalPos())
        
        if hasattr(main_win, 'block_close'):
            main_win.block_close = False
            main_win.activateWindow()

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
        self.block_close = False
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

        # Focus Check Timer (Replaces unreliable focusOutEvent)
        self.focus_timer = QTimer(self)
        self.focus_timer.timeout.connect(self.check_focus)
        self.focus_timer.start(100)
    
    def check_focus(self):
        if self.block_close: return
        # If we are not active, close.
        if not self.isActiveWindow():
            self.close()

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
            card.delete_triggered.connect(lambda p=path: self.delete_image(p))
            self.scroll_layout.addWidget(card)
            self.cards.append(card)

    def delete_image(self, path):
        if path in self.image_paths:
            idx = self.image_paths.index(path)
            self.image_paths.remove(path)
            save_images(self.image_paths)
            self.render_cards()
            
            # Smart Selection: try to stay at current index or go back one
            if self.current_idx >= len(self.cards):
                # We were at the last element which is now gone (or list is shorter)
                # But self.cards is just rebuilt. So len(self.cards) matches current state.
                # If we were at 5 and now there are 5 (0-4), we go to 4.
                self.current_idx = max(0, len(self.cards) - 1)
            # If we were at 3 and now there are 4 (0-3), 3 is still valid, so we stay.
            
            self.set_index(self.current_idx)

    def set_index(self, idx):
        if not self.cards: 
            self.current_idx = -1
            return
        if idx < 0: idx = 0
        if idx >= len(self.cards): idx = len(self.cards) - 1
        
        self.current_idx = idx
        self.update_selection()
        
    def update_selection(self):
        for i, card in enumerate(self.cards):
            card.set_selected(i == self.current_idx)
            
        if not self.cards: return
        
        item_width = self.card_w + 20
        target_x = self.current_idx * item_width
        
        hbar = self.scroll.horizontalScrollBar()
        current_scroll = hbar.value()
        viewport_w = self.scroll.viewport().width()
        
        card_start = target_x
        card_end = target_x + self.card_w
        
        target_val = current_scroll
        
        if card_start < current_scroll:
            target_val = card_start
        elif card_end > current_scroll + viewport_w:
            target_val = card_end - viewport_w
        else:
            # If visible, don't auto scroll unless it's way off (user might have scrolled manually)
            pass

        self.anim = QPropertyAnimation(hbar, b"value")
        self.anim.setDuration(300)
        self.anim.setStartValue(current_scroll)
        self.anim.setEndValue(int(target_val))
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

    def keyPressEvent(self, event):
        if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_A:
            self.show_add_menu()
            return
            
        if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_D:
            if 0 <= self.current_idx < len(self.image_paths):
                self.delete_image(self.image_paths[self.current_idx])
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
            
    def show_add_menu(self):
        # Prevent main window from closing when menu opens
        if hasattr(self, 'block_close'):
            self.block_close = True
            
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
                padding: 10px 20px;
            }
            QMenu::item:selected {
                background-color: #3d3d3d;
            }
        """)
        
        file_act = QAction("Add Files...", self)
        file_act.triggered.connect(self.add_files_dialog)
        menu.addAction(file_act)
        
        folder_act = QAction("Add Folder...", self)
        folder_act.triggered.connect(self.add_folder_dialog)
        menu.addAction(folder_act)
        
        menu.exec_(QCursor.pos())
        
        if hasattr(self, 'block_close'):
            self.block_close = False
            self.activateWindow()

    def add_files_dialog(self):
        from PyQt5.QtWidgets import QFileDialog
        self.block_close = True
        files, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp *.gif)")
        self.block_close = False
        self.activateWindow()
        
        if files:
            new_paths = [f for f in files if f not in self.image_paths]
            self.image_paths.extend(new_paths)
            save_images(self.image_paths)
            self.render_cards()
            # Select first new image
            self.set_index(len(self.cards) - len(new_paths))

    def add_folder_dialog(self):
        from PyQt5.QtWidgets import QFileDialog
        self.block_close = True
        folder = QFileDialog.getExistingDirectory(self, "Select Folder Containing Images")
        self.block_close = False
        self.activateWindow()
        
        if folder:
            image_exts = {'.png', '.jpg', '.jpeg', '.bmp', '.webp', '.gif'}
            new_paths = []
            try:
                # Scan top level files in folder
                for f in os.listdir(folder):
                    ext = os.path.splitext(f)[1].lower()
                    if ext in image_exts:
                        full_path = os.path.join(folder, f).replace("\\", "/")
                        if full_path not in self.image_paths:
                            new_paths.append(full_path)
            except Exception as e:
                print(f"Error scanning folder: {e}")
                
            if new_paths:
                self.image_paths.extend(new_paths)
                save_images(self.image_paths)
                self.render_cards()
                self.set_index(len(self.cards) - len(new_paths))

    def launch_chrome(self, path):
        try:
            # Use start commmand for windows for default browser or chrome specifically if path known
            # 'start chrome "path"'
            subprocess.run(f'start chrome "{path}"', shell=True)
            self.close() # Close launcher on launch?
        except Exception as e:
            print(f"Error launching: {e}")
            
    def wheelEvent(self, event):
        # Allow default vertical scrolling if shift is pressed? 
        # But we only have horizontal.
        # Native QScrollArea wheel event scrolls vertically.
        # We manually handle it to convert to horizontal + speed.
        
        delta = event.angleDelta().y()
        if delta == 0:
            delta = event.angleDelta().x()
            
        if delta != 0:
            hbar = self.scroll.horizontalScrollBar()
            # "Fast" scroll: multiply standard step 
            # Standard click is often 120. 
            step = 60 # Amount to scroll per tick
            multiplier = 3 # Speed multiplier
            
            scroll_amount = int(-1 * (delta / 120) * step * multiplier)
            hbar.setValue(hbar.value() + scroll_amount)
            event.accept()

    # focusOutEvent removed in favor of QTimer check

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GalleryWindow()
    window.show()
    # Force focus
    window.activateWindow()
    window.raise_()
    sys.exit(app.exec_())
