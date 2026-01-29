import sys
import os
import subprocess
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QCursor

# --- THEME CONSTANTS (from THEME_GUIDE.md) ---
CP_BG = "#050505"           # Main Window Background
CP_PANEL = "#111111"        # Panel/Input Background
CP_YELLOW = "#FCEE0A"       # Accent: Yellow
CP_CYAN = "#00F0FF"         # Accent: Cyan
CP_RED = "#FF003C"          # Accent: Red
CP_GREEN = "#00ff21"        # Accent: Green
CP_DIM = "#3a3a3a"          # Dimmed/Borders/Inactive
CP_TEXT = "#E0E0E0"         # Primary Text

# --- GIT LOGIC ---
class GitWorker:
    @staticmethod
    def get_commits(directory):
        """
        Returns a list of dictionaries containing commit info.
        Format: Hash, Author, Date, Message
        """
        if not os.path.isdir(directory):
            return {"error": "Invalid directory"}
        
        # Check if it's a git repo
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
            # git log format: hash|author|date|message
            # Explicitly add "-- ." to filter log to the current directory
            cmd = ["git", "log", "--pretty=format:%h|%an|%ad|%s", "--date=short", "-n", "200", "--", "."]
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
    def checkout_path(directory, commit_hash):
        """
        Reverts the files in 'directory' to the state at 'commit_hash'.
        Uses: git checkout <hash> -- .
        """
        try:
            cmd = ["git", "checkout", commit_hash, "--", "."]
            subprocess.check_call(cmd, cwd=directory)
            return {"success": True}
        except subprocess.CalledProcessError as e:
            return {"error": f"Git Error: {e}"}
        except Exception as e:
            return {"error": str(e)}

# --- UI COMPONENTS ---

class CyberButton(QPushButton):
    def __init__(self, text, color=CP_DIM, hover_color=CP_YELLOW, text_color="white", hover_text_color="black"):
        super().__init__(text)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.default_style = f"""
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
        """
        self.setStyleSheet(self.default_style)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Git Time Machine // CYBERPUNK EDITION")
        self.resize(1000, 700)
        
        # Calculate config path relative to the script location
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "git_history_config.json")

        # Global Stylesheet
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
                selection-background-color: {CP_CYAN};
                selection-color: {CP_BG};
            }}
            QHeaderView::section {{
                background-color: {CP_DIM};
                color: {CP_YELLOW};
                padding: 4px;
                border: 1px solid {CP_PANEL};
                font-weight: bold;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {CP_BG};
                width: 10px;
            }}
            QScrollBar::handle:vertical {{
                background: {CP_DIM};
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """
        )

        # Main Layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 1. Path Selection Area
        path_layout = QHBoxLayout()
        
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select Git Directory...")
        
        # Load last path or default to current
        last_path = self.load_config()
        if last_path and os.path.isdir(last_path):
            self.path_input.setText(last_path)
        else:
            self.path_input.setText(os.getcwd())
            
        self.path_input.returnPressed.connect(self.load_commits)
        
        browse_btn = CyberButton("BROWSE", CP_DIM, CP_CYAN)
        browse_btn.clicked.connect(self.browse_directory)
        
        load_btn = CyberButton("LOAD COMMITS", CP_DIM, CP_YELLOW)
        load_btn.clicked.connect(self.load_commits)

        path_layout.addWidget(QLabel("DIR:"))
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_btn)
        path_layout.addWidget(load_btn)
        
        layout.addLayout(path_layout)

        # 2. Commit List (Table)
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["HASH", "DATE", "AUTHOR", "MESSAGE"])
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch) # Message stretches
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        # Customizing alternating colors is tricky in pure stylesheet for QTableWidget, 
        # so relying on basic CP_PANEL bg.
        
        layout.addWidget(self.table)

        # 3. Action Area
        action_layout = QHBoxLayout()
        
        self.status_label = QLabel("READY")
        self.status_label.setStyleSheet(f"color: {CP_CYAN}; font-weight: bold;")
        
        revert_btn = CyberButton("RESTORE SELECTED VERSION", CP_DIM, CP_RED, "white", "black")
        revert_btn.clicked.connect(self.revert_commit)
        
        action_layout.addWidget(self.status_label)
        action_layout.addStretch()
        action_layout.addWidget(revert_btn)
        
        layout.addLayout(action_layout)

        # Initial Load if path exists
        if os.path.isdir(self.path_input.text()):
            self.load_commits()

    def load_config(self):
        """Loads the last directory from json config."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    return data.get("last_directory", "")
        except Exception as e:
            print(f"Error loading config: {e}")
        return ""

    def save_config(self, directory):
        """Saves the current directory to json config."""
        try:
            data = {"last_directory": directory}
            with open(self.config_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving config: {e}")

    def browse_directory(self):
        start_dir = self.path_input.text() if os.path.isdir(self.path_input.text()) else os.getcwd()
        directory = QFileDialog.getExistingDirectory(self, "Select Git Repository", start_dir)
        if directory:
            self.path_input.setText(directory)
            self.load_commits()

    def load_commits(self):
        directory = self.path_input.text().strip()
        if not directory:
            return

        # Save config on successful load attempt
        if os.path.isdir(directory):
            self.save_config(directory)

        self.table.setRowCount(0)
        self.status_label.setText("LOADING...")
        QApplication.processEvents()

        result = GitWorker.get_commits(directory)
        
        if "error" in result:
            self.status_label.setStyleSheet(f"color: {CP_RED};")
            self.status_label.setText(f"ERROR: {result['error']}")
            QMessageBox.critical(self, "Error", result['error'])
            return

        commits = result["success"]
        self.table.setRowCount(len(commits))
        
        for i, commit in enumerate(commits):
            # Create Items
            item_hash = QTableWidgetItem(commit['hash'])
            item_date = QTableWidgetItem(commit['date'])
            item_auth = QTableWidgetItem(commit['author'])
            item_msg = QTableWidgetItem(commit['message'])
            
            # Formatting
            for item in [item_hash, item_date, item_auth, item_msg]:
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable) # Read only
            
            item_hash.setForeground(QColor(CP_YELLOW))
            item_date.setForeground(QColor(CP_TEXT))
            item_auth.setForeground(QColor(CP_CYAN))
            item_msg.setForeground(QColor(CP_TEXT))

            self.table.setItem(i, 0, item_hash)
            self.table.setItem(i, 1, item_date)
            self.table.setItem(i, 2, item_auth)
            self.table.setItem(i, 3, item_msg)

        self.status_label.setStyleSheet(f"color: {CP_GREEN}; font-weight: bold;")
        self.status_label.setText(f"LOADED {len(commits)} COMMITS")

    def revert_commit(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Required", "Please select a commit to restore from.")
            return

        # Row index of selection
        row = selected_items[0].row()
        commit_hash = self.table.item(row, 0).text()
        commit_msg = self.table.item(row, 3).text()
        directory = self.path_input.text()

        confirm = QMessageBox.question(
            self,
            "Confirm Restore",
            f"Are you sure you want to replace ALL files in:\n{directory}\n\nWith files from commit:\n[{commit_hash}] {commit_msg}?\n\n(Current uncommitted changes will be lost!)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.status_label.setText("RESTORING...")
            QApplication.processEvents()
            
            result = GitWorker.checkout_path(directory, commit_hash)
            
            if "success" in result:
                self.status_label.setStyleSheet(f"color: {CP_GREEN}; font-weight: bold;")
                self.status_label.setText(f"SUCCESS: RESTORED TO {commit_hash}")
                QMessageBox.information(self, "Success", f"Directory restored to state of commit {commit_hash}.\nFiles are staged for commit.")
            else:
                self.status_label.setStyleSheet(f"color: {CP_RED}; font-weight: bold;")
                self.status_label.setText("RESTORE FAILED")
                QMessageBox.critical(self, "Error", result['error'])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())