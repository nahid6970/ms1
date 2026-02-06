import sys
import os
import json
import subprocess
import requests
import hashlib
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QLineEdit, QComboBox, QScrollArea, 
                             QGridLayout, QFrame, QCheckBox, QStackedWidget, QMenu, 
                             QInputDialog, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QRunnable, QThreadPool, pyqtSlot, QObject
from PyQt6.QtGui import QPixmap, QAction

# GREEN & BLUE TECH THEME PALETTE
CP_BG = "#050505"
CP_PANEL = "#0D0D0D"
CP_GREEN = "#00FF41"        
CP_BLUE = "#00AEEF"         
CP_DIM = "#222222"          
CP_TEXT = "#E0E0E0"
CP_SUBTEXT = "#808080"
CP_RED = "#FF003C"

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.json")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
ROOT_SHOWS_FOLDER = r"D:\Downloads\@Sonarr"
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cyber_tv_cache")

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

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

def load_settings():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {"sort_order": "Recently Added"}

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")

class ImageDownloadSignals(QObject):
    finished = pyqtSignal(str, str)
    error = pyqtSignal(str)

class ImageDownloadWorker(QRunnable):
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.signals = ImageDownloadSignals()

    @pyqtSlot()
    def run(self):
        if not self.url or not self.url.startswith("http"): return
        url_hash = hashlib.md5(self.url.encode()).hexdigest()
        ext = self.url.split('.')[-1].split('?')[0] if '.' in self.url else 'jpg'
        if len(ext) > 4: ext = 'jpg'
        local_path = os.path.join(CACHE_DIR, f"{url_hash}.{ext}")
        if os.path.exists(local_path):
            self.signals.finished.emit(self.url, local_path)
            return
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(max_retries=3)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            response = session.get(self.url, headers=headers, timeout=30)
            if response.status_code == 200:
                with open(local_path, 'wb') as f: f.write(response.content)
                self.signals.finished.emit(self.url, local_path)
            else: self.signals.error.emit(f"Status {response.status_code}")
        except Exception as e: self.signals.error.emit(str(e))

class ScannerThread(QThread):
    finished = pyqtSignal(list)
    def run(self):
        shows = load_data()
        updated = False
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
                                    new_ep = {'id': len(show.get('episodes', [])) + 1, 'title': name, 'watched': False, 'added_date': datetime.now().isoformat()}
                                    if 'episodes' not in show: show['episodes'] = []
                                    show['episodes'].insert(0, new_ep)
                                    existing_titles.add(name)
                                    updated = True
                                    new_episodes_found = True
                    if new_episodes_found and show.get('episode_sort_type') == 'alphabetical':
                        order = show.get('episode_sort_order', 'asc')
                        show['episodes'].sort(key=lambda x: x['title'].lower(), reverse=(order == 'desc'))
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
                            new_show = {'id': max([s['id'] for s in shows], default=0) + 1, 'title': item, 'year': '', 'cover_image': '', 'directory_path': item_path, 'rating': None, 'status': 'Continuing', 'episodes': []}
                            for root, _, files in os.walk(item_path):
                                for f in files:
                                    name, ext = os.path.splitext(f)
                                    if ext.lower() in ['.mp4', '.mkv', '.avi', '.mov', '.webm']:
                                        new_show['episodes'].append({'id': len(new_show['episodes']) + 1, 'title': name, 'watched': False, 'added_date': datetime.now().isoformat()})
                            new_show['episodes'].reverse()
                            shows.append(new_show)
                            updated = True
            except Exception as e: print(f"Scanner error: {e}")
        if updated: save_data(shows)
        self.finished.emit(shows)

class EpisodeItem(QFrame):
    toggled = pyqtSignal()
    deleteRequested = pyqtSignal(int)
    def __init__(self, show, episode, parent=None):
        super().__init__(parent)
        self.show_data = show
        self.episode = episode
        self.setup_ui()
    def setup_ui(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"QFrame {{ background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; margin: 2px; padding: 5px; }} QFrame:hover {{ border: 1px solid {CP_GREEN}; }}")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        title_label = QLabel(self.episode['title'])
        title_label.setStyleSheet(f"color: {CP_TEXT}; font-weight: bold; border: none;")
        title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout.addWidget(title_label, 1)
        
        self.watched_cb = QCheckBox("Watched")
        self.watched_cb.setChecked(self.episode.get('watched', False))
        self.watched_cb.stateChanged.connect(self.toggle_watched)
        layout.addWidget(self.watched_cb)

        del_btn = QPushButton("DEL")
        del_btn.setFixedWidth(40)
        del_btn.setStyleSheet(f"QPushButton {{ outline: none; background-color: {CP_DIM}; color: {CP_SUBTEXT}; border: none; padding: 2px; }} QPushButton:hover {{ background-color: {CP_RED}; color: white; }}")
        del_btn.clicked.connect(lambda: self.deleteRequested.emit(self.episode['id']))
        layout.addWidget(del_btn)

    def toggle_watched(self, state):
        self.episode['watched'] = (state == 2)
        self.toggled.emit()

class ShowCard(QPushButton):
    deleteRequested = pyqtSignal(int)
    openFolderRequested = pyqtSignal(dict)
    
    def __init__(self, show, onClick, parent=None):
        super().__init__(parent)
        self.show_data = show
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(lambda: onClick(self.show_data))
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)
        self.setup_ui()
        if self.show_data.get('cover_image'):
            worker = ImageDownloadWorker(self.show_data['cover_image'])
            worker.signals.finished.connect(self.on_image_ready)
            QThreadPool.globalInstance().start(worker)
            
    def setup_ui(self):
        self.setFixedSize(180, 280)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        self.poster = QLabel()
        self.poster.setFixedSize(170, 180)
        self.poster.setStyleSheet(f"background-color: #000; border: 1px solid {CP_DIM};")
        self.poster.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.poster.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.layout.addWidget(self.poster)
        info_widget = QWidget()
        info_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)
        title_label = QLabel(self.show_data['title'])
        title_label.setStyleSheet(f"color: {CP_TEXT}; font-weight: bold; background: transparent; border: none;")
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        info_layout.addWidget(title_label)
        watched_count = sum(1 for e in self.show_data.get('episodes', []) if e.get('watched'))
        total_count = len(self.show_data.get('episodes', []))
        latest_str = "No episodes"
        dates = []
        for e in self.show_data.get('episodes', []):
            if e.get('added_date'):
                try: dates.append(datetime.fromisoformat(e['added_date']))
                except: pass
        if dates: latest_str = max(dates).strftime('%d %b, %Y')
        stats_label = QLabel(f"{watched_count}/{total_count} EPS")
        stats_label.setStyleSheet(f"color: {CP_SUBTEXT}; font-size: 8pt; background: transparent; border: none;")
        stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        info_layout.addWidget(stats_label)
        date_label = QLabel(latest_str)
        date_label.setStyleSheet(f"color: {CP_BLUE}; font-size: 7pt; font-style: italic; background: transparent; border: none;")
        date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        date_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        info_layout.addWidget(date_label)
        self.layout.addWidget(info_widget)
        self.update_style()
        
    def show_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet(f"QMenu {{ background-color: {CP_PANEL}; border: 1px solid {CP_BLUE}; color: {CP_TEXT}; }} QMenu::item:selected {{ background-color: {CP_BLUE}; color: black; }}")
        open_action = QAction("Open Folder", self)
        open_action.triggered.connect(lambda: self.openFolderRequested.emit(self.show_data))
        delete_action = QAction("Delete Show", self)
        delete_action.triggered.connect(lambda: self.deleteRequested.emit(self.show_data['id']))
        menu.addAction(open_action)
        menu.addSeparator()
        menu.addAction(delete_action)
        menu.exec(self.mapToGlobal(pos))
        
    def on_image_ready(self, url, path):
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            self.poster.setPixmap(pixmap.scaled(self.poster.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
            
    def update_style(self):
        episodes = self.show_data.get('episodes', [])
        all_watched = len(episodes) > 0 and all(e.get('watched') for e in episodes)
        default_border = CP_GREEN if all_watched else CP_DIM
        self.setStyleSheet(f"""
            QPushButton {{ 
                outline: none;
                background-color: {CP_PANEL}; 
                border: 2px solid {default_border}; 
                border-radius: 4px; 
            }} 
            QPushButton:hover {{ 
                border: 2px solid {CP_BLUE}; 
                background-color: #111; 
            }}
        """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TV SHOW TRACKER // TECH_OS")
        self.resize(1100, 850)
        QThreadPool.globalInstance().setMaxThreadCount(8)
        self.shows = load_data()
        self.settings = load_settings()
        self.current_show = None
        self.setup_ui()
        saved_sort = self.settings.get("sort_order", "Recently Added")
        index = self.sort.findText(saved_sort)
        if index >= 0: self.sort.setCurrentIndex(index)
        self.refresh_grid()
        self.start_scan()
        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(self.start_scan)
        self.scan_timer.start(3600000)
        
    def setup_ui(self):
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QLineEdit {{ background-color: {CP_PANEL}; color: {CP_GREEN}; border: 1px solid {CP_DIM}; padding: 6px; }}
            QPushButton {{ 
                outline: none;
                background-color: {CP_DIM}; 
                border: 1px solid {CP_DIM}; 
                color: white; 
                padding: 6px 12px; 
                font-weight: bold; 
            }}
            QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_GREEN}; color: {CP_GREEN}; }}
            QComboBox {{ background: {CP_PANEL}; color: {CP_GREEN}; border: 1px solid {CP_DIM}; padding: 4px; }}
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{ border: none; background: {CP_BG}; width: 12px; }}
            QScrollBar::handle:vertical {{ background: {CP_BLUE}; min-height: 20px; border: 1px solid {CP_BLUE}; }}
            QScrollBar:horizontal {{ border: none; background: {CP_BG}; height: 12px; }}
            QScrollBar::handle:horizontal {{ background: {CP_BLUE}; min-width: 20px; border: 1px solid {CP_BLUE}; }}
            QCheckBox::indicator {{ width: 14px; height: 14px; border: 1px solid {CP_DIM}; background: {CP_PANEL}; }}
            QCheckBox::indicator:checked {{ background: {CP_GREEN}; border: 1px solid {CP_GREEN}; }}
        """)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.list_view = QWidget()
        l_layout = QVBoxLayout(self.list_view)
        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("SEARCH_SHOWS...")
        self.search.textChanged.connect(self.refresh_grid)
        toolbar.addWidget(self.search)
        self.sort = QComboBox()
        self.sort.addItems(["Title", "Recently Added", "Progress", "Last Updated"])
        self.sort.currentIndexChanged.connect(self.on_sort_changed)
        toolbar.addWidget(self.sort)
        scan_btn = QPushButton("SCAN")
        scan_btn.clicked.connect(self.start_scan)
        toolbar.addWidget(scan_btn)
        restart_btn = QPushButton("RESTART")
        restart_btn.setStyleSheet(f"color: {CP_BLUE}; border-color: {CP_BLUE};")
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
        
        self.detail_view = QWidget()
        d_layout = QVBoxLayout(self.detail_view)
        header = QHBoxLayout()
        back_btn = QPushButton("<< BACK")
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        header.addWidget(back_btn)
        self.d_title = QLabel("TITLE")
        self.d_title.setStyleSheet(f"font-size: 16pt; font-weight: bold; color: {CP_GREEN};")
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
        
    def on_sort_changed(self):
        self.settings["sort_order"] = self.sort.currentText()
        save_settings(self.settings)
        self.refresh_grid()
        
    def refresh_grid(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        q = self.search.text().lower()
        filtered = [s for s in self.shows if q in s['title'].lower()]
        s_type = self.sort.currentText()
        if s_type == "Title": filtered.sort(key=lambda x: x['title'].lower())
        elif s_type == "Recently Added": filtered.sort(key=lambda x: x['id'], reverse=True)
        elif s_type == "Progress": filtered.sort(key=lambda s: sum(1 for e in s.get('episodes', []) if e.get('watched'))/max(1, len(s.get('episodes', []))), reverse=True)
        elif s_type == "Last Updated":
            def get_last_date(s):
                dates = []
                for e in s.get('episodes', []):
                    if e.get('added_date'):
                        try: dates.append(datetime.fromisoformat(e['added_date']))
                        except: pass
                return max(dates) if dates else datetime.min
            filtered.sort(key=get_last_date, reverse=True)
            
        cols = 5
        for i, show in enumerate(filtered):
            card = ShowCard(show, self.open_detail)
            card.deleteRequested.connect(self.delete_show)
            card.openFolderRequested.connect(self.open_folder_from_card)
            self.grid.addWidget(card, i // cols, i % cols)
            
    def open_detail(self, show):
        self.current_show = show
        self.d_title.setText(show['title'])
        self.refresh_episodes()
        self.stack.setCurrentIndex(1)
        
    def refresh_episodes(self):
        while self.e_layout.count():
            item = self.e_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        if self.current_show:
            for ep in self.current_show.get('episodes', []):
                item = EpisodeItem(self.current_show, ep)
                item.toggled.connect(self.save_and_sync)
                item.deleteRequested.connect(self.delete_episode)
                self.e_layout.addWidget(item)
                
    def delete_show(self, show_id):
        confirm = QMessageBox.question(self, "Delete Show", "Are you sure you want to delete this show from library?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.shows = [s for s in self.shows if s['id'] != show_id]
            save_data(self.shows)
            self.refresh_grid()
            
    def delete_episode(self, episode_id):
        if self.current_show:
            self.current_show['episodes'] = [e for e in self.current_show['episodes'] if e['id'] != episode_id]
            save_data(self.shows)
            self.refresh_episodes()
            
    def save_and_sync(self): 
        save_data(self.shows)
        
    def open_show_folder(self):
        if self.current_show and self.current_show.get('directory_path'):
            p = self.current_show['directory_path']
            if os.path.exists(p):
                if sys.platform == 'win32': os.startfile(p)
                else: subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', p])
                
    def open_folder_from_card(self, show_data):
        p = show_data.get('directory_path')
        if p and os.path.exists(p):
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
