import sys
import os
import json
import subprocess
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QLineEdit, QGroupBox, QScrollArea, 
                             QGridLayout, QFrame, QComboBox, QDialog, QFormLayout, 
                             QListWidget, QListWidgetItem, QCheckBox, QStackedWidget)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap

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

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")
ROOT_SHOWS_FOLDER = r"D:\Downloads\@Sonarr"

def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")
    return []

def save_data(data):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving data: {e}")

class ScannerThread(QThread):
    finished = pyqtSignal(list)
    
    def run(self):
        shows = load_data()
        updated = False
        
        # Scan existing shows for new episodes
        for show in shows:
            if 'directory_path' in show and show['directory_path']:
                dir_path = show['directory_path']
                if os.path.isdir(dir_path):
                    existing_titles = {e['title'] for e in show.get('episodes', [])}
                    new_episodes_found = False
                    
                    for root, _, files in os.walk(dir_path):
                        for filename in files:
                            name, ext = os.path.splitext(filename)
                            if ext.lower() in ['.mp4', '.mkv', '.avi', '.mov', '.webm']:
                                if name not in existing_titles:
                                    new_ep = {
                                        'id': len(show.get('episodes', [])) + 1,
                                        'title': name,
                                        'watched': False,
                                        'added_date': datetime.now().isoformat(),
                                        'notify': 'unseen'
                                    }
                                    if 'episodes' not in show:
                                        show['episodes'] = []
                                    show['episodes'].insert(0, new_ep)
                                    existing_titles.add(name)
                                    updated = True
                                    new_episodes_found = True
                    
                    if new_episodes_found and show.get('episode_sort_type') == 'alphabetical':
                        order = show.get('episode_sort_order', 'asc')
                        show['episodes'].sort(key=lambda x: x['title'].lower(), reverse=(order == 'desc'))
        
        # Scan for missing shows
        if os.path.exists(ROOT_SHOWS_FOLDER):
            existing_paths = {s.get('directory_path', '').lower() for s in shows if s.get('directory_path')}
            try:
                for item in os.listdir(ROOT_SHOWS_FOLDER):
                    item_path = os.path.join(ROOT_SHOWS_FOLDER, item)
                    if os.path.isdir(item_path) and item_path.lower() not in existing_paths:
                        has_videos = False
                        for _, _, files in os.walk(item_path):
                            if any(os.path.splitext(f)[1].lower() in ['.mp4', '.mkv', '.avi', '.mov', '.webm'] for f in files):
                                has_videos = True
                                break
                        
                        if has_videos:
                            new_id = max([s['id'] for s in shows], default=0) + 1
                            new_show = {
                                'id': new_id,
                                'title': item,
                                'year': '',
                                'cover_image': '',
                                'directory_path': item_path,
                                'rating': None,
                                'status': 'Continuing',
                                'episodes': []
                            }
                            # Scan episodes for new show
                            for root, _, files in os.walk(item_path):
                                for f in files:
                                    name, ext = os.path.splitext(f)
                                    if ext.lower() in ['.mp4', '.mkv', '.avi', '.mov', '.webm']:
                                        new_show['episodes'].append({
                                            'id': len(new_show['episodes']) + 1,
                                            'title': name,
                                            'watched': False,
                                            'added_date': datetime.now().isoformat(),
                                            'notify': 'unseen'
                                        })
                            new_show['episodes'].reverse()
                            shows.append(new_show)
                            updated = True
            except Exception as e:
                print(f"Scanner error: {e}")
        
        if updated:
            save_data(shows)
        
        self.finished.emit(shows)

class EpisodeItem(QFrame):
    toggled = pyqtSignal()
    
    def __init__(self, show, episode, parent=None):
        super().__init__(parent)
        self.show_data = show
        self.episode = episode
        self.setup_ui()
        
    def setup_ui(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CP_PANEL};
                border: 1px solid {CP_DIM};
                margin: 2px;
                padding: 5px;
            }}
            QFrame:hover {{
                border: 1px solid {CP_CYAN};
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Title
        title_label = QLabel(self.episode['title'])
        title_label.setStyleSheet(f"color: {CP_TEXT}; font-weight: bold; border: none;")
        layout.addWidget(title_label, 1)
        
        # Unseen Notify
        self.notify_btn = QPushButton("NEW" if self.episode.get('notify') == 'unseen' else "SEEN")
        notify_color = CP_RED if self.episode.get('notify') == 'unseen' else CP_DIM
        self.notify_btn.setFixedWidth(60)
        self.notify_btn.setStyleSheet(f"QPushButton {{ background-color: {notify_color}; color: black; font-weight: bold; font-size: 8pt; border: none; }}")
        self.notify_btn.clicked.connect(self.toggle_notify)
        layout.addWidget(self.notify_btn)
        
        # Watched Checkbox
        self.watched_cb = QCheckBox("Watched")
        self.watched_cb.setChecked(self.episode.get('watched', False))
        self.watched_cb.stateChanged.connect(self.toggle_watched)
        layout.addWidget(self.watched_cb)

    def toggle_notify(self):
        current = self.episode.get('notify', 'unseen')
        self.episode['notify'] = 'seen' if current == 'unseen' else 'unseen'
        self.notify_btn.setText("NEW" if self.episode['notify'] == 'unseen' else "SEEN")
        notify_color = CP_RED if self.episode['notify'] == 'unseen' else CP_DIM
        self.notify_btn.setStyleSheet(f"background-color: {notify_color}; color: black; font-weight: bold; font-size: 8pt; border: none;")
        self.toggled.emit()

    def toggle_watched(self, state):
        self.episode['watched'] = (state == 2)
        self.toggled.emit()

class ShowCard(QPushButton):
    def __init__(self, show, onClick, parent=None):
        super().__init__(parent)
        self.show_data = show
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(lambda: onClick(show))
        self.setup_ui()
        
    def setup_ui(self):
        unseen_count = sum(1 for e in self.show_data.get('episodes', []) if e.get('notify') == 'unseen')
        watched_count = sum(1 for e in self.show_data.get('episodes', []) if e.get('watched'))
        total_count = len(self.show_data.get('episodes', []))
        
        layout = QVBoxLayout(self)
        title_label = QLabel(self.show_data['title'])
        title_label.setStyleSheet(f"color: {CP_YELLOW}; font-size: 11pt; font-weight: bold; border: none; background: transparent;")
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        stats_label = QLabel(f"{watched_count}/{total_count} EPS")
        stats_label.setStyleSheet(f"color: {CP_SUBTEXT}; font-size: 9pt; border: none; background: transparent;")
        stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(stats_label)
        
        if unseen_count > 0:
            unseen_label = QLabel(f"[{unseen_count} NEW]")
            unseen_label.setStyleSheet(f"color: {CP_RED}; font-weight: bold; font-size: 8pt; border: none; background: transparent;")
            unseen_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(unseen_label)
        
        self.setFixedSize(180, 110)
        self.update_style()

    def update_style(self):
        unseen = any(e.get('notify') == 'unseen' for e in self.show_data.get('episodes', []))
        border = CP_RED if unseen else CP_DIM
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {CP_PANEL};
                border: 2px solid {border};
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #1a1a1a;
                border: 2px solid {CP_CYAN};
            }}
        """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TV SHOW TRACKER // CYBERPUNK_OS")
        self.resize(1100, 750)
        self.shows = load_data()
        self.current_show = None
        
        self.setup_ui()
        self.refresh_grid()
        self.start_scan()
        
        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(self.start_scan)
        self.scan_timer.start(3600000)

    def setup_ui(self):
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QLineEdit {{ background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 6px; }}
            QLineEdit:focus {{ border: 1px solid {CP_CYAN}; }}
            QPushButton {{ background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 6px 12px; font-weight: bold; }}
            QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
            QPushButton:pressed {{ background-color: {CP_YELLOW}; color: black; }}
            QComboBox {{ background: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px; }}
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{ border: none; background: {CP_BG}; width: 10px; margin: 0px; }}
            QScrollBar::handle:vertical {{ background: {CP_DIM}; min-height: 20px; }}
            QScrollBar::handle:vertical:hover {{ background: {CP_CYAN}; }}
            QCheckBox {{ spacing: 8px; color: {CP_TEXT}; }}
            QCheckBox::indicator {{ width: 14px; height: 14px; border: 1px solid {CP_DIM}; background: {CP_PANEL}; }}
            QCheckBox::indicator:checked {{ background: {CP_YELLOW}; border-color: {CP_YELLOW}; }}
        """)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # --- LIST VIEW ---
        self.list_view = QWidget()
        l_layout = QVBoxLayout(self.list_view)
        
        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("SEARCH_SHOWS...")
        self.search.textChanged.connect(self.refresh_grid)
        toolbar.addWidget(self.search)
        
        self.sort = QComboBox()
        self.sort.addItems(["Title", "Recently Added", "Unseen First"])
        self.sort.currentIndexChanged.connect(self.refresh_grid)
        toolbar.addWidget(self.sort)
        
        scan_btn = QPushButton("SCAN")
        scan_btn.clicked.connect(self.start_scan)
        toolbar.addWidget(scan_btn)
        
        restart_btn = QPushButton("RESTART")
        restart_btn.setStyleSheet(f"color: {CP_ORANGE}; border-color: {CP_ORANGE};")
        restart_btn.clicked.connect(self.restart_app)
        toolbar.addWidget(restart_btn)
        
        l_layout.addLayout(toolbar)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.grid_container = QWidget()
        self.grid = QGridLayout(self.grid_container)
        self.grid.setSpacing(15)
        self.scroll.setWidget(self.grid_container)
        l_layout.addWidget(self.scroll)
        
        self.stack.addWidget(self.list_view)

        # --- DETAIL VIEW ---
        self.detail_view = QWidget()
        d_layout = QVBoxLayout(self.detail_view)
        
        header = QHBoxLayout()
        back_btn = QPushButton("<< BACK")
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        header.addWidget(back_btn)
        
        self.d_title = QLabel("TITLE")
        self.d_title.setStyleSheet(f"font-size: 16pt; font-weight: bold; color: {CP_YELLOW};")
        header.addWidget(self.d_title, 1)
        
        folder_btn = QPushButton("OPEN FOLDER")
        folder_btn.clicked.connect(self.open_show_folder)
        header.addWidget(folder_btn)
        
        d_layout.addLayout(header)
        
        self.e_scroll = QScrollArea()
        self.e_scroll.setWidgetResizable(True)
        self.e_container = QWidget()
        self.e_layout = QVBoxLayout(self.e_container)
        self.e_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.e_scroll.setWidget(self.e_container)
        d_layout.addWidget(self.e_scroll)
        
        self.stack.addWidget(self.detail_view)

    def refresh_grid(self):
        while self.grid.count():
            w = self.grid.takeAt(0).widget()
            if w: w.deleteLater()
            
        q = self.search.text().lower()
        s_type = self.sort.currentText()
        filtered = [s for s in self.shows if q in s['title'].lower()]
        
        if s_type == "Title": filtered.sort(key=lambda x: x['title'].lower())
        elif s_type == "Recently Added": filtered.sort(key=lambda x: x['id'], reverse=True)
        elif s_type == "Unseen First":
            filtered.sort(key=lambda s: sum(1 for e in s.get('episodes', []) if e.get('notify') == 'unseen'), reverse=True)
            
        cols = 5
        for i, show in enumerate(filtered):
            card = ShowCard(show, self.open_detail)
            self.grid.addWidget(card, i // cols, i % cols)
            
    def open_detail(self, show):
        self.current_show = show
        self.d_title.setText(show['title'])
        self.refresh_episodes()
        self.stack.setCurrentIndex(1)
        
    def refresh_episodes(self):
        while self.e_layout.count():
            w = self.e_layout.takeAt(0).widget()
            if w: w.deleteLater()
        if self.current_show:
            for ep in self.current_show.get('episodes', []):
                item = EpisodeItem(self.current_show, ep)
                item.toggled.connect(self.save_and_sync)
                self.e_layout.addWidget(item)

    def save_and_sync(self):
        save_data(self.shows)
        
    def open_show_folder(self):
        if self.current_show and self.current_show.get('directory_path'):
            p = self.current_show['directory_path']
            if os.path.exists(p):
                if sys.platform == 'win32': os.startfile(p)
                else: subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', p])

    def start_scan(self):
        self.scanner = ScannerThread()
        self.scanner.finished.connect(self.on_scan_finished)
        self.scanner.start()
        
    def on_scan_finished(self, updated):
        self.shows = updated
        self.refresh_grid()
        if self.current_show:
            self.current_show = next((s for s in self.shows if s['id'] == self.current_show['id']), None)
            if self.current_show: self.refresh_episodes()

    def restart_app(self):
        save_data(self.shows)
        os.execv(sys.executable, [sys.executable] + sys.argv)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
