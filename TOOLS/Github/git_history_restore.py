import sys
import os
import subprocess
import json
import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog, QMessageBox, QAbstractItemView, QStyledItemDelegate, QStyle,
    QTreeView, QDialog, QFileIconProvider, QInputDialog, QTextBrowser, QSplitter, QSpinBox, QMenu
)
from PyQt6.QtCore import Qt, QSize, QRect, QDir, QFileInfo, QThread, pyqtSignal, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QFont, QColor, QCursor, QPainter, QFileSystemModel, QIcon, QPixmap, QPen, QStandardItemModel, QStandardItem

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
        is_active = index.siblingAtColumn(0).data(Qt.ItemDataRole.UserRole) == True
        
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. Draw Background
        bg_color = QColor(CP_PANEL)
        if is_selected:
            bg_color = QColor(CP_CYAN)
        elif is_hovered:
            bg_color = QColor(CP_YELLOW)
        
        painter.fillRect(option.rect, bg_color)

        # 2. Draw Active Border
        if is_active:
            painter.setPen(QPen(QColor(CP_GREEN), 2))
            rect = option.rect
            
            # Draw top and bottom borders for all cells in the row
            painter.drawLine(rect.left(), rect.top() + 1, rect.right(), rect.top() + 1)
            painter.drawLine(rect.left(), rect.bottom(), rect.right(), rect.bottom())
            
            # Draw left border only for the first column
            if index.column() == 0:
                painter.drawLine(rect.left() + 1, rect.top() + 1, rect.left() + 1, rect.bottom())
                
            # Draw right border only for the last column
            if index.column() == index.model().columnCount() - 1:
                painter.drawLine(rect.right() - 1, rect.top() + 1, rect.right() - 1, rect.bottom())

        # 3. Determine Text Color
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
        
        # 4. Draw Text
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
    
    def __init__(self, directory, limit=None, scope="."):
        super().__init__()
        self.directory = directory
        self.limit = limit
        self.scope = scope
    
    def run(self):
        result = GitWorker.get_commits(self.directory, self.limit, self.scope)
        self.finished.emit(result)

class GitWorker:
    @staticmethod
    def get_commits(directory, limit=None, scope="."):
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
            # Ensure scope is handled correctly (default to current dir if empty)
            git_scope = scope if scope and scope.strip() else "."
            
            if limit and limit > 0:
                cmd = ["git", "log", "--pretty=format:%h|%an|%ad|%s", "--date=short", "-n", str(limit), "--", git_scope]
            else:
                cmd = ["git", "log", "--pretty=format:%h|%an|%ad|%s", "--date=short", "--", git_scope]
            
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
    def get_git_root(directory):
        """Get the root directory of the git repository"""
        try:
            root = subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=directory,
                text=True,
                encoding='utf-8'
            ).strip()
            return root
        except:
            return directory

    @staticmethod
    def get_diff_between(directory, commit_a, commit_b="HEAD", scope="."):
        """Get the diff between two points, scoped to a path"""
        try:
            git_scope = scope if scope and scope.strip() else "."
            
            # Get file stats (additions/deletions)
            cmd_stats = ["git", "diff", "--stat", "--format=", f"{commit_a}..{commit_b}", "--", git_scope]
            stats_result = subprocess.check_output(cmd_stats, cwd=directory, text=True, encoding='utf-8', errors='replace')
            
            # Get detailed diff
            cmd_diff = ["git", "diff", f"{commit_a}..{commit_b}", "--color=never", "--", git_scope]
            diff_result = subprocess.check_output(cmd_diff, cwd=directory, text=True, encoding='utf-8', errors='replace')
            
            return {"success": {"stats": stats_result, "diff": diff_result}}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def checkout_path(directory, commit_hash, scope="."):
        try:
            git_scope = scope if scope and scope.strip() else "."
            cmd = ["git", "checkout", commit_hash, "--", git_scope]
            subprocess.check_call(cmd, cwd=directory)
            return {"success": True}
        except subprocess.CalledProcessError as e:
            return {"error": f"Git Error: {e}"}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def checkout_file(directory, commit_hash, file_path):
        try:
            cmd = ["git", "checkout", commit_hash, "--", file_path]
            subprocess.check_call(cmd, cwd=directory)
            return {"success": True}
        except subprocess.CalledProcessError as e:
            return {"error": f"Git Error: {e}"}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_file_history(directory, file_path, limit=50):
        try:
            cmd = ["git", "log", "--pretty=format:%h|%ad|%s", "--date=short", "-n", str(limit), "--", file_path]
            result = subprocess.check_output(cmd, cwd=directory, text=True, encoding='utf-8')
            commits = []
            for line in result.strip().split('\n'):
                if not line: continue
                parts = line.split('|', 2)
                if len(parts) == 3:
                    commits.append({
                        "hash": parts[0],
                        "date": parts[1],
                        "message": parts[2]
                    })
            return {"success": commits}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_commit_tree(directory, commit_hash, sub_path=None):
        """Get all files in the repository at a specific commit, optionally filtered by sub_path"""
        try:
            cmd = ["git", "ls-tree", "-r", "--name-only", "-z", commit_hash]
            if sub_path and sub_path != ".":
                cmd.append(sub_path)
            result = subprocess.check_output(cmd, cwd=directory, text=True, encoding='utf-8')
            return {"success": [f for f in result.split('\0') if f]}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_local_changes(directory):
        """Get list of files that have local changes (modified, deleted, staged, etc.)"""
        try:
            # -u to see untracked, but let's stick to tracked changes for safety
            cmd = ["git", "status", "--porcelain", "-z"]
            result = subprocess.check_output(cmd, cwd=directory, text=True, encoding="utf-8")
            files = []
            parts = result.split("\x00")
            for part in parts:
                if not part: continue
                # Format: XY filename (XY is 2 chars)
                status = part[:2]
                filename = part[3:]
                # We care about anything changed in index or worktree
                if status.strip():
                    files.append(filename)
            return {"success": files}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_commit_changed_files(directory, commit_hash):
        """Get all files that were changed in a specific commit (including additions/deletions)"""
        try:
            cmd = ["git", "diff-tree", "--no-commit-id", "--name-status", "-r", "-z", commit_hash]
            result = subprocess.check_output(cmd, cwd=directory, text=True, encoding="utf-8")
            parts = result.split("\x00")
            files = []
            for i in range(0, len(parts)-1, 2):
                status = parts[i]
                filename = parts[i+1]
                if status and filename:
                    files.append({"status": status, "path": filename})
            return {"success": files}
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

class CyberDiffBrowser(QTextBrowser):
    file_context_requested = pyqtSignal(int)
    file_restore_requested = pyqtSignal(int)
    file_timeline_requested = pyqtSignal(int)

    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window

    def contextMenuEvent(self, event):
        url = self.anchorAt(event.pos())
        if url.startswith("file-"):
            try:
                idx = int(url.replace("file-", ""))
                menu = self.createStandardContextMenu()
                menu.addSeparator()
                
                # Header info - use main_window if available
                file_name = "Unknown"
                if self.main_window and idx < len(self.main_window.current_diff_sections):
                    file_name = os.path.basename(self.main_window.current_diff_sections[idx]['name'])
                
                header_action = menu.addAction(f"📄 FILE: {file_name}")
                header_action.setEnabled(False)
                menu.addSeparator()
                
                action_open = menu.addAction("📂 Open in Editor")
                action_restore = menu.addAction("⏮️ Restore this File")
                action_timeline = menu.addAction("📜 View File Timeline")
                
                selected = menu.exec(event.globalPos())
                if selected == action_open:
                    self.file_context_requested.emit(idx)
                elif selected == action_restore:
                    self.file_restore_requested.emit(idx)
                elif selected == action_timeline:
                    self.file_timeline_requested.emit(idx)
                return
            except Exception:
                pass
        super().contextMenuEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Git Time Machine // CYBERPUNK EDITION")
        
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), r"C:\@delta\output\git_restore\git_history_config.json")
        self.commit_limit = 200  # Default limit
        self.window_width = 1400  # Default window width
        self.window_height = 700  # Default window height
        self.split_ratio = [2, 3]  # Default split ratio [left, right]
        self.current_diff_sections = []  # Store parsed diff sections
        self.active_commit_hash = None # Track currently restored full commit
        self.restored_files = {} # Track restored files: {rel_path: commit_hash}
        
        # Load config first to get window size
        self.load_config()
        self.resize(self.window_width, self.window_height)

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
        
        settings_btn = CyberButton("⚙️ SETTINGS", CP_DIM, CP_CYAN)
        settings_btn.clicked.connect(self.open_settings)
        
        load_btn = CyberButton("LOAD COMMITS", CP_DIM, CP_YELLOW)
        load_btn.clicked.connect(self.load_commits)

        path_layout.addWidget(QLabel("DIR:"))
        path_layout.addWidget(self.path_input)
        
        path_layout.addWidget(QLabel("SCOPE:"))
        self.scope_input = QLineEdit(".")
        self.scope_input.setPlaceholderText("Folder or file path...")
        self.scope_input.setToolTip("Narrow log to this sub-folder or specific file")
        self.scope_input.setFixedWidth(200)
        self.scope_input.returnPressed.connect(self.load_commits)
        path_layout.addWidget(self.scope_input)

        path_layout.addWidget(browse_btn)
        path_layout.addWidget(tree_browse_btn)
        path_layout.addWidget(settings_btn)
        path_layout.addWidget(load_btn)
        layout.addLayout(path_layout)

        # Main content splitter (Table + Diff Panel)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter = main_splitter  # Store reference for settings
        
        # LEFT: Commit Table
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # Search Bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("SEARCH:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter commits by message, hash, or author...")
        self.search_input.textChanged.connect(self.filter_commits)
        search_layout.addWidget(self.search_input)
        table_layout.addLayout(search_layout)

        # Table Label
        table_label_layout = QHBoxLayout()
        table_label = QLabel("COMMIT HISTORY:")
        table_label.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold;")
        table_label_layout.addWidget(table_label)
        table_label_layout.addStretch()
        table_layout.addLayout(table_label_layout)

        # Table Setup
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["HASH", "DATE", "AUTHOR", "MESSAGE"])
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setMouseTracking(True)
        
        # Apply Custom Delegate
        self.delegate = CyberDelegate(self.table)
        self.table.setItemDelegate(self.delegate)
        self.table.cellEntered.connect(self.on_cell_entered)
        self.table.leaveEvent = self.on_table_leave
        self.table.itemSelectionChanged.connect(self.on_commit_selected)
        self.table.itemDoubleClicked.connect(lambda: self.open_commit_explorer())

        table_layout.addWidget(self.table)
        main_splitter.addWidget(table_widget)
        
        # RIGHT: Diff Panel
        diff_widget = QWidget()
        diff_layout = QVBoxLayout(diff_widget)
        diff_layout.setContentsMargins(0, 0, 0, 0)
        
        diff_header_layout = QHBoxLayout()
        diff_label = QLabel("CHANGES:")
        diff_label.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold;")
        diff_header_layout.addWidget(diff_label)
        
        diff_header_layout.addStretch()
        
        from PyQt6.QtWidgets import QCheckBox
        self.compare_to_head_cb = QCheckBox("Compare to HEAD")
        self.compare_to_head_cb.setToolTip("Show everything that has changed in this folder since the selected commit, instead of just the commit itself.")
        self.compare_to_head_cb.setStyleSheet(f"color: {CP_CYAN}; font-weight: bold;")
        self.compare_to_head_cb.stateChanged.connect(self.on_commit_selected)
        diff_header_layout.addWidget(self.compare_to_head_cb)
        
        diff_layout.addLayout(diff_header_layout)
        
        self.diff_display = CyberDiffBrowser(self)
        self.diff_display.file_context_requested.connect(self.open_file_in_editor)
        self.diff_display.file_restore_requested.connect(self.restore_single_file)
        self.diff_display.file_timeline_requested.connect(self.open_file_timeline)
        self.diff_display.setOpenExternalLinks(False)
        self.diff_display.setOpenLinks(False)
        self.diff_display.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {CP_BG};
                border: 1px solid {CP_DIM};
                color: {CP_TEXT};
                font-family: 'JetBrainsMono Nerd Font', 'Consolas', monospace;
                font-size: 10pt;
            }}
        """)
        self.diff_display.setHtml("<div style='color: #E0E0E0; padding: 20px;'>Select a commit to view changes...</div>")
        self.diff_display.anchorClicked.connect(self.on_file_header_clicked)
        diff_layout.addWidget(self.diff_display)
        
        # Track expanded files
        self.expanded_files = set()
        
        main_splitter.addWidget(diff_widget)
        main_splitter.setStretchFactor(0, self.split_ratio[0])  # Table
        main_splitter.setStretchFactor(1, self.split_ratio[1])  # Diff
        
        self.main_splitter = main_splitter  # Store reference for settings
        
        layout.addWidget(main_splitter)

        action_layout = QHBoxLayout()
        self.status_label = QLabel("READY")
        self.status_label.setStyleSheet(f"color: {CP_CYAN}; font-weight: bold;")
        self.status_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.status_label.mousePressEvent = self.change_commit_limit
        
        copy_hash_btn = CyberButton("COPY HASH", CP_DIM, CP_CYAN, "white", "black")
        copy_hash_btn.clicked.connect(self.copy_hash)
        
        explore_btn = CyberButton("EXPLORE COMMIT", CP_DIM, CP_CYAN, "white", "black")
        explore_btn.clicked.connect(self.open_commit_explorer)
        
        restore_files_btn = CyberButton("RESTORE COMMIT FILES (PREVIOUS)", CP_YELLOW, CP_YELLOW, "black", "black")
        restore_files_btn.clicked.connect(self.restore_files_to_current)
        
        revert_btn = CyberButton("RESTORE SELECTED VERSION", CP_DIM, CP_RED, "white", "black")
        revert_btn.clicked.connect(self.revert_commit)
        
        action_layout.addWidget(self.status_label)
        action_layout.addStretch()
        action_layout.addWidget(copy_hash_btn)
        action_layout.addWidget(explore_btn)
        action_layout.addWidget(restore_files_btn)
        
        restore_commit_files_btn = CyberButton("RESTORE COMMIT FILES (SELECTED)", CP_GREEN, CP_GREEN, "black", "black")
        restore_commit_files_btn.clicked.connect(self.restore_commit_files)
        action_layout.addWidget(restore_commit_files_btn)
        
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

    def open_settings(self):
        """Open settings dialog for window size and split ratio"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        dialog.resize(400, 250)
        dialog.setStyleSheet(f"""
            QDialog {{ background-color: {CP_BG}; }}
            QLabel {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QLineEdit {{
                background-color: {CP_PANEL};
                color: {CP_CYAN};
                border: 1px solid {CP_DIM};
                padding: 6px;
            }}
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("WINDOW SETTINGS:")
        header.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold; font-size: 12pt;")
        layout.addWidget(header)
        
        # Window Width
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("Window Width:"))
        width_input = QLineEdit(str(self.window_width))
        width_layout.addWidget(width_input)
        layout.addLayout(width_layout)
        
        # Window Height
        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("Window Height:"))
        height_input = QLineEdit(str(self.window_height))
        height_layout.addWidget(height_input)
        layout.addLayout(height_layout)
        
        # Split Ratio
        split_layout = QHBoxLayout()
        split_layout.addWidget(QLabel("Left Panel %:"))
        split_input = QLineEdit(str(int(self.split_ratio[0] / sum(self.split_ratio) * 100)))
        split_layout.addWidget(split_input)
        layout.addLayout(split_layout)
        
        info_label = QLabel("(Right panel will take the remaining %)")
        info_label.setStyleSheet(f"color: {CP_DIM}; font-size: 9pt;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = CyberButton("CANCEL", CP_DIM, CP_RED)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = CyberButton("SAVE", CP_DIM, CP_GREEN)
        save_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
        if dialog.exec():
            try:
                new_width = int(width_input.text())
                new_height = int(height_input.text())
                left_percent = int(split_input.text())
                
                if 800 <= new_width <= 3840 and 600 <= new_height <= 2160 and 10 <= left_percent <= 90:
                    self.window_width = new_width
                    self.window_height = new_height
                    right_percent = 100 - left_percent
                    self.split_ratio = [left_percent, right_percent]
                    
                    self.resize(self.window_width, self.window_height)
                    self.main_splitter.setStretchFactor(0, self.split_ratio[0])
                    self.main_splitter.setStretchFactor(1, self.split_ratio[1])
                    
                    self.save_config()
                    self.status_label.setStyleSheet(f"color: {CP_GREEN}; font-weight: bold;")
                    self.status_label.setText("SETTINGS SAVED")
                else:
                    QMessageBox.warning(self, "Invalid Values", "Please enter valid values:\nWidth: 800-3840\nHeight: 600-2160\nLeft %: 10-90")
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", "Please enter valid numbers")

    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self, self.window_width, self.window_height, self.split_ratio)
        if dialog.exec():
            self.window_width = dialog.width_spin.value()
            self.window_height = dialog.height_spin.value()
            left_ratio = dialog.left_spin.value()
            right_ratio = dialog.right_spin.value()
            self.split_ratio = [left_ratio, right_ratio]
            
            # Apply settings
            self.resize(self.window_width, self.window_height)
            self.main_splitter.setStretchFactor(0, self.split_ratio[0])
            self.main_splitter.setStretchFactor(1, self.split_ratio[1])
            
            # Save to config
            self.save_config()

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

    def toggle_file_section(self, url):
        """Toggle file section visibility when clicked"""
        file_id = url.toString()
        # Extract index from "file-0", "file-1", etc.
        if file_id.startswith("file-"):
            try:
                idx = int(file_id.replace("file-", ""))
                if idx in self.expanded_files:
                    self.expanded_files.remove(idx)
                else:
                    self.expanded_files.add(idx)
                
                # Re-render the diff display
                self.render_diff_html()
            except ValueError:
                pass

    def on_file_header_clicked(self, url):
        """Handle clicks on file headers to toggle expand/collapse"""
        file_idx = int(url.toString().replace('file-', ''))
        
        if file_idx in self.expanded_files:
            self.expanded_files.remove(file_idx)
        else:
            self.expanded_files.add(file_idx)
        
        # Regenerate HTML with updated state
        self.render_diff_html()
    
    def open_file_in_editor(self, idx):
        if 0 <= idx < len(self.current_diff_sections):
            rel_path = self.current_diff_sections[idx]['name']
            current_dir = self.path_input.text()
            
            # Get git root to ensure correct path resolution
            base_dir = GitWorker.get_git_root(current_dir)
            full_path = os.path.normpath(os.path.join(base_dir, rel_path))
            
            script_path = r"C:\@delta\ms1\scripts\run\editor_chooser.py"
            
            try:
                # Use Popen to not block the GUI
                subprocess.Popen([sys.executable, script_path, full_path], cwd=os.path.dirname(script_path))
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to launch editor chooser:\n{str(e)}")

    def restore_single_file(self, idx):
        """Restore a single file to the selected commit version"""
        if not (0 <= idx < len(self.current_diff_sections)):
            return
            
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
            
        row = selected_items[0].row()
        commit_hash = self.table.item(row, 0).text()
        rel_path = self.current_diff_sections[idx]['name']
        directory = self.path_input.text()
        
        confirm = QMessageBox.question(
            self, "Confirm File Restore",
            f"Restore single file to commit version [{commit_hash}]?\n\nFile: {rel_path}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            self.status_label.setText(f"RESTORING {rel_path}...")
            self.status_label.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold;")
            QApplication.processEvents()
            
            # Get git root for correct path
            base_dir = GitWorker.get_git_root(directory)
            result = GitWorker.checkout_file(base_dir, commit_hash, rel_path)
            
            if "success" in result:
                self.restored_files[rel_path] = commit_hash
                self.render_diff_html()
                self.status_label.setStyleSheet(f"color: {CP_GREEN}; font-weight: bold;")
                self.status_label.setText(f"SUCCESS: RESTORED {rel_path}")
                QMessageBox.information(self, "Success", f"Successfully restored {rel_path} to version {commit_hash}.")
            else:
                self.status_label.setStyleSheet(f"color: {CP_RED}; font-weight: bold;")
                self.status_label.setText("RESTORE FAILED")
                QMessageBox.critical(self, "Error", result['error'])

    def open_commit_explorer(self):
        """Open a tree explorer for the selected commit"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            # If no selection, maybe try the current item?
            selected_items = [self.table.currentItem()] if self.table.currentItem() else []
            if not selected_items:
                QMessageBox.warning(self, "Selection Required", "Please select a commit to explore.")
                return

        row = selected_items[0].row()
        commit_hash = self.table.item(row, 0).text()
        directory = self.path_input.text()
        base_dir = GitWorker.get_git_root(directory)
        
        # Calculate relative path from git root to current folder for filtering
        rel_sub_path = os.path.relpath(directory, base_dir).replace('\\', '/')
        if rel_sub_path == ".": rel_sub_path = None
        
        self.status_label.setText(f"FETCHING COMMIT TREE: {commit_hash}...")
        self.status_label.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold;")
        QApplication.processEvents()
        
        result = GitWorker.get_commit_tree(base_dir, commit_hash, rel_sub_path)
        if "error" in result:
            QMessageBox.critical(self, "Error", f"Failed to get commit tree:\n{result['error']}")
            return
            
        dialog = CommitExplorerDialog(self, base_dir, commit_hash, result["success"], rel_sub_path)
        dialog.exec()

    def restore_file_by_path(self, rel_path, commit_hash):
        """Helper to restore a file/folder by path from external dialog"""
        directory = self.path_input.text()
        base_dir = GitWorker.get_git_root(directory)
        
        confirm = QMessageBox.question(
            self, "Confirm Restore",
            f"Restore version {commit_hash}?\n\nTarget: {rel_path}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            res = GitWorker.checkout_file(base_dir, commit_hash, rel_path)
            if "success" in res:
                # Update status if it was a file (and tracked in restored_files)
                # Note: Folder restoration doesn't necessarily track specific files easily
                if os.path.isfile(os.path.join(base_dir, rel_path)):
                    self.restored_files[rel_path] = commit_hash
                    self.render_diff_html()
                
                self.status_label.setStyleSheet(f"color: {CP_GREEN}; font-weight: bold;")
                self.status_label.setText(f"SUCCESS: RESTORED {rel_path}")
                QMessageBox.information(self, "Success", f"Restored {rel_path} to {commit_hash}")
            else:
                QMessageBox.critical(self, "Error", res['error'])

    def open_timeline_by_path(self, rel_path):
        """Helper to open timeline for a specific path from external dialog"""
        directory = self.path_input.text()
        base_dir = GitWorker.get_git_root(directory)
        
        self.status_label.setText(f"FETCHING TIMELINE: {rel_path}...")
        self.status_label.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold;")
        QApplication.processEvents()
        
        result = GitWorker.get_file_history(base_dir, rel_path)
        if "error" in result:
            QMessageBox.critical(self, "Error", f"Failed to get history:\n{result['error']}")
            return
            
        commits = result["success"]
        dialog = FileTimelineDialog(self, rel_path, commits, self.restored_files.get(rel_path))
        if dialog.exec():
            commit_hash = dialog.selected_commit
            if commit_hash:
                self.restore_file_by_path(rel_path, commit_hash)

    def open_file_timeline(self, idx):
        """Show timeline of all versions for a specific file"""
        if not (0 <= idx < len(self.current_diff_sections)):
            return
            
        rel_path = self.current_diff_sections[idx]['name']
        directory = self.path_input.text()
        base_dir = GitWorker.get_git_root(directory)
        
        self.status_label.setText(f"FETCHING TIMELINE: {rel_path}...")
        self.status_label.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold;")
        QApplication.processEvents()
        
        result = GitWorker.get_file_history(base_dir, rel_path)
        if "error" in result:
            QMessageBox.critical(self, "Error", f"Failed to get history:\n{result['error']}")
            return
            
        commits = result["success"]
        dialog = FileTimelineDialog(self, rel_path, commits, self.restored_files.get(rel_path))
        if dialog.exec():
            commit_hash = dialog.selected_commit
            if commit_hash:
                confirm = QMessageBox.question(
                    self, "Confirm Restore",
                    f"Restore {rel_path} to version {commit_hash}?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if confirm == QMessageBox.StandardButton.Yes:
                    self.status_label.setText(f"RESTORING {rel_path}...")
                    QApplication.processEvents()
                    res = GitWorker.checkout_file(base_dir, commit_hash, rel_path)
                    if "success" in res:
                        self.restored_files[rel_path] = commit_hash
                        self.render_diff_html()
                        self.status_label.setStyleSheet(f"color: {CP_GREEN}; font-weight: bold;")
                        self.status_label.setText(f"SUCCESS: RESTORED {rel_path}")
                        QMessageBox.information(self, "Success", f"Restored {rel_path} to {commit_hash}")
                    else:
                        self.status_label.setStyleSheet(f"color: {CP_RED}; font-weight: bold;")
                        QMessageBox.critical(self, "Error", res['error'])

    def render_diff_html(self):
        """Render the diff HTML based on current expanded state"""
        if not self.current_diff_sections:
            return
        
        html_parts = []
        html_parts.append(f"<html><body style='background-color: {CP_BG}; color: {CP_TEXT}; margin: 0; padding: 10px; font-family: \"JetBrainsMono Nerd Font\", \"Consolas\", monospace; font-size: 10pt;'>")
        
        for idx, section in enumerate(self.current_diff_sections):
            stats = section['stats']
            stats_text = f'<span style="color: {CP_GREEN};">+{stats["additions"]}</span> <span style="color: {CP_RED};">-{stats["deletions"]}</span>'
            
            is_expanded = idx in self.expanded_files
            icon = '▼' if is_expanded else '▶'
            
            # Check if this file was restored
            rel_path = section['name']
            restored_hash = self.restored_files.get(rel_path)
            active_tag = f' <span style="color: {CP_GREEN}; border: 1px solid {CP_GREEN}; padding: 1px 4px; font-size: 8pt;">ACTIVE: {restored_hash}</span>' if restored_hash else ""
            border_style = f"border-left: 5px solid {CP_GREEN};" if restored_hash else f"border-left: 5px solid {CP_CYAN};"
            
            # File header
            html_parts.append(f'''
                <div style="background-color: {CP_DIM}; color: {CP_YELLOW}; padding: 10px; margin-top: 15px; margin-bottom: 0px; font-weight: bold; {border_style} font-size: 11pt;">
                    <a href="file-{idx}" style="color: {CP_YELLOW}; text-decoration: none;">{icon} 📄 {rel_path} &nbsp;&nbsp; {stats_text}{active_tag}</a>
                </div>
            ''')
            
            # File content (show if expanded)
            if is_expanded:
                content_lines = []
                for line in section['lines']:
                    if line.startswith('+'):
                        escaped_line = line.replace('<', '&lt;').replace('>', '&gt;').replace(' ', '&nbsp;')
                        content_lines.append(f'<div style="color: {CP_GREEN}; background-color: #001a00; padding: 3px 8px;">{escaped_line}</div>')
                    elif line.startswith('-'):
                        escaped_line = line.replace('<', '&lt;').replace('>', '&gt;').replace(' ', '&nbsp;')
                        content_lines.append(f'<div style="color: {CP_RED}; background-color: #1a0000; padding: 3px 8px;">{escaped_line}</div>')
                    elif line.strip():
                        escaped_line = line.replace('<', '&lt;').replace('>', '&gt;').replace(' ', '&nbsp;')
                        content_lines.append(f'<div style="color: {CP_TEXT}; padding: 3px 8px;">{escaped_line}</div>')
                
                html_parts.append(f'<div style="border-left: 5px solid {CP_DIM}; margin-bottom: 8px;">{"".join(content_lines)}</div>')
        
        html_parts.append("</body></html>")
        self.diff_display.setHtml("".join(html_parts))

    def on_commit_selected(self):
        """Load diff when a commit is selected"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            self.diff_display.setHtml(f"<div style='color: {CP_TEXT}; padding: 20px;'>Select a commit to view changes...</div>")
            self.expanded_files.clear()
            self.current_diff_sections = []
            return
        
        row = selected_items[0].row()
        commit_hash = self.table.item(row, 0).text()
        directory = self.path_input.text()
        scope = self.scope_input.text() or "."
        
        compare_mode = self.compare_to_head_cb.isChecked()
        loading_text = "Loading changes since commit..." if compare_mode else "Loading commit changes..."
        self.diff_display.setHtml(f"<div style='color: {CP_YELLOW}; padding: 20px;'>{loading_text}</div>")
        QApplication.processEvents()
        
        if compare_mode:
            result = GitWorker.get_diff_between(directory, commit_hash, "HEAD", scope)
        else:
            # We want just the specific commit diff, but scoped to the path
            result = GitWorker.get_diff_between(directory, f"{commit_hash}^", commit_hash, scope)
            
        if "error" in result:
            self.diff_display.setHtml(f"<div style='color: {CP_RED}; padding: 20px;'>Error loading diff:<br>{result['error']}</div>")
            self.expanded_files.clear()
            self.current_diff_sections = []
            return
        
        diff_data = result["success"]
        
        # Parse and store diff sections
        self.current_diff_sections = self.parse_diff(diff_data["diff"])
        self.expanded_files.clear()  # Collapse all by default
        
        # Render the diff
        self.render_diff_html()
    
    def parse_diff(self, diff_text):
        """Parse git diff into file sections"""
        lines = diff_text.split('\n')
        file_sections = []
        skip_until_diff = True
        current_file = None
        current_file_lines = []
        file_stats = {}
        
        # First pass: collect file stats from diff
        for line in lines:
            if line.startswith('diff --git'):
                # Safer extraction using regex to handle spaces and b/ prefix correctly
                m = re.match(r'diff --git a/(.*) b/(.*)', line)
                if m:
                    current_file = m.group(2)
                    file_stats[current_file] = {'additions': 0, 'deletions': 0}
                else:
                    parts = line.split(' ')
                    if len(parts) >= 4:
                        # Fallback: simpler extraction, handle b/ prefix carefully
                        # Check if part[3] starts with b/ and remove it
                        raw_name = parts[3]
                        if raw_name.startswith('b/'):
                            current_file = raw_name[2:]
                        else:
                            current_file = raw_name
                        file_stats[current_file] = {'additions': 0, 'deletions': 0}
            elif current_file and line.startswith('+') and not line.startswith('+++'):
                file_stats[current_file]['additions'] += 1
            elif current_file and line.startswith('-') and not line.startswith('---'):
                file_stats[current_file]['deletions'] += 1
        
        # Second pass: group by files
        current_file = None
        current_file_lines = []
        
        for line in lines:
            # Skip everything until we hit the first diff
            if skip_until_diff:
                if line.startswith('diff --git'):
                    skip_until_diff = False
                else:
                    continue
            
            # Detect file changes
            if line.startswith('diff --git'):
                # Save previous file section
                if current_file and current_file_lines:
                    file_sections.append({
                        'name': current_file,
                        'lines': current_file_lines[:],
                        'stats': file_stats.get(current_file, {'additions': 0, 'deletions': 0})
                    })
                    current_file_lines = []
                
                # Extract new filename
                m = re.match(r'diff --git a/(.*) b/(.*)', line)
                if m:
                    current_file = m.group(2)
                else:
                    parts = line.split(' ')
                    if len(parts) >= 4:
                         raw_name = parts[3]
                         if raw_name.startswith('b/'):
                             current_file = raw_name[2:]
                         else:
                             current_file = raw_name
                continue
            
            # Skip metadata
            if line.startswith('index ') or line.startswith('new file') or line.startswith('deleted file') or line.startswith('mode ') or line.startswith('+++') or line.startswith('---') or line.startswith('@@'):
                continue
            
            # Collect file lines
            if current_file:
                current_file_lines.append(line)
        
        # Save last file section
        if current_file and current_file_lines:
            file_sections.append({
                'name': current_file,
                'lines': current_file_lines,
                'stats': file_stats.get(current_file, {'additions': 0, 'deletions': 0})
            })
        
        return file_sections

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
                    self.window_width = data.get("window_width", 1400)
                    self.window_height = data.get("window_height", 700)
                    self.split_ratio = data.get("split_ratio", [2, 3])
                    return data.get("last_directory", "")
        except: pass
        return ""

    def save_config(self):
        directory = self.path_input.text() if hasattr(self, 'path_input') else ""
        try:
            with open(self.config_file, 'w') as f:
                json.dump({
                    "last_directory": directory,
                    "commit_limit": self.commit_limit,
                    "window_width": self.window_width,
                    "window_height": self.window_height,
                    "split_ratio": self.split_ratio
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
        self.loader_thread = CommitLoaderThread(directory, self.commit_limit, self.scope_input.text())
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

        self.update_table_active_state()
        self.status_label.setStyleSheet(f"color: {CP_GREEN}; font-weight: bold;")
        limit_text = f" (LIMIT: {self.commit_limit})" if self.commit_limit > 0 else " (ALL)"
        self.status_label.setText(f"LOADED {len(commits)} COMMITS{limit_text}")

        self.table.viewport().update()

    def update_table_active_state(self):
        """Update the table items to show which commit is active"""
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                is_active = item.text() == self.active_commit_hash
                # Set UserRole data for the whole row (delegates look at col 0)
                item.setData(Qt.ItemDataRole.UserRole, is_active)
        self.table.viewport().update()

    def filter_commits(self):
        """Client-side filter for the commit table"""
        search_text = self.search_input.text().strip().lower()
        for row in range(self.table.rowCount()):
            match = False
            # Check Hash, Author, and Message columns
            for col in [0, 2, 3]:
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

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
            scope = self.scope_input.text() or "."
            result = GitWorker.checkout_path(directory, commit_hash, scope)
            if "success" in result:
                self.active_commit_hash = commit_hash
                self.update_table_active_state()
                self.status_label.setStyleSheet(f"color: {CP_GREEN}; font-weight: bold;")
                self.status_label.setText(f"SUCCESS: RESTORED TO {commit_hash}")
                QMessageBox.information(self, "Success", f"Restored to {commit_hash}.")
            else:
                self.status_label.setStyleSheet(f"color: {CP_RED}; font-weight: bold;")
                self.status_label.setText("RESTORE FAILED")
                QMessageBox.critical(self, "Error", result['error'])

    def restore_files_to_current(self):
        """Replace current working files with the parent commit version (one commit before selected)"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Required", "Please select a commit.")
            return

        row = selected_items[0].row()
        commit_hash = self.table.item(row, 0).text()
        commit_msg = self.table.item(row, 3).text()
        directory = self.path_input.text()
        base_dir = GitWorker.get_git_root(directory)
        
        if not self.current_diff_sections:
            QMessageBox.information(self, "No Changes", "No files to restore. Select a commit first.")
            return
        
        target_files = [s['name'] for s in self.current_diff_sections]
        
        if not target_files:
            QMessageBox.information(self, "No Files", "No files found.")
            return

        # Use parent commit (commit before the selected one)
        parent_hash = f"{commit_hash}^"

        confirm = QMessageBox.question(
            self, "Replace with Previous Version",
            f"Replace current files with the version BEFORE:\n\n[{commit_hash}] {commit_msg}\n\n"
            f"Files to replace: {len(target_files)}\n\n"
            f"⚠️ This will use the parent commit ({parent_hash})",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.status_label.setText("REPLACING FILES...")
            self.status_label.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold;")
            QApplication.processEvents()
            
            success_count = 0
            failed = []
            
            for file_path in target_files:
                res = GitWorker.checkout_file(base_dir, parent_hash, file_path)
                if "success" in res:
                    success_count += 1
                    self.restored_files[file_path] = parent_hash
                else:
                    failed.append(file_path)
            
            self.render_diff_html()
            
            if success_count == len(target_files):
                self.status_label.setStyleSheet(f"color: {CP_GREEN}; font-weight: bold;")
                self.status_label.setText(f"SUCCESS: {success_count} FILE(S) REPLACED")
                QMessageBox.information(self, "Success", f"Replaced {success_count} file(s) with parent commit version.")
            else:
                self.status_label.setStyleSheet(f"color: {CP_RED}; font-weight: bold;")
                self.status_label.setText("REPLACE PARTIALLY FAILED")
                QMessageBox.warning(self, "Partial Success", f"Replaced {success_count} file(s).\nFailed: {len(failed)}")

    def restore_commit_files(self):
        """Restore only the files from the selected commit (not parent)"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Required", "Please select a commit.")
            return

        row = selected_items[0].row()
        commit_hash = self.table.item(row, 0).text()
        commit_msg = self.table.item(row, 3).text()
        directory = self.path_input.text()
        base_dir = GitWorker.get_git_root(directory)
        
        if not self.current_diff_sections:
            QMessageBox.information(self, "No Changes", "No files to restore. Select a commit first.")
            return
        
        target_files = [s['name'] for s in self.current_diff_sections]
        
        if not target_files:
            QMessageBox.information(self, "No Files", "No files found.")
            return

        confirm = QMessageBox.question(
            self, "Restore Commit Files",
            f"Restore files from commit:\n\n[{commit_hash}] {commit_msg}\n\n"
            f"Files to restore: {len(target_files)}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.status_label.setText("RESTORING FILES...")
            self.status_label.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold;")
            QApplication.processEvents()
            
            success_count = 0
            failed = []
            
            for file_path in target_files:
                res = GitWorker.checkout_file(base_dir, commit_hash, file_path)
                if "success" in res:
                    success_count += 1
                    self.restored_files[file_path] = commit_hash
                else:
                    failed.append(file_path)
            
            self.render_diff_html()
            
            if success_count == len(target_files):
                self.status_label.setStyleSheet(f"color: {CP_GREEN}; font-weight: bold;")
                self.status_label.setText(f"SUCCESS: {success_count} FILE(S) RESTORED")
                QMessageBox.information(self, "Success", f"Restored {success_count} file(s) from commit {commit_hash}.")
            else:
                self.status_label.setStyleSheet(f"color: {CP_RED}; font-weight: bold;")
                self.status_label.setText("RESTORE PARTIALLY FAILED")
                QMessageBox.warning(self, "Partial Success", f"Restored {success_count} file(s).\nFailed: {len(failed)}")


# --- SETTINGS DIALOG ---
class SettingsDialog(QDialog):
    def __init__(self, parent=None, width=1400, height=700, split_ratio=[2, 3]):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(500, 300)
        
        self.setStyleSheet(f"""
            QDialog {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QLabel {{ color: {CP_TEXT}; }}
            QSpinBox {{
                background-color: {CP_PANEL};
                color: {CP_CYAN};
                border: 1px solid {CP_DIM};
                padding: 5px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = QLabel("⚙️ WINDOW SETTINGS")
        header.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold; font-size: 14pt;")
        layout.addWidget(header)
        
        # Window Size
        size_group = QWidget()
        size_layout = QVBoxLayout(size_group)
        
        size_label = QLabel("Window Size:")
        size_label.setStyleSheet(f"color: {CP_CYAN}; font-weight: bold; margin-bottom: 5px;")
        size_layout.addWidget(size_label)
        
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("Width:"))
        self.width_spin = QInputDialog.getInt(self, "", "", width, 800, 3840, 1)[0] if False else None
        from PyQt6.QtWidgets import QSpinBox
        self.width_spin = QSpinBox()
        self.width_spin.setRange(800, 3840)
        self.width_spin.setValue(width)
        self.width_spin.setSuffix(" px")
        width_layout.addWidget(self.width_spin)
        size_layout.addLayout(width_layout)
        
        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("Height:"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(600, 2160)
        self.height_spin.setValue(height)
        self.height_spin.setSuffix(" px")
        height_layout.addWidget(self.height_spin)
        size_layout.addLayout(height_layout)
        
        layout.addWidget(size_group)
        
        # Split Ratio
        split_group = QWidget()
        split_layout = QVBoxLayout(split_group)
        
        split_label = QLabel("Panel Split Ratio:")
        split_label.setStyleSheet(f"color: {CP_CYAN}; font-weight: bold; margin-bottom: 5px;")
        split_layout.addWidget(split_label)
        
        left_layout = QHBoxLayout()
        left_layout.addWidget(QLabel("Left Panel (Table):"))
        self.left_spin = QSpinBox()
        self.left_spin.setRange(1, 10)
        self.left_spin.setValue(split_ratio[0])
        left_layout.addWidget(self.left_spin)
        split_layout.addLayout(left_layout)
        
        right_layout = QHBoxLayout()
        right_layout.addWidget(QLabel("Right Panel (Diff):"))
        self.right_spin = QSpinBox()
        self.right_spin.setRange(1, 10)
        self.right_spin.setValue(split_ratio[1])
        right_layout.addWidget(self.right_spin)
        split_layout.addLayout(right_layout)
        
        hint_label = QLabel("💡 Tip: Higher values = more space")
        hint_label.setStyleSheet(f"color: {CP_DIM}; font-size: 9pt; margin-top: 5px;")
        split_layout.addWidget(hint_label)
        
        layout.addWidget(split_group)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = CyberButton("CANCEL", CP_DIM, CP_RED)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = CyberButton("SAVE", CP_DIM, CP_GREEN)
        save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)

# --- FILE TIMELINE DIALOG ---
class FileTimelineDialog(QDialog):
    def __init__(self, parent, file_path, commits, active_hash=None):
        super().__init__(parent)
        self.setWindowTitle(f"Timeline: {os.path.basename(file_path)}")
        self.resize(800, 500)
        self.selected_commit = None
        self.active_hash = active_hash
        
        self.setStyleSheet(f"""
            QDialog {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
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
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header = QLabel(f"HISTORY FOR: {file_path}")
        header.setStyleSheet(f"color: {CP_CYAN}; font-weight: bold; font-size: 12pt;")
        layout.addWidget(header)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["HASH", "DATE", "MESSAGE"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setMouseTracking(True)

        # Apply Custom Delegate
        self.delegate = CyberDelegate(self.table)
        self.table.setItemDelegate(self.delegate)
        self.table.cellEntered.connect(self.on_cell_entered)
        self.table.leaveEvent = self.on_table_leave
        
        self.table.setRowCount(len(commits))
        for i, commit in enumerate(commits):
            items = [
                QTableWidgetItem(commit['hash']),
                QTableWidgetItem(commit['date']),
                QTableWidgetItem(commit['message'])
            ]
            
            items[0].setForeground(QColor(CP_YELLOW))
            items[1].setForeground(QColor(CP_TEXT))
            items[2].setForeground(QColor(CP_CYAN))
            
            for col, item in enumerate(items):
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(i, col, item)
            
            # Mark active
            if commit['hash'] == self.active_hash:
                items[0].setData(Qt.ItemDataRole.UserRole, True)
            
        layout.addWidget(self.table)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = CyberButton("CANCEL", CP_DIM, CP_RED)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        restore_btn = CyberButton("RESTORE THIS VERSION", CP_DIM, CP_GREEN)
        restore_btn.clicked.connect(self.accept_selection)
        btn_layout.addWidget(restore_btn)
        
        layout.addLayout(btn_layout)
        
    def on_cell_entered(self, row, column):
        self.delegate.hovered_row = row
        self.table.viewport().update()

    def on_table_leave(self, event):
        self.delegate.hovered_row = -1
        self.table.viewport().update()

    def accept_selection(self):
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            self.selected_commit = self.table.item(row, 0).text()
            self.accept()
        else:
            QMessageBox.warning(self, "Selection Required", "Please select a version to restore.")

# --- COMMIT EXPLORER DIALOG ---
class CommitExplorerDialog(QDialog):
    def __init__(self, parent, directory, commit_hash, files, root_path_to_strip=None):
        super().__init__(parent)
        self.setWindowTitle(f"Explorer: {commit_hash}")
        self.resize(900, 600)
        self.directory = directory
        self.commit_hash = commit_hash
        self.base_dir = GitWorker.get_git_root(directory)
        self.root_path_to_strip = root_path_to_strip
        
        self.setStyleSheet(f"""
            QDialog {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QTreeView {{
                background-color: #080808;
                border: 1px solid {CP_DIM};
                color: {CP_TEXT};
                outline: none;
            }}
            QTreeView::item {{ padding: 3px; }}
            QTreeView::item:hover {{ background-color: #1a1a1a; }}
            QTreeView::item:selected {{ background-color: #222222; color: {CP_YELLOW}; }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Determine the display header
        display_path = os.path.basename(directory) if root_path_to_strip else "ROOT"
        header = QLabel(f"REPO STATE: {display_path} @ {commit_hash}")
        header.setStyleSheet(f"color: {CP_CYAN}; font-weight: bold; font-size: 12pt;")
        layout.addWidget(header)
        
        self.tree_view = QTreeView()
        self.tree_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels([display_path])
        self.tree_view.setModel(self.model)
        
        # Icon Provider
        self.icon_provider = QFileIconProvider()
        
        # Build Tree
        self.build_tree(files)
        
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.tree_view)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = CyberButton("CLOSE", CP_DIM, CP_CYAN)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def build_tree(self, files):
        root_node = self.model.invisibleRootItem()
        nodes = {}
        
        prefix_len = 0
        if self.root_path_to_strip:
            # Ensure prefix ends with / for correct stripping
            prefix = self.root_path_to_strip if self.root_path_to_strip.endswith('/') else self.root_path_to_strip + '/'
            prefix_len = len(prefix)

        # Pre-process paths to ensure we build folders first and sort everything
        # 1. Strip prefix if needed
        processed_files = []
        for f in files:
            display_path = f[prefix_len:] if f.startswith(self.root_path_to_strip or "") else f
            if display_path:
                processed_files.append((display_path, f)) # (display, original)

        # 2. Sort processed files so folders naturally get processed
        # Sorting by display_path ensures we go level by level
        processed_files.sort(key=lambda x: x[0])

        for display_path, full_git_path in processed_files:
            parts = display_path.split('/')
            current_node = root_node
            
            path_so_far_for_restore = ""
            if self.root_path_to_strip:
                 path_so_far_for_restore = self.root_path_to_strip.rstrip('/')

            for i, part in enumerate(parts):
                # Build the display path segment
                display_segment_path = "/".join(parts[:i+1])
                
                # Build the actual git-compatible path for this node
                if path_so_far_for_restore:
                    actual_git_path = f"{path_so_far_for_restore}/{display_segment_path}"
                else:
                    actual_git_path = display_segment_path

                if display_segment_path not in nodes:
                    item = QStandardItem(part)
                    item.setData(actual_git_path, Qt.ItemDataRole.UserRole)
                    
                    is_file = (i == len(parts) - 1)
                    if not is_file:
                        item.setIcon(self.icon_provider.icon(QFileIconProvider.IconType.Folder))
                        item.setData("folder", Qt.ItemDataRole.UserRole + 1)
                    else:
                        item.setIcon(self.icon_provider.icon(QFileIconProvider.IconType.File))
                        item.setData("file", Qt.ItemDataRole.UserRole + 1)
                    
                    current_node.appendRow(item)
                    nodes[display_segment_path] = item
                current_node = nodes[display_segment_path]
        
        self.sort_tree_recursive(root_node)
    
    def sort_tree_recursive(self, parent_item):
        """Sort children: folders first, then files, alphabetically"""
        if parent_item.rowCount() == 0:
            return
        
        children = []
        for i in range(parent_item.rowCount()):
            children.append(parent_item.takeRow(0))
        
        children.sort(key=lambda row: (
            0 if row[0].data(Qt.ItemDataRole.UserRole + 1) == "folder" else 1,
            row[0].text().lower()
        ))
        
        for row in children:
            parent_item.appendRow(row)
            self.sort_tree_recursive(row[0])

    def show_context_menu(self, pos):
        index = self.tree_view.indexAt(pos)
        if not index.isValid(): return
        
        item = self.model.itemFromIndex(index)
        path = item.data(Qt.ItemDataRole.UserRole)
        type = item.data(Qt.ItemDataRole.UserRole + 1)
        
        menu = QMenu(self)
        menu.setStyleSheet(f"QMenu {{ background-color: {CP_PANEL}; color: {CP_TEXT}; border: 1px solid {CP_DIM}; }} QMenu::item:selected {{ background-color: {CP_CYAN}; color: black; }}")
        
        title = menu.addAction(f"{'📁' if type == 'folder' else '📄'} {os.path.basename(path)}")
        title.setEnabled(False)
        menu.addSeparator()
        
        if type == "file":
            action_restore = menu.addAction("⏮️ Restore this File")
            action_timeline = menu.addAction("📜 View File Timeline")
            
            selected = menu.exec(self.tree_view.viewport().mapToGlobal(pos))
            if selected == action_restore:
                self.parent().restore_file_by_path(path, self.commit_hash)
            elif selected == action_timeline:
                self.parent().open_timeline_by_path(path)
                
        else: # folder
            action_restore_folder = menu.addAction("📂 Restore Entire Folder")
            
            selected = menu.exec(self.tree_view.viewport().mapToGlobal(pos))
            if selected == action_restore_folder:
                self.parent().restore_file_by_path(path, self.commit_hash)

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
