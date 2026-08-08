import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QGroupBox, QFormLayout, 
                             QFileDialog, QTextEdit, QDialog, QCheckBox, QProgressBar, 
                             QTabWidget, QPlainTextEdit, QTreeWidget, QTreeWidgetItem, QSplitter)
from PyQt6.QtCore import Qt, QTimer

# CYBERPUNK THEME PALETTE
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_GREEN = "#00ff21"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"

# File extensions treated as text (compared only when "text files only" is enabled)
TEXT_EXTENSIONS = {
    '.json', '.txt', '.html', '.htm', '.xml', '.yaml', '.yml', '.csv', '.tsv',
    '.md', '.ini', '.cfg', '.conf', '.log', '.toml', '.sql', '.env',
    '.py', '.js', '.ts', '.jsx', '.tsx', '.css', '.scss', '.sass', '.less',
    '.bat', '.cmd', '.sh', '.ps1', '.rb', '.go', '.java', '.c', '.cpp', '.h',
    '.cs', '.php', '.swift', '.kt', '.rs', '.vue', '.svelte', '.json5', '.lock'
}

# Filenames without a useful extension that should still count as text
TEXT_FILENAMES = {'.gitignore', '.dockerignore', '.editorconfig', '.npmrc', 'dockerfile'}

# Where the app remembers its settings
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

# Default ignored folders (one per line, editable in Settings)
DEFAULT_IGNORE_TEXT = "\n".join([
    "node_modules", ".git", "__pycache__", "dist", "build",
    "venv", ".venv", ".cache", ".idea", ".vscode", "target",
])

class SettingsDialog(QDialog):
    def __init__(self, parent=None, ignore_text=""):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(420, 380)
        self.setStyleSheet(self.parent().styleSheet())
        layout = QVBoxLayout(self)
        
        tabs = QTabWidget()
        
        # Tab: Ignore Folders
        ignore_tab = QWidget()
        ignore_layout = QVBoxLayout(ignore_tab)
        hint = QLabel("One folder name per line. These folders are skipped during scanning (matched by name at any depth, case-insensitive).")
        hint.setWordWrap(True)
        self.ignore_edit = QPlainTextEdit()
        self.ignore_edit.setPlainText(ignore_text)
        self.ignore_edit.setPlaceholderText("node_modules\n.git\n__pycache__\n...")
        ignore_layout.addWidget(hint)
        ignore_layout.addWidget(self.ignore_edit)
        tabs.addTab(ignore_tab, "Ignore Folders")
        
        layout.addWidget(tabs)
        
        # Save / Cancel
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_save = QPushButton("SAVE")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.clicked.connect(self.accept)
        btn_cancel = QPushButton("CANCEL")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_cancel)
        layout.addLayout(btn_row)
    
    def get_ignore_text(self):
        return self.ignore_edit.toPlainText()

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cyberpunk Folder Scanner")
        self.resize(800, 600)
        
        # Apply Global Theme
        self.setStyleSheet(f"""
            QMainWindow, QDialog {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            
            QLineEdit, QTextEdit, QPlainTextEdit {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px;
                selection-background-color: {CP_CYAN}; selection-color: #000000;
            }}
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{ border: 1px solid {CP_CYAN}; }}
            
            QTabWidget::pane {{ border: 1px solid {CP_DIM}; background: {CP_BG}; }}
            QTabBar::tab {{
                background: {CP_PANEL}; color: {CP_TEXT}; padding: 6px 14px;
                border: 1px solid {CP_DIM}; border-bottom: none; font-weight: bold;
            }}
            QTabBar::tab:hover {{ border: 1px solid {CP_CYAN}; color: {CP_CYAN}; }}
            QTabBar::tab:selected {{ background: {CP_YELLOW}; color: black; }}
            
            QPushButton {{
                background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 6px 12px; font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW};
            }}
            QPushButton:pressed {{
                background-color: {CP_YELLOW}; color: black;
            }}
            
            QCheckBox {{ color: {CP_TEXT}; spacing: 8px; }}
            QCheckBox::indicator {{
                width: 16px; height: 16px; border: 1px solid {CP_DIM}; background-color: {CP_PANEL};
            }}
            QCheckBox::indicator:hover {{ border: 1px solid {CP_CYAN}; }}
            QCheckBox::indicator:checked {{
                background-color: {CP_YELLOW}; border: 1px solid {CP_YELLOW};
            }}
            
            QStatusBar {{
                background: {CP_BG}; border-top: 1px solid {CP_DIM}; color: {CP_TEXT};
            }}
            QStatusBar::item {{ border: none; }}
            QProgressBar {{
                background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; border-radius: 2px;
            }}
            QProgressBar::chunk {{ background-color: {CP_CYAN}; }}
            
            QLabel#scanLabel {{ color: {CP_CYAN}; font-size: 9pt; }}
            
            QTreeWidget {{
                background-color: #0a0a0a; color: {CP_TEXT}; border: 1px solid {CP_DIM};
                alternate-background-color: #0d0d0d;
            }}
            QTreeWidget::item {{ padding: 2px 4px; }}
            QTreeWidget::item:hover {{ background-color: #1c1c1c; }}
            QTreeWidget::item:selected {{ background-color: {CP_YELLOW}; color: #000000; }}
            QHeaderView::section {{
                background-color: {CP_PANEL}; color: {CP_YELLOW}; border: 1px solid {CP_DIM};
                padding: 4px; font-weight: bold;
            }}
            QSplitter::handle {{ background-color: {CP_DIM}; }}
            
            QGroupBox {{
                border: 1px solid {CP_DIM}; margin-top: 10px; padding-top: 10px; font-weight: bold; color: {CP_YELLOW};
            }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
            
            QScrollBar:vertical {{ background: {CP_BG}; width: 10px; margin: 0px; }}
            QScrollBar::handle:vertical {{ background: {CP_CYAN}; min-height: 20px; border-radius: 5px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; background: none; }}
            
            QScrollBar:horizontal {{ background: {CP_BG}; height: 10px; margin: 0px; }}
            QScrollBar::handle:horizontal {{ background: {CP_CYAN}; min-width: 20px; border-radius: 5px; }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; background: none; }}
        """)

        self.snapshot = {}
        self.ignore_text = DEFAULT_IGNORE_TEXT
        
        # Layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Top bar: Restart & Settings
        top_bar = QHBoxLayout()
        self.btn_restart = QPushButton("↺ RESTART")
        self.btn_restart.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_restart.clicked.connect(self.restart_app)
        
        self.btn_settings = QPushButton("⚙ SETTINGS")
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.clicked.connect(self.open_settings)
        
        # Filter search box (filters the file tree below)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter file tree...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setToolTip("Type to filter the file tree below (matches folder/file paths).")
        # Debounce filtering so typing stays smooth even on huge trees
        self._filter_timer = QTimer(self)
        self._filter_timer.setSingleShot(True)
        self._filter_timer.setInterval(150)
        self._filter_timer.timeout.connect(self.apply_filter)
        self.search_input.textChanged.connect(self._schedule_filter)
        
        top_bar.addWidget(self.search_input, 1)
        top_bar.addWidget(self.btn_settings)
        top_bar.addWidget(self.btn_restart)
        layout.addLayout(top_bar)

        # Folder Selection
        grp = QGroupBox("DIRECTORY SCANNER")
        form = QFormLayout()
        
        self.folder_input = QLineEdit()
        # Default to current directory
        self.folder_input.setText(os.path.dirname(__file__))
        self.btn_browse = QPushButton("BROWSE")
        self.btn_browse.clicked.connect(self.browse_folder)
        
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(self.btn_browse)
        
        form.addRow("Target Folder:", folder_layout)

        self.only_text_files = QCheckBox("Only compare text files (json, txt, html, xml, csv, md, code, ...)")
        self.only_text_files.setChecked(True)
        self.only_text_files.setCursor(Qt.CursorShape.PointingHandCursor)
        self.only_text_files.setToolTip("Only take snapshots and compare files with text extensions (json, txt, html, etc.).")
        form.addRow("", self.only_text_files)
        grp.setLayout(form)
        layout.addWidget(grp)
        
        # Actions
        action_layout = QHBoxLayout()
        self.btn_scan = QPushButton("TAKE SNAPSHOT")
        self.btn_scan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_scan.clicked.connect(self.take_snapshot)
        
        self.btn_check = QPushButton("CHECK CHANGES")
        self.btn_check.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_check.clicked.connect(self.check_changes)
        
        action_layout.addWidget(self.btn_scan)
        action_layout.addWidget(self.btn_check)
        layout.addLayout(action_layout)
        
        # Output + live file tree (vertical splitter)
        splitter = QSplitter(Qt.Orientation.Vertical)
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Name"])
        self.tree_widget.setAlternatingRowColors(True)
        splitter.addWidget(self.output_area)
        splitter.addWidget(self.tree_widget)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        layout.addWidget(splitter, 1)
        
        # Slim progress bar + status text pinned to the bottom of the window
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setVisible(False)
        self.progress_label = QLabel("Ready.")
        self.progress_label.setObjectName("scanLabel")
        status = self.statusBar()
        status.addWidget(self.progress_label)
        status.addWidget(self.progress_bar, 1)
        
        # Persist settings whenever anything changes, then restore saved values
        self.folder_input.textChanged.connect(lambda *_: self.save_settings())
        self.only_text_files.stateChanged.connect(lambda *_: self.save_settings())
        self.load_settings()
        self.ensure_gitignore()

    def save_settings(self):
        """Write the current UI settings to settings.json."""
        if getattr(self, '_suppress_save', False):
            return
        data = {
            "target_folder": self.folder_input.text(),
            "only_text_files": self.only_text_files.isChecked(),
            "ignore_folders": self.ignore_text,
        }
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception:
            pass

    def load_settings(self):
        """Restore saved settings from settings.json (if it exists)."""
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            return
        # Suppress the auto-save that setText/setChecked would trigger
        self._suppress_save = True
        try:
            if data.get("target_folder"):
                self.folder_input.setText(data["target_folder"])
            self.only_text_files.setChecked(bool(data.get("only_text_files", True)))
            # Key-presence check so an intentionally emptied list stays empty
            if "ignore_folders" in data:
                self.ignore_text = data["ignore_folders"]
        finally:
            self._suppress_save = False

    def ensure_gitignore(self):
        """Make sure settings.json is listed in the local .gitignore."""
        gi_path = os.path.join(os.path.dirname(__file__), ".gitignore")
        try:
            content = ""
            if os.path.exists(gi_path):
                with open(gi_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            if "settings.json" not in content.splitlines():
                entry = "settings.json\n"
                if content and not content.endswith("\n"):
                    entry = "\n" + entry
                with open(gi_path, 'a', encoding='utf-8') as f:
                    f.write(entry)
        except Exception:
            pass

    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.folder_input.setText(folder)

    def is_text_file(self, path):
        """Return True if the file has a text extension / is a known text filename."""
        name = os.path.basename(path).lower()
        return os.path.splitext(name)[1] in TEXT_EXTENSIONS or name in TEXT_FILENAMES

    def get_ignored_folders(self):
        """Parse the ignore-folders text into a set of lowercase folder names.
        Accepts one name per line (Settings) or comma/semicolon-separated."""
        raw = self.ignore_text.replace(';', ',')
        names = [n for part in raw.split(',') for n in part.splitlines()]
        return {name.strip().lower() for name in names if name.strip()}

    def scan_start(self):
        self.btn_scan.setEnabled(False)
        self.btn_check.setEnabled(False)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(True)
        self.progress_label.setText("Scanning...")
        QApplication.processEvents()

    def scan_end(self):
        self._flush_tree()
        self._finalize_tree()
        if self.search_input.text().strip():
            self.apply_filter()
        self.progress_bar.setVisible(False)
        self.btn_scan.setEnabled(True)
        self.btn_check.setEnabled(True)
        self.progress_label.setText("Ready.")
        QApplication.processEvents()

    def update_progress(self, path, count):
        """Show the current file being scanned in the bottom status bar. Throttled for speed."""
        if count > 20 and count % 50 != 0:
            return
        # Truncate long paths so the status bar doesn't stretch the window
        display = path if len(path) <= 80 else "..." + path[-(80 - 3):]
        self.progress_label.setText(f"Scanning ({count} files) ... {display}")
        self._flush_tree()
        QApplication.processEvents()

    # ---- Live file tree (folder/file view with counts) ----

    def tree_start(self, folder):
        """Reset the tree widget and add the root item for a new scan."""
        self.tree_widget.clear()
        self._tree_items = {}
        self._tree_counts = {}
        self._tree_buffer = set()
        norm = os.path.normpath(folder)
        name = os.path.basename(norm.rstrip("\\/")) or norm
        root = QTreeWidgetItem([f"{name}  (0)"])
        root.setData(0, Qt.ItemDataRole.UserRole, ("dir", norm))
        root.setExpanded(True)
        self.tree_widget.addTopLevelItem(root)
        self._tree_items[norm] = root
        self._tree_counts[norm] = [0, 0]

    def _ensure_dir_item(self, dirpath):
        """Return (creating if needed) the tree item for a directory path."""
        norm = os.path.normpath(dirpath)
        item = self._tree_items.get(norm)
        if item is not None:
            return item
        parent_norm = os.path.normpath(os.path.dirname(norm))
        parent = self._tree_items.get(parent_norm)
        if parent is None:
            if parent_norm == norm:  # safety guard against drive-root loops
                return self.tree_widget.topLevelItem(0)
            parent = self._ensure_dir_item(parent_norm)
        name = os.path.basename(norm) or norm
        item = QTreeWidgetItem([name])
        item.setData(0, Qt.ItemDataRole.UserRole, ("dir", norm))
        parent.addChild(item)
        self._tree_items[norm] = item
        self._tree_counts.setdefault(norm, [0, 0])
        return item

    def _sort_children(self, parent):
        """Sort children of a tree item: folders first (by count descending), then files."""
        children = []
        for i in range(parent.childCount()):
            children.append(parent.takeChild(0))
        
        def get_sort_key(item):
            data = item.data(0, Qt.ItemDataRole.UserRole)
            # Folders (dir) first, then files
            if data[0] == "dir":
                count = self._tree_counts.get(data[1], [0, 0])[1]
                return (0, -count)  # 0 for folder, negative count for descending order
            return (1, item.text(0))  # 1 for file, alphabetical order
        
        children.sort(key=get_sort_key)
        for child in children:
            parent.addChild(child)
            # Recursively sort children if it's a directory
            if child.data(0, Qt.ItemDataRole.UserRole)[0] == "dir":
                self._sort_children(child)

    def _add_tree_file(self, root, f):
        """Add one file to the tree and buffer its folder so labels refresh in batches."""
        pn = os.path.normpath(root)
        parent = self._tree_items.get(pn)
        if parent is None:
            parent = self._ensure_dir_item(pn)
        counts = self._tree_counts.setdefault(pn, [0, 0])
        counts[0] += 1
        cur = pn
        while cur in self._tree_counts:
            self._tree_counts[cur][1] += 1
            nxt = os.path.normpath(os.path.dirname(cur))
            if nxt == cur:
                break
            cur = nxt
        item = QTreeWidgetItem([f])
        item.setData(0, Qt.ItemDataRole.UserRole, ("file", os.path.normpath(os.path.join(root, f))))
        parent.addChild(item)
        self._sort_children(parent)
        self._tree_buffer.add(pn)

    def _set_tree_label(self, pn):
        """Refresh one folder item's text with its current recursive file count."""
        item = self._tree_items.get(pn)
        if item is None:
            return
        total = self._tree_counts.get(pn, [0, 0])[1]
        name = os.path.basename(pn) or pn
        item.setText(0, f"{name}  ({total})")

    def _flush_tree(self):
        """Apply buffered additions: refresh labels of affected folders AND their ancestors."""
        if not getattr(self, '_tree_buffer', None):
            return
        refresh = set()
        for pn in self._tree_buffer:
            cur = pn
            while cur in self._tree_counts:
                refresh.add(cur)
                nxt = os.path.normpath(os.path.dirname(cur))
                if nxt == cur:
                    break
                cur = nxt
        for pn in refresh:
            self._set_tree_label(pn)
            item = self._tree_items.get(pn)
            if item:
                parent = item.parent()
                if parent:
                    self._sort_children(parent)
        self._tree_buffer = set()
        # Keep an active filter applied live while new items stream in
        if self.search_input.text().strip():
            self._schedule_filter()

    def _finalize_tree(self):
        """After a scan: refresh every folder label once, then expand root + first level."""
        # Sort all folders by count
        for pn in self._tree_items:
            self._sort_children(self._tree_items[pn])
            self._set_tree_label(pn)
        
        root = self.tree_widget.topLevelItem(0)
        if root is None:
            return
        root.setExpanded(True)
        for i in range(root.childCount()):
            root.child(i).setExpanded(True)

    # ---- Tree filter search box ----

    def _schedule_filter(self):
        """Debounced entry point: restart the timer so filtering happens after typing pauses."""
        self._filter_timer.start()

    def apply_filter(self):
        """Filter the tree by path substring (case-insensitive). Applies immediately."""
        query = self.search_input.text().strip().lower()
        root = self.tree_widget.topLevelItem(0)
        if root is None:
            return
        if not query:
            self._show_all(root)
            return  # leave expansion state untouched
        self._apply_filter_item(root, query)

    def _show_all(self, item):
        item.setHidden(False)
        for i in range(item.childCount()):
            self._show_all(item.child(i))

    def _apply_filter_item(self, item, query):
        """Hide items that don't match; a folder stays visible if any descendant matches."""
        if item.childCount() == 0:
            path = item.data(0, Qt.ItemDataRole.UserRole)[1].lower()
            visible = query in path
            item.setHidden(not visible)
            return visible
        any_visible = False
        for i in range(item.childCount()):
            if self._apply_filter_item(item.child(i), query):
                any_visible = True
        item.setHidden(not any_visible)
        if any_visible:
            item.setExpanded(True)
        return any_visible

    def get_file_state(self, folder, text_only=False, progress_cb=None, tree_cb=None):
        state = {}
        ignored = self.get_ignored_folders()
        count = 0
        for root, dirs, files in os.walk(folder):
            # Prune ignored directories so os.walk never descends into them
            dirs[:] = [d for d in dirs if d.lower() not in ignored]
            for f in files:
                filepath = os.path.join(root, f)
                count += 1
                if progress_cb:
                    progress_cb(filepath, count)
                if text_only and not self.is_text_file(filepath):
                    continue
                if tree_cb:
                    tree_cb(root, f)
                try:
                    state[filepath] = os.path.getmtime(filepath)
                except Exception:
                    pass
        return state

    def take_snapshot(self):
        folder = self.folder_input.text()
        if not os.path.isdir(folder):
            self.log(f"<span style='color:{CP_RED};'>ERROR: Invalid directory.</span>")
            return
            
        # Remember which filter mode the snapshot was taken with
        self.text_only_enabled = self.only_text_files.isChecked()
        self.tree_start(folder)
        self.scan_start()
        try:
            self.snapshot = self.get_file_state(folder, text_only=self.text_only_enabled,
                                                progress_cb=self.update_progress, tree_cb=self._add_tree_file)
        finally:
            self.scan_end()
        mode = "text files only" if self.text_only_enabled else "all files"
        self.log(f"Snapshot taken for {len(self.snapshot)} files ({mode}) in {folder}.")

    def check_changes(self):
        folder = self.folder_input.text()
        if not os.path.isdir(folder):
            self.log(f"<span style='color:{CP_RED};'>ERROR: Invalid directory.</span>")
            return
            
        if not self.snapshot:
            self.log(f"<span style='color:{CP_RED};'>ERROR: No snapshot found. Please take a snapshot first.</span>")
            return
            
        # Use the same filter mode the snapshot was taken with so the sets match
        if hasattr(self, 'text_only_enabled') and self.only_text_files.isChecked() != self.text_only_enabled:
            self.log(f"<span style='color:{CP_YELLOW};'>Note: text-file filter changed since the snapshot; using the snapshot's setting.</span>")
        
        current_state = None
        self.tree_start(folder)
        self.scan_start()
        try:
            current_state = self.get_file_state(folder, text_only=getattr(self, 'text_only_enabled', False),
                                                progress_cb=self.update_progress, tree_cb=self._add_tree_file)
        finally:
            self.scan_end()
        
        added = []
        modified = []
        deleted = []
        
        for path, mtime in current_state.items():
            if path not in self.snapshot:
                added.append(path)
            elif self.snapshot[path] != mtime:
                modified.append(path)
                
        for path in self.snapshot:
            if path not in current_state:
                deleted.append(path)
                
        if not added and not modified and not deleted:
            self.log(f"<span style='color:{CP_YELLOW};'>No changes detected.</span>")
        else:
            self.log("<br>--- CHANGES DETECTED ---")
            for f in added:
                self.log(f"<span style='color:{CP_GREEN};'>[ADDED]</span> {f}")
            for f in modified:
                self.log(f"<span style='color:{CP_CYAN};'>[MODIFIED]</span> {f}")
            for f in deleted:
                self.log(f"<span style='color:{CP_RED};'>[DELETED]</span> {f}")
        
        # Update snapshot to current so sequential checks work
        self.snapshot = current_state

    def log(self, message):
        self.output_area.append(message)

    def restart_app(self):
        os.execv(sys.executable, [sys.executable] + sys.argv)
        
    def open_settings(self):
        dlg = SettingsDialog(self, ignore_text=self.ignore_text)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.ignore_text = dlg.get_ignore_text()
            self.save_settings()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
