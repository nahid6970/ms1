import json
import math
import os
import sys
import hashlib
import ctypes
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from PyQt6.QtCore import QByteArray, QObject, Qt, QThread, QProcess, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QCursor, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QCheckBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListView,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTreeView,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from PIL import Image, ImageOps
from PyQt6.QtSvg import QSvgRenderer


# CYBERPUNK THEME PALETTE
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
HASH_BITS = 256
THUMB_SIZE = 140
APP_USER_MODEL_ID = "delta.duplicateimagefinder.1"


def app_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def settings_path() -> str:
    return os.path.join(app_dir(), "duplicate_image_finder_settings.json")


def app_icon_svg_path() -> str:
    return os.path.join(app_dir(), "duplicate_image_finder_icon.svg")


def app_icon_ico_path() -> str:
    return os.path.join(app_dir(), "duplicate_image_finder_icon.ico")


def checkbox_check_icon_path() -> str:
    return os.path.join(app_dir(), "duplicate_image_finder_check.svg")


def set_windows_app_id() -> None:
    if not sys.platform.startswith("win"):
        return
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)
    except (AttributeError, OSError):
        pass


def icon_svg_markup() -> str:
    return f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
        <rect x="6" y="6" width="52" height="52" fill="{CP_BG}" stroke="{CP_CYAN}" stroke-width="3"/>
        <rect x="16" y="18" width="18" height="18" fill="none" stroke="{CP_YELLOW}" stroke-width="4"/>
        <rect x="30" y="28" width="18" height="18" fill="none" stroke="{CP_YELLOW}" stroke-width="4"/>
        <line x1="34" y1="22" x2="48" y2="36" stroke="{CP_RED}" stroke-width="3"/>
        <text x="32" y="58" text-anchor="middle" font-family="Consolas, monospace" font-size="11" font-weight="700" fill="{CP_CYAN}">DIF</text>
    </svg>
    """


def ensure_app_icon_files() -> None:
    svg_markup = icon_svg_markup()
    with open(app_icon_svg_path(), "w", encoding="utf-8") as handle:
        handle.write(svg_markup)

    renderer = QSvgRenderer(QByteArray(svg_markup.encode("utf-8")))
    pixmap = QPixmap(256, 256)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    image = pixmap.toImage()
    ptr = image.bits()
    ptr.setsize(image.sizeInBytes())
    pil_image = Image.frombytes(
        "RGBA",
        (image.width(), image.height()),
        bytes(ptr),
        "raw",
        "BGRA",
    )
    pil_image.save(app_icon_ico_path(), format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])


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


def make_app_icon() -> QIcon:
    ensure_app_icon_files()
    icon = QIcon(app_icon_ico_path())
    if not icon.isNull():
        return icon
    svg = icon_svg_markup().encode("utf-8")
    renderer = QSvgRenderer(QByteArray(svg))
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


def apply_windows_window_icon(window: QMainWindow) -> None:
    if not sys.platform.startswith("win"):
        return
    try:
        icon_path = app_icon_ico_path()
        if not os.path.exists(icon_path):
            return
        user32 = ctypes.windll.user32
        wm_seticon = 0x0080
        icon_big = 1
        icon_small = 0
        image_icon = 1
        lr_loadfromfile = 0x0010
        hicon = user32.LoadImageW(None, icon_path, image_icon, 0, 0, lr_loadfromfile)
        if hicon:
            hwnd = int(window.winId())
            user32.SendMessageW(hwnd, wm_seticon, icon_big, hicon)
            user32.SendMessageW(hwnd, wm_seticon, icon_small, hicon)
    except (AttributeError, OSError):
        pass


@dataclass
class ImageRecord:
    path: str
    width: int
    height: int
    file_size: int
    digest: str
    dhash: int

    @property
    def resolution(self) -> str:
        return f"{self.width}x{self.height}"


class SettingsDialog(QDialog):
    def __init__(self, parent: "DuplicateImageFinderApp") -> None:
        super().__init__(parent)
        self.setWindowTitle("SETTINGS")
        self.setModal(True)
        self.resize(420, 160)

        layout = QVBoxLayout(self)
        info = QLabel("Settings panel is ready for future options.")
        info.setWordWrap(True)
        layout.addWidget(info)

        form = QFormLayout()
        self.preview_spin = QSpinBox()
        self.preview_spin.setRange(80, 240)
        self.preview_spin.setValue(parent.thumbnail_size)
        form.addRow("Thumbnail Size", self.preview_spin)
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

    def values(self) -> Dict[str, int]:
        return {"thumbnail_size": self.preview_spin.value()}


class UnionFind:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, item: int) -> int:
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, left: int, right: int) -> None:
        root_left = self.find(left)
        root_right = self.find(right)
        if root_left == root_right:
            return
        if self.rank[root_left] < self.rank[root_right]:
            self.parent[root_left] = root_right
        elif self.rank[root_left] > self.rank[root_right]:
            self.parent[root_right] = root_left
        else:
            self.parent[root_right] = root_left
            self.rank[root_left] += 1


class BKNode:
    def __init__(self, index: int, hash_value: int) -> None:
        self.index = index
        self.hash_value = hash_value
        self.children: Dict[int, "BKNode"] = {}


class BKTree:
    def __init__(self) -> None:
        self.root: Optional[BKNode] = None

    def add(self, index: int, hash_value: int) -> None:
        if self.root is None:
            self.root = BKNode(index, hash_value)
            return
        node = self.root
        while True:
            distance = hamming_distance(hash_value, node.hash_value)
            child = node.children.get(distance)
            if child is None:
                node.children[distance] = BKNode(index, hash_value)
                return
            node = child

    def search(self, hash_value: int, max_distance: int) -> List[int]:
        if self.root is None:
            return []
        matches: List[int] = []
        stack = [self.root]
        while stack:
            node = stack.pop()
            distance = hamming_distance(hash_value, node.hash_value)
            if distance <= max_distance:
                matches.append(node.index)
            low = max(0, distance - max_distance)
            high = distance + max_distance
            for edge_distance, child in node.children.items():
                if low <= edge_distance <= high:
                    stack.append(child)
        return matches


def default_settings() -> Dict[str, Any]:
    return {
        "thumbnail_size": THUMB_SIZE,
        "match_ratio": 92,
        "folders": [],
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
        settings["match_ratio"] = max(60, min(100, int(data.get("match_ratio", 92))))
        folders = data.get("folders", [])
        if isinstance(folders, list):
            normalized_folders = []
            for folder in folders:
                if isinstance(folder, str):
                    normalized_folders.append({"path": folder, "enabled": True})
                elif isinstance(folder, dict) and isinstance(folder.get("path"), str):
                    normalized_folders.append(
                        {
                            "path": folder["path"],
                            "enabled": bool(folder.get("enabled", True)),
                        }
                    )
            settings["folders"] = normalized_folders
        return settings
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return default_settings()


def save_settings(data: Dict[str, Any]) -> None:
    with open(settings_path(), "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def format_bytes(size: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} {unit}"
        value /= 1024
    return f"{size} B"


def hamming_distance(left: int, right: int) -> int:
    return (left ^ right).bit_count()


def similarity_ratio(left: int, right: int) -> float:
    return 1.0 - (hamming_distance(left, right) / HASH_BITS)


def sha1_digest(path: str) -> str:
    digest = hashlib.sha1()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compute_dhash(path: str) -> Tuple[int, int, int]:
    with Image.open(path) as image:
        image = ImageOps.exif_transpose(image)
        rgb = image.convert("RGB")
        width, height = rgb.size
        resized = rgb.convert("L").resize((17, 16), Image.Resampling.LANCZOS)
        pixels = list(resized.getdata())
    result = 0
    for row in range(16):
        row_start = row * 17
        for col in range(16):
            result <<= 1
            if pixels[row_start + col] > pixels[row_start + col + 1]:
                result |= 1
    return result, width, height


class ScanWorker(QObject):
    progress = pyqtSignal(str)
    progress_value = pyqtSignal(int, int)
    finished = pyqtSignal(list)
    failed = pyqtSignal(str)
    cancelled = pyqtSignal()

    def __init__(self, folders: List[str], min_ratio: int) -> None:
        super().__init__()
        self.folders = folders
        self.min_ratio = min_ratio
        self._cancel_requested = False

    def cancel(self) -> None:
        self._cancel_requested = True

    def run(self) -> None:
        try:
            image_paths = self._discover_images()
            if self._cancel_requested:
                self.cancelled.emit()
                return

            self.progress.emit(f"Found {len(image_paths)} image files. Computing fingerprints...")
            records = self._build_records(image_paths)
            if self._cancel_requested:
                self.cancelled.emit()
                return

            groups = self._build_groups(records)
            if self._cancel_requested:
                self.cancelled.emit()
                return

            self.finished.emit(groups)
        except Exception as exc:  # pragma: no cover - GUI fallback
            self.failed.emit(str(exc))

    def _discover_images(self) -> List[str]:
        found: List[str] = []
        for folder in self.folders:
            self.progress.emit(f"Scanning folder: {folder}")
            for root, _, files in os.walk(folder):
                if self._cancel_requested:
                    return found
                for name in files:
                    ext = os.path.splitext(name)[1].lower()
                    if ext in IMAGE_EXTENSIONS:
                        found.append(os.path.join(root, name))
        return found

    def _build_records(self, image_paths: List[str]) -> List[ImageRecord]:
        records: List[ImageRecord] = []
        total = len(image_paths)
        for index, path in enumerate(image_paths, start=1):
            if self._cancel_requested:
                return records
            self.progress.emit(f"Hashing {index}/{total}: {os.path.basename(path)}")
            self.progress_value.emit(index, total)
            try:
                dhash_value, width, height = compute_dhash(path)
                record = ImageRecord(
                    path=path,
                    width=width,
                    height=height,
                    file_size=os.path.getsize(path),
                    digest=sha1_digest(path),
                    dhash=dhash_value,
                )
                records.append(record)
            except Exception as exc:
                self.progress.emit(f"Skipped unreadable image: {path} ({exc})")
        return records

    def _build_groups(self, records: List[ImageRecord]) -> List[dict]:
        if not records:
            return []

        max_distance = math.floor((100 - self.min_ratio) * HASH_BITS / 100)
        uf = UnionFind(len(records))
        digest_map: Dict[str, List[int]] = {}
        tree = BKTree()

        for index, record in enumerate(records):
            digest_map.setdefault(record.digest, []).append(index)
            candidates = tree.search(record.dhash, max_distance)
            for candidate_index in candidates:
                candidate = records[candidate_index]
                ratio = similarity_ratio(record.dhash, candidate.dhash)
                if ratio * 100 >= self.min_ratio:
                    uf.union(index, candidate_index)
            tree.add(index, record.dhash)

        for duplicate_indexes in digest_map.values():
            if len(duplicate_indexes) > 1:
                first = duplicate_indexes[0]
                for other in duplicate_indexes[1:]:
                    uf.union(first, other)

        grouped: Dict[int, List[int]] = {}
        for index in range(len(records)):
            root = uf.find(index)
            grouped.setdefault(root, []).append(index)

        results: List[dict] = []
        for indexes in grouped.values():
            if len(indexes) < 2:
                continue
            items = [records[idx] for idx in indexes]
            base = max(items, key=lambda item: (item.width * item.height, item.file_size))
            ranked = sorted(
                items,
                key=lambda item: (
                    0 if item.path == base.path else 1,
                    -similarity_ratio(base.dhash, item.dhash),
                    item.path.lower(),
                ),
            )
            best_ratio = min(similarity_ratio(base.dhash, item.dhash) for item in ranked if item.path != base.path)
            results.append(
                {
                    "base_path": base.path,
                    "base_hash": base.dhash,
                    "match_ratio": round(best_ratio * 100, 1),
                    "items": ranked,
                }
            )

        results.sort(key=lambda group: (-group["match_ratio"], group["base_path"].lower()))
        return results


class ImageTile(QFrame):
    changed = pyqtSignal()

    def __init__(self, record: ImageRecord, base_hash: int, thumbnail_size: int, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.record = record
        self.base_hash = base_hash
        self.thumbnail_size = thumbnail_size
        self.setObjectName("ImageTile")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        self.thumb_label = QLabel()
        self.thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumb_label.setFixedSize(thumbnail_size, thumbnail_size)
        self.thumb_label.setStyleSheet(f"border: 1px solid {CP_DIM}; background-color: {CP_PANEL};")
        layout.addWidget(self.thumb_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.name_label = QLabel(os.path.basename(record.path))
        self.name_label.setWordWrap(True)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.name_label)

        self.info_label = QLabel(f"{record.resolution} | {format_bytes(record.file_size)}")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet(f"color: {CP_SUBTEXT};")
        layout.addWidget(self.info_label)

        self.match_label = QLabel()
        self.match_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.match_label)

        self.folder_label = QLabel()
        self.folder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.folder_label.setWordWrap(True)
        layout.addWidget(self.folder_label)

        self.refresh_labels()

        self._load_thumbnail()

    def refresh_labels(self) -> None:
        ratio = similarity_ratio(self.base_hash, self.record.dhash) * 100
        match_color = CP_GREEN if round(ratio, 1) >= 100.0 else CP_SUBTEXT
        self.match_label.setText(f"Match: {ratio:.1f}%")
        self.match_label.setStyleSheet(f"color: {match_color}; font-weight: bold;")
        folder_name = os.path.basename(os.path.dirname(self.record.path)) or os.path.dirname(self.record.path)
        self.folder_label.setText(f"Folder: {folder_name}")
        self.folder_label.setStyleSheet(f"color: {CP_CYAN};")

    def _load_thumbnail(self) -> None:
        pixmap = QPixmap(self.record.path)
        if pixmap.isNull():
            self.thumb_label.setText("NO PREVIEW")
            return
        scaled = pixmap.scaled(
            self.thumbnail_size,
            self.thumbnail_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.thumb_label.setPixmap(scaled)

    def contextMenuEvent(self, event) -> None:  # pragma: no cover - GUI event
        menu = QMenu(self)
        open_folder_action = QAction("OPEN FOLDER", self)
        open_image_action = QAction("OPEN IMAGE", self)
        rename_action = QAction("RENAME", self)
        delete_action = QAction("DELETE", self)

        open_folder_action.triggered.connect(self.open_parent_folder)
        open_image_action.triggered.connect(self.open_image)
        rename_action.triggered.connect(self.rename_file)
        delete_action.triggered.connect(self.delete_file)

        menu.addAction(open_image_action)
        menu.addAction(open_folder_action)
        menu.addAction(rename_action)
        menu.addSeparator()
        menu.addAction(delete_action)
        menu.exec(QCursor.pos())

    def mouseDoubleClickEvent(self, event) -> None:  # pragma: no cover - GUI event
        if event.button() == Qt.MouseButton.LeftButton:
            self.open_image()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def open_image(self) -> None:
        if not os.path.exists(self.record.path):
            QMessageBox.warning(self, "Open Failed", "Image file no longer exists.")
            return
        try:
            if sys.platform.startswith("win"):
                os.startfile(self.record.path)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                os.system(f'open "{self.record.path}"')
            else:
                os.system(f'xdg-open "{self.record.path}"')
        except OSError as exc:
            QMessageBox.critical(self, "Open Failed", str(exc))

    def open_parent_folder(self) -> None:
        folder = os.path.dirname(self.record.path)
        if sys.platform.startswith("win"):
            os.startfile(folder)  # type: ignore[attr-defined]

    def rename_file(self) -> None:
        current_dir = os.path.dirname(self.record.path)
        current_name = os.path.basename(self.record.path)
        new_path, _ = QFileDialog.getSaveFileName(
            self,
            "Rename Image",
            os.path.join(current_dir, current_name),
            "Images (*.*)",
        )
        if not new_path or os.path.normcase(new_path) == os.path.normcase(self.record.path):
            return
        if os.path.exists(new_path):
            QMessageBox.warning(self, "Rename Failed", "Target file already exists.")
            return
        try:
            os.rename(self.record.path, new_path)
            self.record.path = new_path
            self.name_label.setText(os.path.basename(new_path))
            self.refresh_labels()
            self.changed.emit()
        except OSError as exc:
            QMessageBox.critical(self, "Rename Failed", str(exc))

    def delete_file(self) -> None:
        answer = QMessageBox.question(
            self,
            "Delete Image",
            f"Delete this image?\n\n{self.record.path}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            os.remove(self.record.path)
            self.setDisabled(True)
            self.setVisible(False)
            self.changed.emit()
        except OSError as exc:
            QMessageBox.critical(self, "Delete Failed", str(exc))


class DuplicateImageFinderApp(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.settings_data = load_settings()
        self.thumbnail_size = self.settings_data.get("thumbnail_size", THUMB_SIZE)
        self.scan_thread: Optional[QThread] = None
        self.scan_worker: Optional[ScanWorker] = None
        self.current_groups: List[dict] = []
        self._restoring_folder_state = False

        self.setWindowTitle("Duplicate Image Finder")
        self.setWindowIcon(make_app_icon())
        self.resize(1480, 860)
        self._apply_theme()
        self._build_ui()
        self.restore_saved_state()

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
            QLineEdit, QSpinBox, QPlainTextEdit, QTextEdit {{
                background-color: {CP_PANEL};
                color: {CP_CYAN};
                border: 1px solid {CP_DIM};
                padding: 4px;
                selection-background-color: {CP_CYAN};
                selection-color: #000000;
            }}
            QLineEdit:focus, QSpinBox:focus {{
                border: 1px solid {CP_CYAN};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 0px;
                border: none;
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
            QPushButton#ScanButton {{
                background-color: {CP_GREEN};
                border: 1px solid {CP_GREEN};
                color: #050505;
                padding: 8px 14px;
            }}
            QPushButton#ScanButton:hover {{
                background-color: #34ff57;
                border: 1px solid {CP_YELLOW};
                color: #050505;
            }}
            QPushButton#ScanButton:pressed {{
                background-color: {CP_YELLOW};
                border: 1px solid {CP_YELLOW};
                color: #050505;
            }}
            QPushButton#ScanButton:disabled {{
                background-color: #1c4f25;
                border: 1px solid #1c4f25;
                color: #7fb78a;
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
            QCheckBox::indicator:unchecked {{
                background: {CP_PANEL};
                border: 1px solid {CP_DIM};
            }}
            QCheckBox::indicator:checked {{
                background: {CP_PANEL};
                border: 1px solid {CP_YELLOW};
                image: url({checkbox_icon});
            }}
            QTableWidget {{
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
            QMenu {{
                background-color: {CP_PANEL};
                color: {CP_TEXT};
                border: 1px solid {CP_CYAN};
            }}
            QMenu::item:selected {{
                background-color: {CP_CYAN};
                color: {CP_BG};
            }}
            QStatusBar::item {{
                border: none;
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
            QFrame#ImageTile {{
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

        controls_group = QGroupBox("SCAN CONTROLS")
        controls_layout = QVBoxLayout(controls_group)
        controls_layout.setSpacing(10)

        folder_buttons = QHBoxLayout()
        add_btn = QPushButton("ADD FOLDERS")
        remove_btn = QPushButton("REMOVE SELECTED")
        clear_btn = QPushButton("CLEAR")
        restart_btn = QPushButton("↺ RESTART")
        settings_btn = QPushButton("⚙ SETTINGS")
        add_btn.clicked.connect(self.add_folders)
        remove_btn.clicked.connect(self.remove_selected_folders)
        clear_btn.clicked.connect(self.clear_folders)
        restart_btn.clicked.connect(self.restart_app)
        settings_btn.clicked.connect(self.open_settings)
        for button in (add_btn, remove_btn, clear_btn, restart_btn, settings_btn):
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            folder_buttons.addWidget(button)
        folder_buttons.addStretch()
        controls_layout.addLayout(folder_buttons)

        self.folder_table = QTableWidget(0, 3)
        self.folder_table.setHorizontalHeaderLabels(["USE", "FOLDERS TO SCAN", "REMOVE"])
        self.folder_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.folder_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.folder_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.folder_table.setColumnWidth(0, 56)
        self.folder_table.setColumnWidth(2, 90)
        self.folder_table.verticalHeader().setVisible(False)
        self.folder_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.folder_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.folder_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.folder_table.setMaximumHeight(180)
        controls_layout.addWidget(self.folder_table)

        match_layout = QHBoxLayout()
        match_label = QLabel("MATCH RATIO")
        self.match_slider = QSlider(Qt.Orientation.Horizontal)
        self.match_slider.setRange(60, 100)
        self.match_spin = QSpinBox()
        self.match_spin.setRange(60, 100)
        self.match_slider.valueChanged.connect(self.match_spin.setValue)
        self.match_spin.valueChanged.connect(self.match_slider.setValue)
        self.match_spin.valueChanged.connect(self.on_match_ratio_changed)
        match_layout.addWidget(match_label)
        match_layout.addWidget(self.match_slider, 1)
        match_layout.addWidget(self.match_spin)

        self.scan_button = QPushButton("SCAN FOR DUPLICATES")
        self.scan_button.setObjectName("ScanButton")
        self.scan_button.clicked.connect(self.start_scan)
        self.cancel_button = QPushButton("CANCEL")
        self.cancel_button.clicked.connect(self.cancel_scan)
        self.cancel_button.setEnabled(False)

        action_row = QHBoxLayout()
        action_row.addWidget(self.scan_button)
        action_row.addWidget(self.cancel_button)
        action_row.addStretch()

        controls_layout.addLayout(match_layout)
        controls_layout.addLayout(action_row)
        controls_layout.addStretch()

        results_group = QGroupBox("MATCH GROUPS")
        results_layout = QVBoxLayout(results_group)
        self.results_table = QTableWidget(0, 1)
        self.results_table.setHorizontalHeaderLabels(["MATCHED IMAGES"])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.results_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.results_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        results_layout.addWidget(self.results_table)

        splitter.addWidget(controls_group)
        splitter.addWidget(results_group)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([360, 1080])

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("READY")
        self.status_progress = QProgressBar()
        self.status_progress.setFixedWidth(220)
        self.status_progress.setMaximum(1)
        self.status_progress.setValue(0)
        self.status_progress.setVisible(False)
        self.statusBar().addPermanentWidget(self.status_progress)

    def restore_saved_state(self) -> None:
        self._restoring_folder_state = True
        self.match_spin.blockSignals(True)
        self.match_slider.blockSignals(True)
        saved_ratio = int(self.settings_data.get("match_ratio", 92))
        self.match_spin.setValue(saved_ratio)
        self.match_slider.setValue(saved_ratio)
        self.match_spin.blockSignals(False)
        self.match_slider.blockSignals(False)

        self.folder_table.setRowCount(0)
        for folder_entry in self.settings_data.get("folders", []):
            folder_path = folder_entry.get("path", "")
            if os.path.isdir(folder_path):
                self.append_folder_row(folder_path, bool(folder_entry.get("enabled", True)))
        self._restoring_folder_state = False

    def append_folder_row(self, folder: str, enabled: bool = True) -> None:
        row = self.folder_table.rowCount()
        self.folder_table.insertRow(row)

        check_container = QWidget()
        check_layout = QHBoxLayout(check_container)
        check_layout.setContentsMargins(0, 0, 0, 0)
        check_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        check_box = QCheckBox()
        check_box.setChecked(enabled)
        check_box.stateChanged.connect(lambda _state, box=check_box: self.on_folder_checkbox_changed(box))
        check_layout.addWidget(check_box)
        self.folder_table.setCellWidget(row, 0, check_container)

        self.folder_table.setItem(row, 1, QTableWidgetItem(folder))
        remove_button = QPushButton("REMOVE")
        remove_button.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_button.setFixedWidth(78)
        remove_button.clicked.connect(lambda _checked=False, r=row: self.remove_folder_row(r))
        self.folder_table.setCellWidget(row, 2, remove_button)

    def remove_folder_row(self, row: int) -> None:
        if 0 <= row < self.folder_table.rowCount():
            self.folder_table.removeRow(row)
            self.rebind_folder_remove_buttons()
            self.persist_state()

    def rebind_folder_remove_buttons(self) -> None:
        for row in range(self.folder_table.rowCount()):
            button = self.folder_table.cellWidget(row, 2)
            if isinstance(button, QPushButton):
                try:
                    button.clicked.disconnect()
                except TypeError:
                    pass
                button.clicked.connect(lambda _checked=False, r=row: self.remove_folder_row(r))

    def persist_state(self) -> None:
        self.settings_data["thumbnail_size"] = self.thumbnail_size
        self.settings_data["match_ratio"] = self.match_spin.value()
        self.settings_data["folders"] = self.folder_entries()
        save_settings(self.settings_data)

    def folder_entries(self) -> List[Dict[str, Any]]:
        entries: List[Dict[str, Any]] = []
        for row in range(self.folder_table.rowCount()):
            path_item = self.folder_table.item(row, 1)
            check_container = self.folder_table.cellWidget(row, 0)
            check_box = check_container.findChild(QCheckBox) if check_container is not None else None
            if path_item is None or check_box is None:
                continue
            entries.append(
                {
                    "path": path_item.text(),
                    "enabled": check_box.isChecked(),
                }
            )
        return entries

    def on_match_ratio_changed(self, value: int) -> None:
        self.settings_data["match_ratio"] = value
        save_settings(self.settings_data)

    def on_folder_checkbox_changed(self, _checkbox: QCheckBox) -> None:
        if self._restoring_folder_state:
            return
        self.persist_state()

    def add_folders(self) -> None:
        dialog = QFileDialog(self, "Select Folders")
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        view = dialog.findChild(QListView, "listView")
        tree = dialog.findChild(QTreeView)
        if view is not None:
            view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        if tree is not None:
            tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        if dialog.exec():
            folders = dialog.selectedFiles()
            existing = {self.folder_table.item(row, 1).text() for row in range(self.folder_table.rowCount())}
            for folder in folders:
                if folder not in existing:
                    self.append_folder_row(folder)
            self.persist_state()

    def remove_selected_folders(self) -> None:
        rows = sorted({index.row() for index in self.folder_table.selectionModel().selectedRows()}, reverse=True)
        for row in rows:
            self.folder_table.removeRow(row)
        self.rebind_folder_remove_buttons()
        self.persist_state()

    def clear_folders(self) -> None:
        self.folder_table.setRowCount(0)
        self.persist_state()

    def selected_folders(self) -> List[str]:
        folders: List[str] = []
        for row in range(self.folder_table.rowCount()):
            path_item = self.folder_table.item(row, 1)
            check_container = self.folder_table.cellWidget(row, 0)
            check_box = check_container.findChild(QCheckBox) if check_container is not None else None
            if path_item is None or check_box is None:
                continue
            if check_box.isChecked():
                folders.append(path_item.text())
        return folders

    def start_scan(self) -> None:
        folders = self.selected_folders()
        if not folders:
            QMessageBox.warning(self, "No Folders", "Add at least one folder to scan.")
            return
        self.results_table.setRowCount(0)
        self.current_groups = []
        self.status_progress.setMaximum(1)
        self.status_progress.setValue(0)
        self.status_progress.setVisible(True)
        self.scan_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.statusBar().showMessage("SCANNING...")

        self.scan_thread = QThread(self)
        self.scan_worker = ScanWorker(folders, self.match_spin.value())
        self.scan_worker.moveToThread(self.scan_thread)

        self.scan_thread.started.connect(self.scan_worker.run)
        self.scan_worker.progress.connect(self.on_progress)
        self.scan_worker.progress_value.connect(self.on_progress_value)
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

    def on_progress(self, message: str) -> None:
        self.statusBar().showMessage(message)

    def on_progress_value(self, current: int, total: int) -> None:
        self.status_progress.setMaximum(max(total, 1))
        self.status_progress.setValue(current)

    def on_scan_finished(self, groups: List[dict]) -> None:
        self.current_groups = groups
        self.render_groups()
        self.statusBar().showMessage(f"Finished. Found {len(groups)} duplicate groups.")

    def on_scan_failed(self, error: str) -> None:
        QMessageBox.critical(self, "Scan Failed", error)
        self.statusBar().showMessage("Scan failed.")

    def on_scan_cancelled(self) -> None:
        self.statusBar().showMessage("Scan cancelled.")

    def render_groups(self) -> None:
        self.results_table.setRowCount(0)
        for group_index, group in enumerate(self.current_groups, start=1):
            items = [item for item in group["items"] if os.path.exists(item.path)]
            if len(items) < 2:
                continue
            base_hash = group["base_hash"]
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)

            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(4, 4, 4, 4)
            row_layout.setSpacing(8)

            for record in items:
                tile = ImageTile(record, base_hash, self.thumbnail_size)
                tile.changed.connect(self.render_groups)
                row_layout.addWidget(tile)
            row_layout.addStretch()

            scroller = QScrollArea()
            scroller.setWidgetResizable(True)
            scroller.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroller.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroller.setWidget(row_widget)

            self.results_table.setCellWidget(row, 0, scroller)
            self.results_table.setRowHeight(row, self.thumbnail_size + 120)

    def restart_app(self) -> None:
        started = QProcess.startDetached(sys.executable, sys.argv)
        if not started:
            QMessageBox.critical(self, "Restart Failed", "Could not relaunch the application.")
            return
        QApplication.instance().quit()

    def open_settings(self) -> None:
        dialog = SettingsDialog(self)
        if dialog.exec():
            self.settings_data.update(dialog.values())
            self.thumbnail_size = self.settings_data["thumbnail_size"]
            self.persist_state()
            self.render_groups()


def main() -> int:
    set_windows_app_id()
    app = QApplication(sys.argv)
    app.setApplicationName("Duplicate Image Finder")
    app.setDesktopFileName(APP_USER_MODEL_ID)
    app.setWindowIcon(make_app_icon())
    window = DuplicateImageFinderApp()
    window.show()
    QTimer.singleShot(0, lambda: apply_windows_window_icon(window))
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
