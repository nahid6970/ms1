import sys
import json
import os
import ctypes
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QGroupBox, QScrollArea, 
                             QFrame, QMessageBox, QFileDialog, QProgressBar, QDialog,
                             QTreeView, QHeaderView)
from PyQt6.QtGui import QFont, QIcon, QColor, QFileSystemModel
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QDir

# ==========================================
# CYBERPUNK THEME PALETTE
# ==========================================
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_GREEN = "#00ff21"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"
CP_SUBTEXT = "#808080"

STYLESHEET = f"""
    QMainWindow {{ background-color: {CP_BG}; }}
    QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
    QLineEdit {{
        background-color: {CP_PANEL};
        color: {CP_CYAN};
        border: 1px solid {CP_DIM};
        padding: 6px;
    }}
    QLineEdit:focus {{ border: 1px solid {CP_CYAN}; }}
    QPushButton {{
        background-color: {CP_DIM};
        border: 1px solid {CP_DIM};
        color: white;
        padding: 8px 15px;
        font-weight: bold;
    }}
    QPushButton:hover {{ border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
    
    /* SIDEBAR BUTTONS */
    QFrame QPushButton {{
        background-color: {CP_DIM};
        border: 1px solid {CP_DIM};
        padding: 4px;
    }}
    QFrame QPushButton:hover {{
        border: 1px solid {CP_CYAN};
    }}
    
    QProgressBar {{
        border: 1px solid {CP_DIM};
        background: {CP_PANEL};
        text-align: center;
        color: {CP_YELLOW};
        height: 20px;
    }}
    QProgressBar::chunk {{ background-color: {CP_CYAN}; }}

    /* TREE VIEW */
    QTreeView {{
        background-color: #080808;
        border: 1px solid {CP_DIM};
        color: {CP_TEXT};
        outline: none;
    }}
    QTreeView::item:hover {{ background-color: #1a1a1a; }}
    QTreeView::item:selected {{ background-color: #222222; color: {CP_YELLOW}; }}
    QHeaderView::section {{
        background-color: {CP_PANEL};
        color: {CP_SUBTEXT};
        padding: 4px;
        border: 1px solid {CP_DIM};
    }}
"""

class SyncWorker(QThread):
    progress = pyqtSignal(int, int, str) # current, total, message
    finished = pyqtSignal(int, int) # success, failed

    def __init__(self, source, destination):
        super().__init__()
        self.source = os.path.normpath(source)
        self.destination = os.path.normpath(destination)

    def run(self):
        file_list = []
        for root, dirs, files in os.walk(self.source):
            for file in files:
                file_list.append(os.path.join(root, file))
        
        total = len(file_list)
        success = 0
        failed = 0

        for i, src_path in enumerate(file_list):
            rel_path = os.path.relpath(src_path, self.source)
            dst_path = os.path.join(self.destination, rel_path)
            dst_dir = os.path.dirname(dst_path)

            try:
                # Ensure destination directory exists (physical folder)
                if not os.path.exists(dst_dir):
                    os.makedirs(dst_dir, exist_ok=True)

                # Handle existing file/link at destination
                if os.path.exists(dst_path) or os.path.lexists(dst_path):
                    if os.path.islink(dst_path):
                        os.remove(dst_path)
                    else:
                        # If it's a real file and not a link, we skip it to be safe 
                        # (User said "match every file and create link", usually means replacing or skipping)
                        # We'll skip real files to avoid accidental data loss.
                        failed += 1
                        self.progress.emit(i+1, total, f"Skipped (Real file exists): {rel_path}")
                        continue

                # Create Symlink (File)
                cmd = f'mklink "{dst_path}" "{src_path}"'
                result = subprocess.run(f'cmd /c {cmd}', capture_output=True, text=True, shell=True)
                
                if result.returncode == 0:
                    success += 1
                    self.progress.emit(i+1, total, f"Linked: {rel_path}")
                else:
                    # Try admin elevation if needed
                    err = result.stderr.strip().lower()
                    if "privilege" in err or "access is denied" in err:
                        params = f'/c {cmd}'
                        ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", params, None, 0)
                        if ret > 32:
                            success += 1
                            self.progress.emit(i+1, total, f"Linked (Admin): {rel_path}")
                        else:
                            failed += 1
                            self.progress.emit(i+1, total, f"Failed (Admin Req): {rel_path}")
                    else:
                        failed += 1
                        self.progress.emit(i+1, total, f"Error: {rel_path}")

            except Exception as e:
                failed += 1
                self.progress.emit(i+1, total, f"Exception: {str(e)}")

        self.finished.emit(success, failed)

class MirrorSyncManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cyberpunk Mirror Symlink")
        self.resize(1100, 700)
        
        self.data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mirror_projects.json")
        self.projects = self.load_data()

        # Central Widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # LEFT SIDE: Project List
        left_panel = QFrame()
        left_panel.setFixedWidth(350)
        left_panel.setStyleSheet(f"background-color: {CP_PANEL}; border: 1px solid {CP_DIM};")
        left_layout = QVBoxLayout(left_panel)
        
        list_title = QLabel("PROJECTS")
        list_title.setStyleSheet(f"color: {CP_YELLOW}; font-weight: bold; font-size: 12pt;")
        left_layout.addWidget(list_title)

        self.project_list = QScrollArea()
        self.project_list.setWidgetResizable(True)
        self.project_list_content = QWidget()
        self.project_list_layout = QVBoxLayout(self.project_list_content)
        self.project_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.project_list.setWidget(self.project_list_content)
        left_layout.addWidget(self.project_list)

        add_proj_btn = QPushButton("➕ New Mirror Project")
        add_proj_btn.setStyleSheet(f"border-color: {CP_GREEN}; color: {CP_GREEN};")
        add_proj_btn.clicked.connect(self.open_add_dialog)
        left_layout.addWidget(add_proj_btn)

        main_layout.addWidget(left_panel)

        # RIGHT SIDE: Execution & Log
        right_layout = QVBoxLayout()
        
        self.selected_label = QLabel("Select a project...")
        self.selected_label.setStyleSheet(f"font-size: 14pt; font-weight: bold; color: {CP_CYAN};")
        right_layout.addWidget(self.selected_label)

        self.details_label = QLabel("")
        self.details_label.setWordWrap(True)
        self.details_label.setStyleSheet(f"color: {CP_SUBTEXT}; font-size: 9pt; margin-bottom: 5px;")
        right_layout.addWidget(self.details_label)

        # Split area for Tree and Log
        split_layout = QHBoxLayout()
        
        # Source Tree View
        self.tree_view = QTreeView()
        self.tree_model = QFileSystemModel()
        self.tree_model.setReadOnly(True)
        self.tree_view.setModel(self.tree_model)
        self.tree_view.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        # Hide columns: Size, Type, Date Modified
        for i in range(1, 4):
            self.tree_view.hideColumn(i)
        
        tree_container = QVBoxLayout()
        tree_container.addWidget(QLabel("SOURCE STRUCTURE:"))
        tree_container.addWidget(self.tree_view)
        split_layout.addLayout(tree_container, stretch=2)

        # Log Area
        log_container = QVBoxLayout()
        log_container.addWidget(QLabel("ACTIVITY LOG:"))
        self.log_area = QScrollArea()
        self.log_area.setWidgetResizable(True)
        self.log_content = QLabel("Ready...")
        self.log_content.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.log_content.setStyleSheet(f"color: {CP_SUBTEXT}; font-size: 9pt; padding: 10px; background-color: #080808;")
        self.log_area.setWidget(self.log_content)
        log_container.addWidget(self.log_area)
        split_layout.addLayout(log_container, stretch=3)

        right_layout.addLayout(split_layout)

        # Progress (Above Rocket Button)
        self.progress_bar = QProgressBar()
        right_layout.addWidget(self.progress_bar)

        self.sync_btn = QPushButton("🚀 START MIRROR SYNC")
        self.sync_btn.setFixedHeight(50)
        self.sync_btn.setEnabled(False)
        self.sync_btn.setStyleSheet(f"""
            QPushButton {{ 
                background-color: {CP_DIM}; 
                border: 1px solid {CP_GREEN}; 
                color: {CP_GREEN}; 
                font-size: 12pt; 
            }}
            QPushButton:hover {{ background-color: {CP_GREEN}; color: black; }}
            QPushButton:disabled {{ 
                background-color: #0a0a0a;
                border: 1px solid #222222; 
                color: #444444; 
            }}
        """)
        self.sync_btn.clicked.connect(self.start_sync)
        right_layout.addWidget(self.sync_btn)

        main_layout.addLayout(right_layout, stretch=1)

        self.current_project = None
        self.refresh_ui()

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_data(self):
        with open(self.data_file, "w") as f:
            json.dump(self.projects, f, indent=4)

    def refresh_ui(self):
        while self.project_list_layout.count():
            child = self.project_list_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        for i, proj in enumerate(self.projects):
            item_frame = QFrame()
            item_frame.setStyleSheet(f"border: none; border-bottom: 1px solid {CP_DIM}; background-color: transparent;")
            item_layout = QHBoxLayout(item_frame)
            item_layout.setContentsMargins(2, 2, 2, 2)
            item_layout.setSpacing(5)

            btn = QPushButton(proj["name"])
            btn.setStyleSheet("text-align: left; padding: 8px; border: none; font-weight: bold; background: transparent;")
            btn.clicked.connect(lambda checked, idx=i: self.select_project(idx))
            item_layout.addWidget(btn, stretch=1)

            edit_btn = QPushButton("📝")
            edit_btn.setFixedSize(35, 35)
            edit_btn.setStyleSheet(f"color: {CP_YELLOW}; border: 1px solid {CP_DIM}; background-color: {CP_BG};")
            edit_btn.clicked.connect(lambda checked, idx=i: self.open_add_dialog(edit_index=idx))
            item_layout.addWidget(edit_btn)

            del_btn = QPushButton("🗑️")
            del_btn.setFixedSize(35, 35)
            del_btn.setStyleSheet(f"color: {CP_RED}; border: 1px solid {CP_DIM}; background-color: {CP_BG};")
            del_btn.clicked.connect(lambda checked, idx=i: self.delete_project(idx))
            item_layout.addWidget(del_btn)

            self.project_list_layout.addWidget(item_frame)

    def select_project(self, index):
        self.current_project = self.projects[index]
        self.selected_label.setText(self.current_project["name"])
        self.details_label.setText(f"SOURCE: {self.current_project['source']}\nDEST: {self.current_project['destination']}")
        
        # Update Tree View
        src_path = self.current_project['source']
        if os.path.exists(src_path):
            self.tree_model.setRootPath(src_path)
            self.tree_view.setRootIndex(self.tree_model.index(src_path))
        
        self.sync_btn.setEnabled(True)
        self.log_content.setText("Project loaded. Click Start to begin.")

    def delete_project(self, index):
        proj = self.projects[index]
        if QMessageBox.question(self, "Delete", f"Remove project '{proj['name']}'?") == QMessageBox.StandardButton.Yes:
            self.projects.pop(index)
            self.save_data()
            self.refresh_ui()
            if self.current_project == proj:
                self.current_project = None
                self.selected_label.setText("Select a project...")
                self.details_label.setText("")
                self.sync_btn.setEnabled(False)

    def open_add_dialog(self, edit_index=None):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Project" if edit_index is not None else "New Mirror Project")
        dialog.resize(900, 350)
        d_layout = QVBoxLayout(dialog)

        proj_data = self.projects[edit_index] if edit_index is not None else {}

        name_in = QLineEdit(proj_data.get("name", ""))
        name_in.setPlaceholderText("Project Name")
        d_layout.addWidget(QLabel("Name:"))
        d_layout.addWidget(name_in)

        src_in = QLineEdit(proj_data.get("source", ""))
        src_btn = QPushButton("📂 Browse Source")
        src_btn.clicked.connect(lambda: src_in.setText(QFileDialog.getExistingDirectory(dialog, "Select Source", src_in.text())))
        d_layout.addWidget(QLabel("Source Root:"))
        h1 = QHBoxLayout()
        h1.addWidget(src_in)
        h1.addWidget(src_btn)
        d_layout.addLayout(h1)

        dst_in = QLineEdit(proj_data.get("destination", ""))
        dst_btn = QPushButton("📂 Browse Destination")
        dst_btn.clicked.connect(lambda: dst_in.setText(QFileDialog.getExistingDirectory(dialog, "Select Destination", dst_in.text())))
        d_layout.addWidget(QLabel("Destination Root:"))
        h2 = QHBoxLayout()
        h2.addWidget(dst_in)
        h2.addWidget(dst_btn)
        d_layout.addLayout(h2)

        save_btn = QPushButton("Save Project")
        save_btn.clicked.connect(dialog.accept)
        d_layout.addWidget(save_btn)

        if dialog.exec():
            name = name_in.text().strip()
            src = src_in.text().strip()
            dst = dst_in.text().strip()
            if name and src and dst:
                new_data = {"name": name, "source": src, "destination": dst}
                if edit_index is not None:
                    self.projects[edit_index] = new_data
                else:
                    self.projects.append(new_data)
                self.save_data()
                self.refresh_ui()

    def start_sync(self):
        if not self.current_project: return
        
        self.sync_btn.setEnabled(False)
        self.log_content.setText("Scanning...")
        
        self.worker = SyncWorker(self.current_project["source"], self.current_project["destination"])
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.sync_finished)
        self.worker.start()

    def update_progress(self, current, total, message):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.log_content.setText(f"[{current}/{total}] {message}\n" + self.log_content.text()[:5000])

    def sync_finished(self, success, failed):
        self.sync_btn.setEnabled(True)
        QMessageBox.information(self, "Complete", f"Sync Finished.\nSuccess: {success}\nFailed: {failed}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = MirrorSyncManager()
    window.show()
    sys.exit(app.exec())
