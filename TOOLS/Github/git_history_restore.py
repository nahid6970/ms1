import sys
import os
import subprocess
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog, QMessageBox, QAbstractItemView, QStyledItemDelegate, QStyle,
    QTreeView, QDialog, QFileIconProvider, QInputDialog, QTextEdit, QSplitter
)
from PyQt6.QtCore import Qt, QSize, QRect, QDir, QFileInfo, QThread, pyqtSignal, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QCursor, QPainter, QFileSystemModel, QIcon, QPixmap

# --- THEME CONSTANTS (from THEME_GUIDE.md) ---
CP_BG = "#050505"           # Main Window Background
CP_PANEL = "#111111"        # Panel/Input Background
CP_YELLOW = "#FCEE0A"       # Accent: Yellow
CP_CYAN = "#00F0FF"         # Accent: Cyan
CP_RED = "#FF003C"          # Accent: Red
CP_GREEN = "#00ff21"        # Accent: Green
CP_DIM = "#3a3a3a"          # Dimmed/Borders/Inactive
CP_TEXT = "#E0E0E0"         # Primary Text

# --- CUSTOM ICON PROVIDER FOR FOLDERS ---
class CyberIconProvider(QFileIconProvider):
    def __init__(self):
        super().__init__()
        
    def icon(self, type_or_info):
        # Always return folder icon for directories
        if isinstance(type_or_info, QFileInfo):
            if type_or_info.isDir():
                return super().icon(QFileIconProvider.IconType.Folder)
        elif type_or_info == QFileIconProvider.IconType.Folder:
            return super().icon(QFileIconProvider.IconType.Folder)
        return super().icon(type_or_info)

# --- CUSTOM DELEGATE FOR ROW HOVER & COLOR PERSISTENCE ---
class CyberDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hovered_row = -1

    def paint(self, painter, option, index):
        # Check states
        is_selected = option.state & QStyle.StateFlag.State_Selected
        is_hovered = index.row() == self.hovered_row
        
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. Draw Background
        bg_color = QColor(CP_PANEL)
        if is_selected:
            bg_color = QColor(CP_CYAN)
        elif is_hovered:
            bg_color = QColor(CP_YELLOW)
        
        painter.fillRect(option.rect, bg_color)

        # 2. Determine Text Color
        if is_selected or is_hovered:
            # Force black text when highlighted/selected
            text_color = QColor("#000000")
        else:
            # Extract color from Brush if available
            fg_data = index.data(Qt.ItemDataRole.ForegroundRole)
            from PyQt6.QtGui import QBrush
            if isinstance(fg_data, QBrush):
                text_color = fg_data.color()
            elif isinstance(fg_data, QColor):
                text_color = fg_data
            else:
                text_color = QColor(CP_TEXT)
        
        # 3. Draw Text
        painter.setPen(text_color)
        text = str(index.data(Qt.ItemDataRole.DisplayRole))
        
        # Add some padding
        text_rect = option.rect.adjusted(10, 0, -10, 0)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, text)
        
        painter.restore()

# --- GIT LOGIC ---
class CommitLoaderThread(QThread):
    """Background thread for loading commits"""
    finished = pyqtSignal(dict)  # Emits result when done
    
    def __init__(self, directory, limit=None):
        super().__init__()
        self.directory = directory
        self.limit = limit
    
    def run(self):
        result = GitWorker.get_commits(self.directory, self.limit)
        self.finished.emit(result)

class GitWorker:
    @staticmethod
    def get_commits(directory, limit=None):
        if not os.path.isdir(directory):
            return {"error": "Invalid directory"}
        
        try:
            subprocess.check_call(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=directory,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except subprocess.CalledProcessError:
            return {"error": "Not a git repository"}
        except FileNotFoundError:
            return {"error": "Git not found on system path"}

        try:
            if limit and limit > 0:
                cmd = ["git", "log", "--pretty=format:%h|%an|%ad|%s", "--date=short", "-n", str(limit), "--", "."]
            else:
                cmd = ["git", "log", "--pretty=format:%h|%an|%ad|%s", "--date=short", "--", "."]
            result = subprocess.check_output(cmd, cwd=directory, text=True, encoding='utf-8')
            
            commits = []
            for line in result.strip().split('\n'):
                if not line: continue
                parts = line.split('|', 3)
                if len(parts) == 4:
                    commits.append({
                        "hash": parts[0],
                        "author": parts[1],
                        "date": parts[2],
                        "message": parts[3]
                    })
            return {"success": commits}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_commit_diff(directory, commit_hash):
        """Get the diff for a specific commit"""
        try:
            cmd = ["git", "show", "--pretty=format:", "--name-status", commit_hash]
            result = subprocess.check_output(cmd, cwd=directory, text=True, encoding='utf-8')
            
            # Get detailed diff
            cmd_diff = ["git", "show", commit_hash, "--color=never"]
            diff_result = subprocess.check_output(cmd_diff, cwd=directory, text=True, encoding='utf-8')
            
            return {"success": {"files": result, "diff": diff_result}}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def checkout_path(directory, commit_hash):
        try:
            cmd = ["git", "checkout", commit_hash, "--", "."]
            subprocess.check_call(cmd, cwd=directory)
            return {"success": True}
        except subprocess.CalledProcessError as e:
            return {"error": f"Git Error: {e}"}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_commit_diff(directory, commit_hash):
        """Get the diff for a specific commit"""
        try:
            cmd = ["git", "show", "--pretty=format:", "--name-status", commit_hash]
            files_result = subprocess.check_output(cmd, cwd=directory, text=True, encoding='utf-8')
            
            cmd = ["git", "show", commit_hash, "--color=never"]
            diff_result = subprocess.check_output(cmd, cwd=directory, text=True, encoding='utf-8')
            
            return {"success": {"files": files_result, "diff": diff_result}}
        except Exception as e:
            return {"error": str(e)}

# --- UI COMPONENTS ---

class CyberButton(QPushButton):
    def __init__(self, text, color=CP_DIM, hover_color=CP_YELLOW, text_color="white", hover_text_color="black"):
        super().__init__(text)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: {text_color};
                border: 1px solid {CP_DIM};
                padding: 8px 16px;
                font-family: 'Consolas';
                font-weight: bold;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: #2a2a2a;
                border: 1px solid {hover_color};
                color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {hover_color};
                color: {hover_text_color};
            }}
        """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Git Time Machine // CYBERPUNK EDITION")
        self.resize(1000, 700)
        
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "git_history_config.json")
        self.commit_limit = 200  # Default limit

        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            
            QLineEdit {{
                background-color: {CP_PANEL}; 
                color: {CP_CYAN}; 
                border: 1px solid {CP_DIM}; 
                padding: 6px;
            }}
            QLineEdit:focus {{ border: 1px solid {CP_CYAN}; }}
            
            QTableWidget {{
                background-color: {CP_PANEL};
                gridline-color: {CP_DIM};
                border: 1px solid {CP_DIM};
                outline: none;
            }}
            QHeaderView::section {{
                background-color: {CP_DIM};
                color: {CP_YELLOW};
                padding: 6px;
                border: 1px solid {CP_PANEL};
                font-weight: bold;
            }}
            QScrollBar:vertical {{
                border: 1px solid {CP_DIM};
                background: {CP_BG};
                width: 12px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {CP_CYAN};
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {CP_YELLOW};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: 1px solid {CP_DIM};
                background: {CP_BG};
                height: 12px;
                margin: 0px;
            }}
            QScrollBar::handle:horizontal {{
                background: {CP_CYAN};
                min-width: 20px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {CP_YELLOW};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            QTextEdit {{
                background-color: {CP_PANEL};
                color: {CP_TEXT};
                border: 1px solid {CP_DIM};
                font-family: 'Consolas';
                font-size: 9pt;
            }}
            
            /* TREE VIEW */
            QTreeView {{
                background-color: #080808;
                border: 1px solid {CP_DIM};
                color: {CP_TEXT};
                outline: none;
                show-decoration-selected: 1;
            }}
            QTreeView::item {{
                padding: 2px;
            }}
            QTreeView::item:hover {{ background-color: #1a1a1a; }}
            QTreeView::item:selected {{ 
                background-color: #222222; 
                color: {CP_YELLOW}; 
            }}
        """
        )

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select Git Directory...")
        
        last_path = self.load_config()
        self.path_input.setText(last_path if last_path and os.path.isdir(last_path) else os.getcwd())
            
        self.path_input.returnPressed.connect(self.load_commits)
        
        browse_btn = CyberButton("BROWSE", CP_DIM, CP_CYAN)
        browse_btn.clicked.connect(self.browse_directory)
        
        tree_browse_btn = CyberButton("TREE VIEW", CP_DIM, CP_GREEN)
        tree_browse_btn.clicked.connect(self.open_tree_browser)
        
        load_btn = CyberButton("LOAD COMMITS", CP_DIM, CP_YELLOW)
        load_btn.clicked.connect(self.load_commits)

        path_layout.addWidget(QLabel("DIR:"))
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_btn)
        path_layout.addWidget(tree_browse_btn)
        path_layout.addWidget(load_btn)
        layout.addLayout(path_layout)

        # Main content splitter (Table + Diff Panel)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # LEFT: Commit Table
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        table_label = QLabel("COMMIT HISTORY:")
        table_label.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold;")
        table_layout.addWidget(table_label)

        # Table Setup
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["HASH", "DATE", "AUTHOR", "MESSAGE"])
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setMouseTracking(True)
        
        # Apply Custom Delegate
        self.delegate = CyberDelegate(self.table)
        self.table.setItemDelegate(self.delegate)
        self.table.cellEntered.connect(self.on_cell_entered)
        self.table.leaveEvent = self.on_table_leave
        self.table.itemSelectionChanged.connect(self.on_commit_selected)

        table_layout.addWidget(self.table)
        main_splitter.addWidget(table_widget)
        
        # RIGHT: Diff Panel
        diff_widget = QWidget()
        diff_layout = QVBoxLayout(diff_widget)
        diff_layout.setContentsMargins(0, 0, 0, 0)
        
        diff_label = QLabel("CHANGES:")
        diff_label.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold;")
        diff_layout.addWidget(diff_label)
        
        self.diff_display = QTextEdit()
        self.diff_display.setReadOnly(True)
        self.diff_display.setAcceptRichText(True)  # Enable HTML rendering
        self.diff_display.setStyleSheet(f"""
            background-color: {CP_BG};
            color: {CP_TEXT};
            border: 1px solid {CP_DIM};
            font-family: 'Consolas';
            font-size: 9pt;
        """)
        self.diff_display.setText("Select a commit to view changes...")
        diff_layout.addWidget(self.diff_display)
        
        main_splitter.addWidget(diff_widget)
        main_splitter.setStretchFactor(0, 2)  # Table takes 2/3
        main_splitter.setStretchFactor(1, 1)  # Diff takes 1/3
        
        layout.addWidget(main_splitter)

        action_layout = QHBoxLayout()
        self.status_label = QLabel("READY")
        self.status_label.setStyleSheet(f"color: {CP_CYAN}; font-weight: bold;")
        self.status_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.status_label.mousePressEvent = self.change_commit_limit
        
        copy_hash_btn = CyberButton("COPY HASH", CP_DIM, CP_CYAN, "white", "black")
        copy_hash_btn.clicked.connect(self.copy_hash)
        
        revert_btn = CyberButton("RESTORE SELECTED VERSION", CP_DIM, CP_RED, "white", "black")
        revert_btn.clicked.connect(self.revert_commit)
        
        action_layout.addWidget(self.status_label)
        action_layout.addStretch()
        action_layout.addWidget(copy_hash_btn)
        action_layout.addWidget(revert_btn)
        layout.addLayout(action_layout)

        if os.path.isdir(self.path_input.text()):
            self.load_commits()

    def change_commit_limit(self, event):
        """Open dialog to change commit limit"""
        limit, ok = QInputDialog.getInt(
            self, 
            "Set Commit Limit", 
            "How many commits to load?\n(0 = load all commits)", 
            self.commit_limit, 
            0, 
            10000, 
            1
        )
        if ok:
            self.commit_limit = limit
            self.save_config()
            self.status_label.setStyleSheet(f"color: {CP_GREEN}; font-weight: bold;")
            if limit == 0:
                self.status_label.setText(f"LIMIT SET: ALL COMMITS")
            else:
                self.status_label.setText(f"LIMIT SET: {limit} COMMITS")

    def open_tree_browser(self):
        """Open a popup window with tree view directory browser"""
        dialog = TreeBrowserDialog(self, self.path_input.text())
        if dialog.exec():
            selected_path = dialog.get_selected_path()
            if selected_path:
                self.path_input.setText(selected_path)
                self.load_commits()

    def on_cell_entered(self, row, column):
        self.delegate.hovered_row = row
        self.table.viewport().update()

    def on_table_leave(self, event):
        self.delegate.hovered_row = -1
        self.table.viewport().update()

    def on_commit_selected(self):
        """Load diff when a commit is selected"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            self.diff_display.setText("Select a commit to view changes...")
            return
        
        row = selected_items[0].row()
        commit_hash = self.table.item(row, 0).text()
        directory = self.path_input.text()
        
        self.diff_display.setText("Loading changes...")
        QApplication.processEvents()
        
        result = GitWorker.get_commit_diff(directory, commit_hash)
        if "error" in result:
            self.diff_display.setText(f"Error loading diff:\n{result['error']}")
            return
        
        diff_data = result["success"]
        
        # Format the diff nicely
        formatted_diff = self.format_diff(diff_data["diff"])
        self.diff_display.setHtml(formatted_diff)
    
    def format_diff(self, diff_text):
        """Format git diff with colors using HTML"""
        lines = diff_text.split('\n')
        formatted_lines = []
        
        for line in lines:
            if line.startswith('+++') or line.startswith('---'):
                formatted_lines.append(f'<span style="color: {CP_CYAN}; font-weight: bold;">{line}</span>')
            elif line.startswith('+'):
                formatted_lines.append(f'<span style="color: {CP_GREEN};">{line}</span>')
            elif line.startswith('-'):
                formatted_lines.append(f'<span style="color: {CP_RED};">{line}</span>')
            elif line.startswith('@@'):
                formatted_lines.append(f'<span style="color: {CP_YELLOW}; font-weight: bold;">{line}</span>')
            elif line.startswith('diff --git'):
                formatted_lines.append(f'<span style="color: {CP_CYAN}; font-weight: bold;">{line}</span>')
            else:
                formatted_lines.append(line)
        
        return '<pre style="margin: 0; padding: 5px;">' + '<br>'.join(formatted_lines) + '</pre>'

    def copy_hash(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Required", "Please select a commit to copy its hash.")
            return

        row = selected_items[0].row()
        commit_hash = self.table.item(row, 0).text()
        
        clipboard = QApplication.clipboard()
        clipboard.setText(commit_hash)
        
        self.status_label.setStyleSheet(f"color: {CP_GREEN}; font-weight: bold;")
        self.status_label.setText(f"HASH COPIED: {commit_hash}")

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.commit_limit = data.get("commit_limit", 200)
                    return data.get("last_directory", "")
        except: pass
        return ""

    def save_config(self):
        directory = self.path_input.text() if hasattr(self, 'path_input') else ""
        try:
            with open(self.config_file, 'w') as f:
                json.dump({
                    "last_directory": directory,
                    "commit_limit": self.commit_limit
                }, f)
        except: pass

    def browse_directory(self):
        start_dir = self.path_input.text() if os.path.isdir(self.path_input.text()) else os.getcwd()
        directory = QFileDialog.getExistingDirectory(self, "Select Git Repository", start_dir)
        if directory:
            self.path_input.setText(directory)
            self.load_commits()

    def load_commits(self):
        directory = self.path_input.text().strip()
        if not directory: return
        if os.path.isdir(directory): self.save_config()

        self.table.setRowCount(0)
        self.status_label.setText("LOADING...")
        self.status_label.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold;")
        QApplication.processEvents()

        # Use threading for better performance
        self.loader_thread = CommitLoaderThread(directory, self.commit_limit)
        self.loader_thread.finished.connect(self.on_commits_loaded)
        self.loader_thread.start()

    def on_commits_loaded(self, result):
        """Called when commits are loaded in background thread"""
        if "error" in result:
            self.status_label.setStyleSheet(f"color: {CP_RED}; font-weight: bold;")
            self.status_label.setText(f"ERROR: {result['error']}")
            return

        commits = result["success"]
        self.table.setRowCount(len(commits))
        
        for i, commit in enumerate(commits):
            items = [
                QTableWidgetItem(commit['hash']),
                QTableWidgetItem(commit['date']),
                QTableWidgetItem(commit['author']),
                QTableWidgetItem(commit['message'])
            ]
            
            # Set colors (Yellow for hash, Cyan for author, Text for others)
            items[0].setForeground(QColor(CP_YELLOW))
            items[1].setForeground(QColor(CP_TEXT))
            items[2].setForeground(QColor(CP_CYAN))
            items[3].setForeground(QColor(CP_TEXT))
            
            for col, item in enumerate(items):
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(i, col, item)

        self.status_label.setStyleSheet(f"color: {CP_GREEN}; font-weight: bold;")
        limit_text = f" (LIMIT: {self.commit_limit})" if self.commit_limit > 0 else " (ALL)"
        self.status_label.setText(f"LOADED {len(commits)} COMMITS{limit_text}")

    def revert_commit(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Required", "Please select a commit to restore from.")
            return

        row = selected_items[0].row()
        commit_hash = self.table.item(row, 0).text()
        commit_msg = self.table.item(row, 3).text()
        directory = self.path_input.text()

        confirm = QMessageBox.question(
            self, "Confirm Restore",
            f"Restore directory to commit:\n[{commit_hash}] {commit_msg}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.status_label.setText("RESTORING...")
            QApplication.processEvents()
            result = GitWorker.checkout_path(directory, commit_hash)
            if "success" in result:
                self.status_label.setStyleSheet(f"color: {CP_GREEN}; font-weight: bold;")
                self.status_label.setText(f"SUCCESS: RESTORED TO {commit_hash}")
                QMessageBox.information(self, "Success", f"Restored to {commit_hash}.")
            else:
                self.status_label.setStyleSheet(f"color: {CP_RED}; font-weight: bold;")
                self.status_label.setText("RESTORE FAILED")
                QMessageBox.critical(self, "Error", result['error'])

# --- TREE BROWSER DIALOG ---
class TreeBrowserDialog(QDialog):
    def __init__(self, parent=None, start_path=""):
        super().__init__(parent)
        self.setWindowTitle("Select Directory - Tree View")
        self.resize(700, 500)
        self.selected_path = start_path if start_path and os.path.isdir(start_path) else os.getcwd()
        
        self.setStyleSheet(f"""
            QDialog {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QLineEdit {{
                background-color: {CP_PANEL};
                color: {CP_CYAN};
                border: 1px solid {CP_DIM};
                padding: 6px;
            }}
            QTreeView {{
                background-color: #080808;
                border: 1px solid {CP_DIM};
                color: {CP_TEXT};
                outline: none;
                show-decoration-selected: 1;
            }}
            QTreeView::item {{
                padding: 2px;
            }}
            QTreeView::item:hover {{ 
                background-color: #1a1a1a; 
            }}
            QTreeView::item:selected {{ 
                background-color: #222222; 
                color: {CP_YELLOW};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_label = QLabel("BROWSE DIRECTORIES:")
        header_label.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold; font-size: 12pt;")
        layout.addWidget(header_label)
        
        # Current Path Display
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Selected:"))
        self.path_display = QLineEdit(self.selected_path)
        self.path_display.setReadOnly(True)
        path_layout.addWidget(self.path_display)
        layout.addLayout(path_layout)
        
        # Tree View
        self.tree_view = QTreeView()
        self.tree_model = QFileSystemModel()
        self.tree_model.setReadOnly(True)
        self.tree_model.setFilter(QDir.Filter.Dirs | QDir.Filter.NoDotAndDotDot)
        self.tree_model.setIconProvider(CyberIconProvider())
        
        self.tree_model.setRootPath("")
        self.tree_view.setModel(self.tree_model)
        self.tree_view.setRootIndex(self.tree_model.index(""))
        self.tree_view.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        # Hide columns: Size, Type, Date Modified
        for i in range(1, 4):
            self.tree_view.hideColumn(i)
        
        self.tree_view.clicked.connect(self.on_directory_clicked)
        self.tree_view.doubleClicked.connect(self.on_directory_double_clicked)
        
        # Expand to start path
        if os.path.isdir(self.selected_path):
            index = self.tree_model.index(self.selected_path)
            self.tree_view.setCurrentIndex(index)
            self.tree_view.scrollTo(index)
            self.tree_view.expand(index)
        
        layout.addWidget(self.tree_view)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = CyberButton("CANCEL", CP_DIM, CP_RED)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        select_btn = CyberButton("SELECT", CP_DIM, CP_GREEN)
        select_btn.clicked.connect(self.accept)
        btn_layout.addWidget(select_btn)
        
        layout.addLayout(btn_layout)
    
    def on_directory_clicked(self, index):
        path = self.tree_model.filePath(index)
        if os.path.isdir(path):
            self.selected_path = path
            self.path_display.setText(path)
    
    def on_directory_double_clicked(self, index):
        path = self.tree_model.filePath(index)
        if os.path.isdir(path):
            self.selected_path = path
            self.path_display.setText(path)
            self.accept()
    
    def get_selected_path(self):
        return self.selected_path

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
