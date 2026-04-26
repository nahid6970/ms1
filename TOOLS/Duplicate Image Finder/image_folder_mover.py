import json
import os
import shutil
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QIcon, QPixmap
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
    QMessageBox,
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
PREVIEW_SIZE = 760
THUMB_SIZE = 108


def app_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def settings_path() -> str:
    return os.path.join(app_dir(), "image_folder_mover_settings.json")


def default_settings() -> Dict[str, Any]:
    return {
        "source_folders": [],
        "destination_folders": [],
        "thumbnail_size": THUMB_SIZE,
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
        buttons.addStretch()
        save_btn = QPushButton("SAVE")
        cancel_btn = QPushButton("CANCEL")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

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


class ImageFolderMoverApp(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.settings_data = load_settings()
        self.thumbnail_size = int(self.settings_data.get("thumbnail_size", THUMB_SIZE))
        self.images: List[ImageEntry] = []
        self.current_index = -1
        self._restoring_sources = False
        self.thumbnail_cache: Dict[Tuple[str, int], QPixmap] = {}

        self.setWindowTitle("Image Folder Mover")
        self.resize(1720, 980)
        self._apply_theme()
        self._build_ui()
        self.restore_state()
        self.reload_images()

    def _apply_theme(self) -> None:
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
        splitter.setSizes([360, 980, 360])

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("READY")

    def build_left_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("SOURCE FOLDERS")
        group_layout = QVBoxLayout(group)

        button_row = QHBoxLayout()
        add_btn = QPushButton("ADD FOLDERS")
        remove_btn = QPushButton("REMOVE SELECTED")
        clear_btn = QPushButton("CLEAR")
        refresh_btn = QPushButton("REFRESH")
        add_btn.clicked.connect(self.add_source_folders)
        remove_btn.clicked.connect(self.remove_selected_source_folders)
        clear_btn.clicked.connect(self.clear_source_folders)
        refresh_btn.clicked.connect(self.reload_images)
        for button in (add_btn, remove_btn, clear_btn, refresh_btn):
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
        self.preview_label.setMinimumHeight(640)
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
        self.thumb_list.setMaximumHeight(self.thumbnail_size + 76)
        self.thumb_list.currentRowChanged.connect(self.on_thumbnail_selected)
        thumbs_layout.addWidget(self.thumb_list)

        layout.addWidget(preview_group, 1)
        layout.addWidget(thumbs_group)
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
        edit_btn = QPushButton("EDIT TARGET")
        remove_btn = QPushButton("REMOVE TARGET")
        add_btn.clicked.connect(self.add_destination_folder)
        edit_btn.clicked.connect(self.edit_selected_destination_folder)
        remove_btn.clicked.connect(self.remove_selected_destination_folder)
        button_row.addWidget(add_btn)
        button_row.addWidget(edit_btn)
        button_row.addWidget(remove_btn)
        group_layout.addLayout(button_row)

        self.destination_table = QTableWidget(0, 4)
        self.destination_table.setHorizontalHeaderLabels(["NAME", "PATH", "BG", "FG"])
        self.destination_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.destination_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.destination_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.destination_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.destination_table.verticalHeader().setVisible(False)
        self.destination_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.destination_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.destination_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.destination_table.setMinimumHeight(260)
        group_layout.addWidget(self.destination_table)

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

        self.destination_table.setRowCount(0)
        for entry in self.settings_data.get("destination_folders", []):
            self.append_destination_table_row(entry)
        self.refresh_destination_buttons()
        self.update_source_folder_label()

    def persist_state(self) -> None:
        self.settings_data["source_folders"] = self.source_folder_entries()
        self.settings_data["destination_folders"] = self.destination_folder_entries()
        self.settings_data["thumbnail_size"] = self.thumbnail_size
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
        entries: List[Dict[str, str]] = []
        for row in range(self.destination_table.rowCount()):
            name_item = self.destination_table.item(row, 0)
            path_item = self.destination_table.item(row, 1)
            bg_item = self.destination_table.item(row, 2)
            fg_item = self.destination_table.item(row, 3)
            if None in (name_item, path_item, bg_item, fg_item):
                continue
            entries.append(
                {
                    "name": name_item.text(),
                    "path": path_item.text(),
                    "bg": bg_item.text(),
                    "fg": fg_item.text(),
                }
            )
        return entries

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
            self.reload_images()

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
        self.reload_images()

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
            self.reload_images()

    def remove_selected_source_folders(self) -> None:
        rows = sorted({index.row() for index in self.source_table.selectionModel().selectedRows()}, reverse=True)
        for row in rows:
            self.source_table.removeRow(row)
        self.rebind_source_remove_buttons()
        self.persist_state()
        self.update_source_folder_label()
        self.reload_images()

    def clear_source_folders(self) -> None:
        self.source_table.setRowCount(0)
        self.persist_state()
        self.update_source_folder_label()
        self.reload_images()

    def append_destination_table_row(self, entry: Dict[str, str]) -> None:
        row = self.destination_table.rowCount()
        self.destination_table.insertRow(row)
        self.destination_table.setItem(row, 0, QTableWidgetItem(entry["name"]))
        self.destination_table.setItem(row, 1, QTableWidgetItem(entry["path"]))
        self.destination_table.setItem(row, 2, QTableWidgetItem(entry["bg"]))
        self.destination_table.setItem(row, 3, QTableWidgetItem(entry["fg"]))

    def add_destination_folder(self) -> None:
        dialog = DestinationFolderDialog(self)
        if dialog.exec():
            values = dialog.values()
            if not values["name"] or not values["path"]:
                QMessageBox.warning(self, "Invalid Target", "Name and path are required.")
                return
            os.makedirs(values["path"], exist_ok=True)
            self.append_destination_table_row(values)
            self.persist_state()
            self.refresh_destination_buttons()

    def edit_selected_destination_folder(self) -> None:
        row = self.destination_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Target Selected", "Select a target row to edit.")
            return
        initial = {
            "name": self.destination_table.item(row, 0).text(),
            "path": self.destination_table.item(row, 1).text(),
            "bg": self.destination_table.item(row, 2).text(),
            "fg": self.destination_table.item(row, 3).text(),
        }
        dialog = DestinationFolderDialog(self, initial)
        if dialog.exec():
            values = dialog.values()
            if not values["name"] or not values["path"]:
                QMessageBox.warning(self, "Invalid Target", "Name and path are required.")
                return
            os.makedirs(values["path"], exist_ok=True)
            for column, value in enumerate((values["name"], values["path"], values["bg"], values["fg"])):
                self.destination_table.setItem(row, column, QTableWidgetItem(value))
            self.persist_state()
            self.refresh_destination_buttons()

    def remove_selected_destination_folder(self) -> None:
        row = self.destination_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Target Selected", "Select a target row to remove.")
            return
        self.destination_table.removeRow(row)
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
        for entry in self.destination_folder_entries():
            button = QPushButton(entry["name"])
            button.setMinimumHeight(54)
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
            self.destination_buttons_layout.addWidget(button)
        self.destination_buttons_layout.addStretch()

    def reload_images(self) -> None:
        current_path = self.images[self.current_index].path if 0 <= self.current_index < len(self.images) else None
        self.images = []

        for folder in self.enabled_source_folders():
            for root, _, files in os.walk(folder):
                for name in files:
                    if os.path.splitext(name)[1].lower() not in IMAGE_EXTENSIONS:
                        continue
                    path = os.path.join(root, name)
                    try:
                        with Image.open(path) as image:
                            image = ImageOps.exif_transpose(image)
                            width, height = image.size
                        self.images.append(
                            ImageEntry(
                                path=path,
                                source_folder=folder,
                                width=width,
                                height=height,
                                file_size=os.path.getsize(path),
                            )
                        )
                    except Exception:
                        continue

        self.images.sort(key=lambda item: item.path.lower())
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
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
