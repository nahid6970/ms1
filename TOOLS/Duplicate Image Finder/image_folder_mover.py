import json
import os
import shutil
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from PyQt6.QtCore import QObject, Qt, QSize, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QColor, QCursor, QIcon, QKeySequence, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QCheckBox,
    QColorDialog,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSplitter,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PIL import Image, ImageOps


CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_GREEN = "#00ff21"
CP_ORANGE = "#ff934b"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"
CP_SUBTEXT = "#808080"

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".gif",
    ".webp",
    ".tif",
    ".tiff",
}
PREVIEW_SIZE = 800
THUMB_SIZE = 90


def app_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def settings_path() -> str:
    return os.path.join(app_dir(), "image_folder_mover_settings.json")


def checkbox_check_icon_path() -> str:
    return os.path.join(app_dir(), "image_folder_mover_check.svg")


def ensure_checkbox_check_icon() -> str:
    path = checkbox_check_icon_path()
    svg_markup = f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">
        <path d="M3 8.5 L6.2 11.5 L13 4.5" fill="none" stroke="{CP_YELLOW}" stroke-width="2.2" stroke-linecap="square" stroke-linejoin="miter"/>
    </svg>
    """
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(svg_markup)
    return path.replace("\\", "/")


def default_settings() -> Dict[str, Any]:
    return {
        "source_folders": [],
        "destination_folders": [],
        "thumbnail_size": THUMB_SIZE,
        "show_thumbnails": True,
        "window_height": 980,
    }


def load_settings() -> Dict[str, Any]:
    path = settings_path()
    if not os.path.exists(path):
        return default_settings()
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        settings = default_settings()
        settings["thumbnail_size"] = int(data.get("thumbnail_size", THUMB_SIZE))
        settings["show_thumbnails"] = bool(data.get("show_thumbnails", True))
        settings["window_height"] = int(data.get("window_height", 980))

        source_folders = data.get("source_folders", [])
        normalized_sources = []
        if isinstance(source_folders, list):
            for entry in source_folders:
                if isinstance(entry, str):
                    normalized_sources.append({"path": entry, "enabled": True})
                elif isinstance(entry, dict) and isinstance(entry.get("path"), str):
                    normalized_sources.append(
                        {
                            "path": entry["path"],
                            "enabled": bool(entry.get("enabled", True)),
                        }
                    )
        settings["source_folders"] = normalized_sources

        destination_folders = data.get("destination_folders", [])
        normalized_destinations = []
        if isinstance(destination_folders, list):
            for entry in destination_folders:
                if isinstance(entry, dict) and isinstance(entry.get("path"), str):
                    normalized_destinations.append(
                        {
                            "name": str(entry.get("name", os.path.basename(entry["path"]) or entry["path"])),
                            "path": entry["path"],
                            "bg": str(entry.get("bg", CP_DIM)),
                            "fg": str(entry.get("fg", CP_TEXT)),
                        }
                    )
        settings["destination_folders"] = normalized_destinations
        return settings
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return default_settings()


def save_settings(data: Dict[str, Any]) -> None:
    with open(settings_path(), "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def format_bytes(size: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} {unit}"
        value /= 1024
    return f"{size} B"


@dataclass
class ImageEntry:
    path: str
    source_folder: str
    width: int
    height: int
    file_size: int

    @property
    def name(self) -> str:
        return os.path.basename(self.path)

    @property
    def folder_name(self) -> str:
        return os.path.basename(self.source_folder) or self.source_folder

    @property
    def resolution(self) -> str:
        return f"{self.width}x{self.height}"


class DestinationFolderDialog(QDialog):
    def __init__(self, parent: QWidget, initial: Optional[Dict[str, str]] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("DESTINATION FOLDER")
        self.resize(520, 260)
        self.delete_requested = False
        self._build_ui(initial or {})

    def _build_ui(self, initial: Dict[str, str]) -> None:
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.name_edit = QLineEdit(initial.get("name", ""))
        self.path_edit = QLineEdit(initial.get("path", ""))
        self.bg_edit = QLineEdit(initial.get("bg", CP_DIM))
        self.fg_edit = QLineEdit(initial.get("fg", CP_TEXT))

        browse_btn = QPushButton("BROWSE")
        browse_btn.clicked.connect(self.browse_folder)
        bg_btn = QPushButton("BG COLOR")
        fg_btn = QPushButton("FG COLOR")
        bg_btn.clicked.connect(lambda: self.pick_color(self.bg_edit))
        fg_btn.clicked.connect(lambda: self.pick_color(self.fg_edit))

        path_row = QHBoxLayout()
        path_row.addWidget(self.path_edit, 1)
        path_row.addWidget(browse_btn)
        path_widget = QWidget()
        path_widget.setLayout(path_row)

        bg_row = QHBoxLayout()
        bg_row.addWidget(self.bg_edit, 1)
        bg_row.addWidget(bg_btn)
        bg_widget = QWidget()
        bg_widget.setLayout(bg_row)

        fg_row = QHBoxLayout()
        fg_row.addWidget(self.fg_edit, 1)
        fg_row.addWidget(fg_btn)
        fg_widget = QWidget()
        fg_widget.setLayout(fg_row)

        form.addRow("Display Name", self.name_edit)
        form.addRow("Folder Path", path_widget)
        form.addRow("BG Color", bg_widget)
        form.addRow("FG Color", fg_widget)
        layout.addLayout(form)

        buttons = QHBoxLayout()
        if initial:
            delete_btn = QPushButton("DELETE TARGET")
            delete_btn.setStyleSheet(f"background-color: {CP_RED}; color: white;")
            delete_btn.clicked.connect(self.request_delete)
            buttons.addWidget(delete_btn)

        buttons.addStretch()
        save_btn = QPushButton("SAVE")
        cancel_btn = QPushButton("CANCEL")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

    def request_delete(self) -> None:
        self.delete_requested = True
        self.accept()

    def browse_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if folder:
            self.path_edit.setText(folder)
            if not self.name_edit.text().strip():
                self.name_edit.setText(os.path.basename(folder) or folder)

    def pick_color(self, target: QLineEdit) -> None:
        color = QColorDialog.getColor(QColor(target.text() or CP_DIM), self, "Pick Color")
        if color.isValid():
            target.setText(color.name())

    def values(self) -> Dict[str, str]:
        return {
            "name": self.name_edit.text().strip(),
            "path": self.path_edit.text().strip(),
            "bg": self.bg_edit.text().strip() or CP_DIM,
            "fg": self.fg_edit.text().strip() or CP_TEXT,
        }


class SourceFoldersWidget(QTableWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(0, 3, parent)
        self.setHorizontalHeaderLabels(["USE", "SOURCE FOLDERS", "REMOVE"])
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.setColumnWidth(0, 56)
        self.setColumnWidth(2, 86)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)


class ScanWorker(QObject):
    progress = pyqtSignal(str)
    progress_value = pyqtSignal(int, int)
    finished = pyqtSignal(list)
    failed = pyqtSignal(str)
    cancelled = pyqtSignal()

    def __init__(self, folders: List[str]) -> None:
        super().__init__()
        self.folders = folders
        self._cancel_requested = False

    def cancel(self) -> None:
        self._cancel_requested = True

    def run(self) -> None:
        try:
            image_paths: List[Tuple[str, str]] = []
            for folder in self.folders:
                self.progress.emit(f"Scanning folder: {folder}")
                for root, _, files in os.walk(folder):
                    if self._cancel_requested:
                        self.cancelled.emit()
                        return
                    for name in files:
                        if os.path.splitext(name)[1].lower() in IMAGE_EXTENSIONS:
                            image_paths.append((os.path.join(root, name), folder))

            total = len(image_paths)
            entries: List[ImageEntry] = []
            for index, (path, source_folder) in enumerate(image_paths, start=1):
                if self._cancel_requested:
                    self.cancelled.emit()
                    return
                self.progress.emit(f"Loading {index}/{total}: {os.path.basename(path)}")
                self.progress_value.emit(index, total)
                try:
                    with Image.open(path) as image:
                        image = ImageOps.exif_transpose(image)
                        width, height = image.size
                    entries.append(
                        ImageEntry(
                            path=path,
                            source_folder=source_folder,
                            width=width,
                            height=height,
                            file_size=os.path.getsize(path),
                        )
                    )
                except Exception:
                    continue

            entries.sort(key=lambda item: item.path.lower())
            self.finished.emit(entries)
        except Exception as exc:
            self.failed.emit(str(exc))


class ImageFolderMoverApp(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.settings_data = load_settings()
        self.thumbnail_size = int(self.settings_data.get("thumbnail_size", THUMB_SIZE))
        self.show_thumbnails = bool(self.settings_data.get("show_thumbnails", True))
        self.window_height = int(self.settings_data.get("window_height", 980))
        self.images: List[ImageEntry] = []
        self.destination_entries: List[Dict[str, str]] = []
        self.current_index = -1
        self._restoring_sources = False
        self.thumbnail_cache: Dict[Tuple[str, int], QPixmap] = {}
        self.scan_thread: Optional[QThread] = None
        self.scan_worker: Optional[ScanWorker] = None

        self.setWindowTitle("Image Folder Mover")
        self.resize(1720, self.window_height)
        self._apply_theme()
        self._build_ui()
        self._setup_shortcuts()
        self.restore_state()
        self.set_current_index(-1)

    def _apply_theme(self) -> None:
        checkbox_icon = ensure_checkbox_check_icon()
        self.setStyleSheet(
            f"""
            QMainWindow, QDialog {{
                background-color: {CP_BG};
            }}
            QWidget {{
                color: {CP_TEXT};
                font-family: 'Consolas';
                font-size: 10pt;
            }}
            QLineEdit, QPlainTextEdit, QTextEdit {{
                background-color: {CP_PANEL};
                color: {CP_CYAN};
                border: 1px solid {CP_DIM};
                padding: 4px;
                selection-background-color: {CP_CYAN};
                selection-color: #000000;
            }}
            QPushButton {{
                background-color: {CP_DIM};
                border: 1px solid {CP_DIM};
                color: white;
                padding: 6px 12px;
                font-weight: bold;
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
            QPushButton#PrimaryButton {{
                background-color: {CP_GREEN};
                border: 1px solid {CP_GREEN};
                color: #050505;
            }}
            QPushButton#PrimaryButton:hover {{
                background-color: #34ff57;
                border: 1px solid {CP_YELLOW};
                color: #050505;
            }}
            QGroupBox {{
                border: 1px solid {CP_DIM};
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
                color: {CP_YELLOW};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }}
            QCheckBox {{
                spacing: 0px;
                color: {CP_TEXT};
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {CP_DIM};
                background: {CP_PANEL};
            }}
            QCheckBox::indicator:checked {{
                background: {CP_PANEL};
                border: 1px solid {CP_YELLOW};
                image: url({checkbox_icon});
            }}
            QTableWidget, QListWidget {{
                background-color: {CP_PANEL};
                border: 1px solid {CP_DIM};
                gridline-color: {CP_DIM};
            }}
            QHeaderView::section {{
                background-color: {CP_PANEL};
                color: {CP_YELLOW};
                border: 1px solid {CP_DIM};
                padding: 6px;
            }}
            QListWidget::item:selected {{
                background: {CP_CYAN};
                color: {CP_BG};
            }}
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background: {CP_BG};
                width: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {CP_CYAN};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
                background: none;
            }}
            QScrollBar:horizontal {{
                background: {CP_BG};
                height: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:horizontal {{
                background: {CP_CYAN};
                min-width: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
                background: none;
            }}
            QFrame#PreviewFrame {{
                border: 1px solid {CP_DIM};
                background-color: {CP_PANEL};
            }}
            QStatusBar::item {{
                border: none;
            }}
            """
        )

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        root.addWidget(splitter, 1)

        self.left_panel = self.build_left_panel()
        self.center_panel = self.build_center_panel()
        self.right_panel = self.build_right_panel()

        splitter.addWidget(self.left_panel)
        splitter.addWidget(self.center_panel)
        splitter.addWidget(self.right_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([360, 1060, 300])

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("READY")
        self.status_progress = QProgressBar()
        self.status_progress.setFixedWidth(220)
        self.status_progress.setMaximum(1)
        self.status_progress.setValue(0)
        self.status_progress.setVisible(False)
        self.statusBar().addPermanentWidget(self.status_progress)

    def build_left_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("SOURCE FOLDERS")
        group_layout = QVBoxLayout(group)

        button_row = QHBoxLayout()
        add_btn = QPushButton("ADD FOLDERS")
        settings_btn = QPushButton("SETTINGS")
        scan_btn = QPushButton("SCAN")
        scan_btn.setObjectName("PrimaryButton")
        add_btn.clicked.connect(self.add_source_folders)
        settings_btn.clicked.connect(self.open_settings_dialog)
        scan_btn.clicked.connect(self.start_scan)
        self.scan_button = scan_btn
        self.cancel_button = QPushButton("CANCEL")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_scan)
        for button in (add_btn, settings_btn, scan_btn):
            button_row.addWidget(button)
        button_row.addStretch()
        group_layout.addLayout(button_row)

        self.source_table = SourceFoldersWidget(self)
        self.source_table.setMinimumHeight(320)
        group_layout.addWidget(self.source_table, 1)

        self.source_table_label = QLabel("0 enabled folders")
        self.source_table_label.setStyleSheet(f"color: {CP_SUBTEXT};")
        group_layout.addWidget(self.source_table_label)

        layout.addWidget(group)
        return panel

    def build_center_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        preview_group = QGroupBox("GALLERY")
        preview_layout = QVBoxLayout(preview_group)

        top_bar = QHBoxLayout()
        prev_btn = QPushButton("PREV")
        next_btn = QPushButton("NEXT")
        prev_btn.clicked.connect(lambda: self.step_image(-1))
        next_btn.clicked.connect(lambda: self.step_image(1))
        top_bar.addWidget(prev_btn)
        top_bar.addWidget(next_btn)
        top_bar.addStretch()
        self.image_count_label = QLabel("0 / 0")
        top_bar.addWidget(self.image_count_label)
        preview_layout.addLayout(top_bar)

        self.preview_frame = QFrame()
        self.preview_frame.setObjectName("PreviewFrame")
        preview_frame_layout = QVBoxLayout(self.preview_frame)
        preview_frame_layout.setContentsMargins(12, 12, 12, 12)

        self.preview_label = QLabel("NO IMAGE")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(600)
        preview_frame_layout.addWidget(self.preview_label, 1)
        preview_layout.addWidget(self.preview_frame, 1)

        self.preview_meta_label = QLabel("Add source folders to begin.")
        self.preview_meta_label.setWordWrap(True)
        self.preview_meta_label.setStyleSheet(f"color: {CP_SUBTEXT};")
        preview_layout.addWidget(self.preview_meta_label)

        thumbs_group = QGroupBox("THUMBNAILS")
        thumbs_layout = QVBoxLayout(thumbs_group)
        self.thumb_list = QListWidget()
        self.thumb_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.thumb_list.setMovement(QListWidget.Movement.Static)
        self.thumb_list.setSpacing(8)
        self.thumb_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.thumb_list.setWrapping(False)
        self.thumb_list.setFlow(QListWidget.Flow.LeftToRight)
        self.thumb_list.setIconSize(QSize(self.thumbnail_size, self.thumbnail_size))
        self.thumb_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.thumb_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.thumb_list.setFixedHeight(self.thumbnail_size + 84)
        self.thumb_list.currentRowChanged.connect(self.on_thumbnail_selected)
        thumbs_layout.addWidget(self.thumb_list)

        self.thumbs_group = thumbs_group
        layout.addWidget(preview_group, 1)
        layout.addWidget(thumbs_group)
        thumbs_group.setVisible(self.show_thumbnails)
        return panel

    def build_right_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        group = QGroupBox("MOVE TARGETS")
        group_layout = QVBoxLayout(group)

        button_row = QHBoxLayout()
        add_btn = QPushButton("ADD TARGET")
        add_btn.clicked.connect(self.add_destination_folder)
        button_row.addWidget(add_btn)
        button_row.addStretch()
        group_layout.addLayout(button_row)

        self.destination_buttons_scroll = QScrollArea()
        self.destination_buttons_scroll.setWidgetResizable(True)
        self.destination_buttons_host = QWidget()
        self.destination_buttons_layout = QVBoxLayout(self.destination_buttons_host)
        self.destination_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.destination_buttons_layout.setSpacing(8)
        self.destination_buttons_layout.addStretch()
        self.destination_buttons_scroll.setWidget(self.destination_buttons_host)
        group_layout.addWidget(self.destination_buttons_scroll, 1)

        self.current_target_label = QLabel("Select a thumbnail, then use a target button to move the image.")
        self.current_target_label.setWordWrap(True)
        self.current_target_label.setStyleSheet(f"color: {CP_SUBTEXT};")
        group_layout.addWidget(self.current_target_label)

        layout.addWidget(group, 1)
        return panel

    def restore_state(self) -> None:
        self._restoring_sources = True
        self.source_table.setRowCount(0)
        for entry in self.settings_data.get("source_folders", []):
            path = entry.get("path", "")
            if os.path.isdir(path):
                self.append_source_folder_row(path, bool(entry.get("enabled", True)))
        self._restoring_sources = False

        self.destination_entries = [dict(entry) for entry in self.settings_data.get("destination_folders", [])]
        self.refresh_destination_buttons()
        self.update_source_folder_label()

    def persist_state(self) -> None:
        self.settings_data["source_folders"] = self.source_folder_entries()
        self.settings_data["destination_folders"] = [dict(entry) for entry in self.destination_entries]
        self.settings_data["thumbnail_size"] = self.thumbnail_size
        self.settings_data["show_thumbnails"] = self.show_thumbnails
        self.settings_data["window_height"] = self.window_height
        save_settings(self.settings_data)

    def source_folder_entries(self) -> List[Dict[str, Any]]:
        entries: List[Dict[str, Any]] = []
        for row in range(self.source_table.rowCount()):
            checkbox = self.checkbox_for_row(row)
            item = self.source_table.item(row, 1)
            if checkbox is None or item is None:
                continue
            entries.append({"path": item.text(), "enabled": checkbox.isChecked()})
        return entries

    def destination_folder_entries(self) -> List[Dict[str, str]]:
        return [dict(entry) for entry in self.destination_entries]

    def append_source_folder_row(self, folder: str, enabled: bool = True) -> None:
        row = self.source_table.rowCount()
        self.source_table.insertRow(row)

        checkbox_container = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_container)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)
        checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        checkbox = QCheckBox()
        checkbox.setChecked(enabled)
        checkbox.stateChanged.connect(self.on_source_folder_toggle)
        checkbox_layout.addWidget(checkbox)
        self.source_table.setCellWidget(row, 0, checkbox_container)

        self.source_table.setItem(row, 1, QTableWidgetItem(folder))
        remove_button = QPushButton("REMOVE")
        remove_button.setFixedWidth(78)
        remove_button.clicked.connect(lambda _checked=False, r=row: self.remove_source_folder_row(r))
        self.source_table.setCellWidget(row, 2, remove_button)

    def checkbox_for_row(self, row: int) -> Optional[QCheckBox]:
        container = self.source_table.cellWidget(row, 0)
        return container.findChild(QCheckBox) if container is not None else None

    def remove_source_folder_row(self, row: int) -> None:
        if 0 <= row < self.source_table.rowCount():
            self.source_table.removeRow(row)
            self.rebind_source_remove_buttons()
            self.persist_state()
            self.update_source_folder_label()
            self.statusBar().showMessage("Source folders updated. Click SCAN to reload images.")

    def rebind_source_remove_buttons(self) -> None:
        for row in range(self.source_table.rowCount()):
            button = self.source_table.cellWidget(row, 2)
            if isinstance(button, QPushButton):
                try:
                    button.clicked.disconnect()
                except TypeError:
                    pass
                button.clicked.connect(lambda _checked=False, r=row: self.remove_source_folder_row(r))

    def on_source_folder_toggle(self) -> None:
        if self._restoring_sources:
            return
        self.persist_state()
        self.update_source_folder_label()
        self.statusBar().showMessage("Source folders updated. Click SCAN to reload images.")

    def update_source_folder_label(self) -> None:
        enabled = len(self.enabled_source_folders())
        total = self.source_table.rowCount()
        self.source_table_label.setText(f"{enabled} enabled folders / {total} total")

    def enabled_source_folders(self) -> List[str]:
        folders = []
        for row in range(self.source_table.rowCount()):
            checkbox = self.checkbox_for_row(row)
            item = self.source_table.item(row, 1)
            if checkbox is None or item is None:
                continue
            if checkbox.isChecked():
                folders.append(item.text())
        return folders

    def add_source_folders(self) -> None:
        dialog = QFileDialog(self, "Select Source Folders")
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        if dialog.exec():
            folders = dialog.selectedFiles()
            existing = {self.source_table.item(row, 1).text() for row in range(self.source_table.rowCount())}
            for folder in folders:
                if folder not in existing:
                    self.append_source_folder_row(folder, True)
            self.persist_state()
            self.update_source_folder_label()
            self.statusBar().showMessage("Source folders added. Click SCAN to load images.")

    def remove_selected_source_folders(self) -> None:
        rows = sorted({index.row() for index in self.source_table.selectionModel().selectedRows()}, reverse=True)
        for row in rows:
            self.source_table.removeRow(row)
        self.rebind_source_remove_buttons()
        self.persist_state()
        self.update_source_folder_label()
        self.statusBar().showMessage("Source folders updated. Click SCAN to reload images.")

    def clear_source_folders(self) -> None:
        self.source_table.setRowCount(0)
        self.persist_state()
        self.update_source_folder_label()
        self.images = []
        self.populate_thumbnails()
        self.set_current_index(-1)
        self.statusBar().showMessage("Source folders cleared.")

    def add_destination_folder(self) -> None:
        dialog = DestinationFolderDialog(self)
        if dialog.exec():
            values = dialog.values()
            if not values["name"] or not values["path"]:
                QMessageBox.warning(self, "Invalid Target", "Name and path are required.")
                return
            os.makedirs(values["path"], exist_ok=True)
            self.destination_entries.append(values)
            self.persist_state()
            self.refresh_destination_buttons()

    def edit_destination_folder(self, index: int) -> None:
        if not (0 <= index < len(self.destination_entries)):
            return
        initial = dict(self.destination_entries[index])
        dialog = DestinationFolderDialog(self, initial)
        if dialog.exec():
            if dialog.delete_requested:
                self.remove_destination_folder(index)
                return
            values = dialog.values()
            if not values["name"] or not values["path"]:
                QMessageBox.warning(self, "Invalid Target", "Name and path are required.")
                return
            os.makedirs(values["path"], exist_ok=True)
            self.destination_entries[index] = values
            self.persist_state()
            self.refresh_destination_buttons()

    def remove_destination_folder(self, index: int) -> None:
        if not (0 <= index < len(self.destination_entries)):
            return
        self.destination_entries.pop(index)
        self.persist_state()
        self.refresh_destination_buttons()

    def clear_destination_buttons(self) -> None:
        while self.destination_buttons_layout.count():
            item = self.destination_buttons_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def refresh_destination_buttons(self) -> None:
        self.clear_destination_buttons()
        for index, entry in enumerate(self.destination_entries):
            button = QPushButton(entry["name"])
            button.setMinimumHeight(30)
            button.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {entry['bg']};
                    color: {entry['fg']};
                    border: 1px solid {entry['fg']};
                    padding: 8px 10px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    border: 1px solid {CP_YELLOW};
                    color: {entry['fg']};
                }}
                """
            )
            button.clicked.connect(lambda _checked=False, target=entry: self.move_current_image(target))
            button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            button.customContextMenuRequested.connect(
                lambda _pos, idx=index, btn=button: self.show_destination_button_menu(idx, btn)
            )
            button.setToolTip(entry["path"])
            self.destination_buttons_layout.addWidget(button)
        self.destination_buttons_layout.addStretch()

    def show_destination_button_menu(self, index: int, button: QPushButton) -> None:
        menu = QMenu(self)
        edit_action = QAction("EDIT", self)
        remove_action = QAction("REMOVE", self)
        edit_action.triggered.connect(lambda: self.edit_destination_folder(index))
        remove_action.triggered.connect(lambda: self.remove_destination_folder(index))
        menu.addAction(edit_action)
        menu.addAction(remove_action)
        menu.exec(button.mapToGlobal(button.rect().bottomLeft()))

    def start_scan(self) -> None:
        folders = self.enabled_source_folders()
        if not folders:
            QMessageBox.warning(self, "No Folders", "Add and enable at least one source folder.")
            return

        self.scan_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.status_progress.setMaximum(1)
        self.status_progress.setValue(0)
        self.status_progress.setVisible(True)
        self.statusBar().showMessage("SCANNING...")

        self.scan_thread = QThread(self)
        self.scan_worker = ScanWorker(folders)
        self.scan_worker.moveToThread(self.scan_thread)
        self.scan_thread.started.connect(self.scan_worker.run)
        self.scan_worker.progress.connect(self.on_scan_progress)
        self.scan_worker.progress_value.connect(self.on_scan_progress_value)
        self.scan_worker.finished.connect(self.on_scan_finished)
        self.scan_worker.failed.connect(self.on_scan_failed)
        self.scan_worker.cancelled.connect(self.on_scan_cancelled)
        self.scan_worker.finished.connect(self.cleanup_scan_thread)
        self.scan_worker.failed.connect(self.cleanup_scan_thread)
        self.scan_worker.cancelled.connect(self.cleanup_scan_thread)
        self.scan_thread.start()

    def cancel_scan(self) -> None:
        if self.scan_worker is not None:
            self.scan_worker.cancel()
            self.statusBar().showMessage("CANCELLING...")

    def cleanup_scan_thread(self, *_args) -> None:
        self.scan_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.status_progress.setVisible(False)
        if self.scan_thread is not None:
            self.scan_thread.quit()
            self.scan_thread.wait()
            self.scan_thread.deleteLater()
            self.scan_thread = None
        self.scan_worker = None

    def on_scan_progress(self, message: str) -> None:
        self.statusBar().showMessage(message)

    def on_scan_progress_value(self, current: int, total: int) -> None:
        self.status_progress.setMaximum(max(total, 1))
        self.status_progress.setValue(current)

    def on_scan_finished(self, entries: List[ImageEntry]) -> None:
        current_path = self.images[self.current_index].path if 0 <= self.current_index < len(self.images) else None
        self.images = entries
        self.populate_thumbnails()
        if current_path:
            for index, entry in enumerate(self.images):
                if entry.path == current_path:
                    self.set_current_index(index)
                    break
            else:
                self.set_current_index(0 if self.images else -1)
        else:
            self.set_current_index(0 if self.images else -1)
        self.statusBar().showMessage(f"Loaded {len(self.images)} images.")

    def on_scan_failed(self, error: str) -> None:
        QMessageBox.critical(self, "Scan Failed", error)
        self.statusBar().showMessage("Scan failed.")

    def on_scan_cancelled(self) -> None:
        self.statusBar().showMessage("Scan cancelled.")

    def thumbnail_cache_key(self, path: str) -> Tuple[str, int]:
        return (os.path.normcase(path), self.thumbnail_size)

    def invalidate_thumbnail(self, path: str) -> None:
        self.thumbnail_cache.pop(self.thumbnail_cache_key(path), None)

    def load_thumbnail(self, path: str) -> QPixmap:
        key = self.thumbnail_cache_key(path)
        cached = self.thumbnail_cache.get(key)
        if cached is not None and not cached.isNull():
            return cached
        pixmap = QPixmap(path)
        if pixmap.isNull():
            return pixmap
        scaled = pixmap.scaled(
            self.thumbnail_size,
            self.thumbnail_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.thumbnail_cache[key] = scaled
        return scaled

    def populate_thumbnails(self) -> None:
        self.thumb_list.blockSignals(True)
        self.thumb_list.clear()
        for entry in self.images:
            item = QListWidgetItem(entry.name)
            item.setToolTip(entry.path)
            item.setData(Qt.ItemDataRole.UserRole, entry.path)
            thumb = self.load_thumbnail(entry.path)
            if not thumb.isNull():
                item.setIcon(QIcon(thumb))
            self.thumb_list.addItem(item)
        self.thumb_list.blockSignals(False)

    def set_current_index(self, index: int) -> None:
        if not self.images:
            self.current_index = -1
            self.preview_label.setText("NO IMAGE")
            self.preview_label.setPixmap(QPixmap())
            self.preview_meta_label.setText("No images found in enabled source folders.")
            self.image_count_label.setText("0 / 0")
            self.current_target_label.setText("Select a source folder and add move targets.")
            self.thumb_list.clearSelection()
            return

        index = max(0, min(index, len(self.images) - 1))
        self.current_index = index
        entry = self.images[index]
        preview = QPixmap(entry.path)
        if preview.isNull():
            self.preview_label.setText("NO PREVIEW")
            self.preview_label.setPixmap(QPixmap())
        else:
            scaled = preview.scaled(
                PREVIEW_SIZE,
                PREVIEW_SIZE,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.preview_label.setPixmap(scaled)
        self.preview_meta_label.setText(
            f"{entry.name}\n{entry.resolution} | {format_bytes(entry.file_size)}\nSource Folder: {entry.folder_name}"
        )
        self.image_count_label.setText(f"{index + 1} / {len(self.images)}")
        self.current_target_label.setText(f"Current Image: {entry.name}")

        self.thumb_list.blockSignals(True)
        self.thumb_list.setCurrentRow(index)
        self.thumb_list.scrollToItem(self.thumb_list.item(index))
        self.thumb_list.blockSignals(False)

    def on_thumbnail_selected(self, row: int) -> None:
        if 0 <= row < len(self.images):
            self.set_current_index(row)

    def step_image(self, delta: int) -> None:
        if not self.images:
            return
        self.set_current_index(self.current_index + delta)

    def _setup_shortcuts(self) -> None:
        prev_act = QAction(self)
        prev_act.setShortcut(QKeySequence(Qt.Key.Key_Left))
        prev_act.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        prev_act.triggered.connect(lambda: self.step_image(-1))
        self.addAction(prev_act)

        next_act = QAction(self)
        next_act.setShortcut(QKeySequence(Qt.Key.Key_Right))
        next_act.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        next_act.triggered.connect(lambda: self.step_image(1))
        self.addAction(next_act)

    def open_settings_dialog(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("SETTINGS")
        dialog.resize(320, 160)
        layout = QVBoxLayout(dialog)
        cb = QCheckBox("Show Thumbnails")
        cb.setChecked(self.show_thumbnails)
        layout.addWidget(cb)
        from PyQt6.QtWidgets import QSpinBox
        height_row = QHBoxLayout()
        height_row.addWidget(QLabel("Window Height:"))
        height_spin = QSpinBox()
        height_spin.setRange(400, 4000)
        height_spin.setValue(self.window_height)
        height_row.addWidget(height_spin)
        layout.addLayout(height_row)
        buttons = QHBoxLayout()
        save_btn = QPushButton("SAVE")
        cancel_btn = QPushButton("CANCEL")
        save_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        buttons.addStretch()
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        if dialog.exec():
            self.show_thumbnails = cb.isChecked()
            self.thumbs_group.setVisible(self.show_thumbnails)
            self.window_height = height_spin.value()
            self.resize(self.width(), self.window_height)
            self.persist_state()

    def move_current_image(self, target: Dict[str, str]) -> None:
        if not (0 <= self.current_index < len(self.images)):
            QMessageBox.warning(self, "No Image Selected", "Select an image first.")
            return

        entry = self.images[self.current_index]
        os.makedirs(target["path"], exist_ok=True)
        target_path = os.path.join(target["path"], entry.name)
        if os.path.exists(target_path):
            QMessageBox.warning(self, "Move Blocked", f"Target file already exists:\n\n{target_path}")
            return

        try:
            shutil.move(entry.path, target_path)
            self.invalidate_thumbnail(entry.path)
        except OSError as exc:
            QMessageBox.critical(self, "Move Failed", str(exc))
            return

        moved_name = entry.name
        self.images.pop(self.current_index)
        self.populate_thumbnails()
        if self.images:
            self.set_current_index(min(self.current_index, len(self.images) - 1))
        else:
            self.set_current_index(-1)
        self.statusBar().showMessage(f"Moved {moved_name} -> {target['name']}")


def main() -> int:
    app = QApplication(sys.argv)
    window = ImageFolderMoverApp()
    screen = app.primaryScreen().availableGeometry()
    window.move((screen.width() - window.width()) // 2, (screen.height() - window.height()) // 2)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
