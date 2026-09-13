#!/usr/bin/env python3
"""PyQt6 cyberpunk GUI for recovering damaged Git refs safely."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterable, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication, QDialog, QFileDialog, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QMessageBox, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget,
)


# Palette from md/THEME_GUIDE.md
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
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
DEFAULT_REPO = Path(__file__).resolve().parents[3]
AUTOSTASH_SUBJECTS = ("On main: autostash", "index on main:", "WIP on ")


def run_git(repo: Path, *args: str, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True, creationflags=CREATE_NO_WINDOW, timeout=timeout)


def git_root_from(path: Path) -> Optional[Path]:
    try:
        result = run_git(path, "rev-parse", "--show-toplevel", timeout=5)
        if result.returncode == 0:
            root = Path((result.stdout or "").strip())
            if root.exists():
                return root
    except Exception:
        pass
    candidate = path
    while True:
        if (candidate / ".git").exists():
            return candidate
        if candidate.parent == candidate:
            return None
        candidate = candidate.parent


def git_dir(repo: Path) -> Path:
    result = run_git(repo, "rev-parse", "--git-dir", timeout=5)
    if result.returncode == 0:
        value = Path((result.stdout or "").strip())
        return value if value.is_absolute() else (repo / value).resolve()
    return repo / ".git"


def ref_file(repo: Path, refname: str) -> Path:
    return git_dir(repo).joinpath(*refname.split("/"))


def is_valid_sha(value: str) -> bool:
    return bool(SHA_RE.fullmatch(value.strip()))


def read_ref_value(path: Path) -> Optional[str]:
    try:
        raw = path.read_text(encoding="ascii", errors="replace").strip()
    except Exception:
        return None
    return raw if is_valid_sha(raw) else None


def atomic_write_text(path: Path, text: str) -> None:
    """Replace a ref atomically, including when its old contents are corrupted."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="ascii", newline="\n") as handle:
            handle.write(text.rstrip() + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def packed_ref_value(repo: Path, refname: str) -> Optional[str]:
    try:
        lines = (git_dir(repo) / "packed-refs").read_text(encoding="ascii", errors="replace").splitlines()
    except OSError:
        return None
    for line in lines:
        line = line.strip()
        if line and not line.startswith(("#", "^")) and " " in line:
            sha, name = line.split(" ", 1)
            if name == refname and is_valid_sha(sha):
                return sha
    return None


def reflog_value(repo: Path, refname: str) -> Optional[str]:
    try:
        lines = (git_dir(repo) / "logs" / Path(refname)).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    for line in reversed([line for line in lines if line]):
        parts = line.split()
        if len(parts) >= 2 and is_valid_sha(parts[1]):
            return parts[1]
    return None


def object_exists(repo: Path, sha: str) -> bool:
    if not is_valid_sha(sha):
        return False
    try:
        return run_git(repo, "cat-file", "-e", f"{sha}^{{commit}}", timeout=5).returncode == 0
    except Exception:
        return False


def current_branch(repo: Path) -> Optional[str]:
    result = run_git(repo, "symbolic-ref", "--quiet", "--short", "HEAD", timeout=5)
    branch = (result.stdout or "").strip()
    return branch if result.returncode == 0 and branch else None


def current_branch_refname(branch: str) -> str:
    return f"refs/heads/{branch}"


def remote_branch_refname(branch: str) -> str:
    return f"refs/remotes/origin/{branch}"


def resolve_ref(repo: Path, refname: str) -> Optional[str]:
    for sha in (read_ref_value(ref_file(repo, refname)), packed_ref_value(repo, refname), reflog_value(repo, refname)):
        if sha and object_exists(repo, sha):
            return sha
    return None


def iter_loose_refs(repo: Path) -> Iterable[str]:
    refs_root = git_dir(repo) / "refs"
    if not refs_root.exists():
        return []
    return ["refs/" + path.relative_to(refs_root).as_posix() for path in refs_root.rglob("*") if path.is_file()]


@dataclass(frozen=True)
class CommitInfo:
    sha: str
    timestamp: int
    subject: str


@dataclass(frozen=True)
class RefRepair:
    refname: str
    before: Optional[str]
    after: str
    source: str


def commit_info(repo: Path, sha: str) -> Optional[CommitInfo]:
    result = run_git(repo, "show", "-s", "--format=%ct%x00%s", sha, timeout=10)
    parts = (result.stdout or "").strip().split("\x00")
    if result.returncode != 0 or len(parts) != 2:
        return None
    try:
        return CommitInfo(sha, int(parts[0]), parts[1])
    except ValueError:
        return None


def unreachable_commits(repo: Path) -> list[CommitInfo]:
    result = run_git(repo, "fsck", "--full", "--unreachable", timeout=60)
    infos: list[CommitInfo] = []
    for line in (result.stdout or "").splitlines():
        match = re.search(r"unreachable commit ([0-9a-f]{40})", line)
        if match:
            info = commit_info(repo, match.group(1))
            if info:
                infos.append(info)
    return infos


def best_recovery_commit(repo: Path, branch: str) -> tuple[Optional[str], str]:
    """Find the newest normal valid commit, avoiding autostash/index/WIP snapshots."""
    local_path = ref_file(repo, current_branch_refname(branch))
    direct = read_ref_value(local_path)
    if direct and object_exists(repo, direct):
        return direct, "existing local ref"
    candidates: dict[str, tuple[str, Optional[CommitInfo]]] = {}
    for source, sha in (("origin tracking ref", resolve_ref(repo, remote_branch_refname(branch))), ("local reflog", reflog_value(repo, current_branch_refname(branch))), ("ORIG_HEAD", read_ref_value(git_dir(repo) / "ORIG_HEAD"))):
        if sha and object_exists(repo, sha):
            candidates[sha] = (source, commit_info(repo, sha))
    for info in unreachable_commits(repo):
        candidates.setdefault(info.sha, ("unreachable commit", info))
    valid = [(sha, source, info) for sha, (source, info) in candidates.items() if info]
    normal = [item for item in valid if not item[2].subject.startswith(AUTOSTASH_SUBJECTS)]
    pool = normal or valid
    if not pool:
        return None, "no valid recoverable commit found"
    sha, source, info = max(pool, key=lambda item: item[2].timestamp)
    return sha, f"{source}: {info.subject}"


def backup_ref(repo: Path, refname: str) -> Optional[Path]:
    path = ref_file(repo, refname)
    if not path.exists():
        return None
    target = git_dir(repo) / "git-ref-rescue-backups" / datetime.now().strftime("%Y%m%d-%H%M%S-%f") / Path(*refname.split("/"))
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)
    return target


def write_repaired_ref(repo: Path, refname: str, sha: str) -> RefRepair:
    path = ref_file(repo, refname)
    before = read_ref_value(path)
    if before == sha and object_exists(repo, sha):
        return RefRepair(refname, before, sha, "already valid")
    backup = backup_ref(repo, refname)
    atomic_write_text(path, sha)
    return RefRepair(refname, before, sha, f"atomic repair; backup={backup}" if backup else "atomic repair")


class SettingsDialog(QDialog):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setWindowTitle("⚙ SETTINGS")
        self.setModal(True)
        layout = QVBoxLayout(self)
        title = QLabel("SETTINGS MODULE READY")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        layout.addWidget(QLabel("Future recovery preferences can be added here."))
        close = QPushButton("CLOSE")
        close.clicked.connect(self.accept)
        layout.addWidget(close)


class GitRefRescueApp(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("GIT REF RESCUE // CYBERPUNK")
        self.resize(1120, 780)
        self.setMinimumSize(900, 650)
        self.repo_edit = QLineEdit(str(DEFAULT_REPO))
        self.branch_label = QLabel("-")
        self.head_label = QLabel("-")
        self.local_label = QLabel("-")
        self.remote_label = QLabel("-")
        self.state_label = QLabel("READY")
        self.log = QPlainTextEdit()
        self._apply_theme()
        self._build_ui()
        self.refresh_status()

    def _apply_theme(self) -> None:
        self.setStyleSheet(f"""
            QMainWindow, QDialog, QWidget {{ background-color: {CP_BG}; color: {CP_TEXT}; font-family: Consolas; font-size: 10pt; }}
            QLineEdit, QPlainTextEdit {{ background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 6px; selection-background-color: {CP_CYAN}; selection-color: {CP_BG}; }}
            QLineEdit:focus, QPlainTextEdit:focus {{ border: 1px solid {CP_CYAN}; }}
            QPushButton {{ background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 7px 12px; font-weight: bold; }}
            QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; color: {CP_YELLOW}; }}
            QPushButton:pressed {{ background-color: {CP_YELLOW}; color: {CP_BG}; }}
            QGroupBox {{ background-color: {CP_PANEL}; border: 1px solid {CP_DIM}; margin-top: 10px; padding-top: 12px; font-weight: bold; color: {CP_YELLOW}; }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 6px; }}
            QScrollBar:vertical {{ background: {CP_BG}; width: 10px; }}
            QScrollBar::handle:vertical {{ background: {CP_CYAN}; min-height: 20px; border-radius: 5px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
            QLabel#title {{ color: {CP_YELLOW}; font-size: 18pt; font-weight: bold; }}
            QLabel#subtitle {{ color: {CP_SUBTEXT}; font-size: 9pt; }}
            QLabel#sectionTitle {{ color: {CP_YELLOW}; font-weight: bold; }}
            QLabel.status {{ color: {CP_CYAN}; background: {CP_PANEL}; font-weight: bold; padding: 3px; }}
        """)

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(16, 16, 16, 16)
        title = QLabel("// GIT REF RESCUE")
        title.setObjectName("title")
        outer.addWidget(title)
        subtitle = QLabel("ATOMIC REF RECOVERY • INDEX/WORKTREE PRESERVED")
        subtitle.setObjectName("subtitle")
        outer.addWidget(subtitle)

        repo_row = QHBoxLayout()
        repo_row.addWidget(QLabel("REPOSITORY"))
        repo_row.addWidget(self.repo_edit, 1)
        browse = QPushButton("BROWSE")
        browse.clicked.connect(self.choose_repo)
        repo_row.addWidget(browse)
        current = QPushButton("USE CURRENT")
        current.clicked.connect(self.use_current_dir)
        repo_row.addWidget(current)
        outer.addLayout(repo_row)

        status = QGroupBox("SYSTEM STATUS")
        status_layout = QVBoxLayout(status)
        for name, label in (("BRANCH", self.branch_label), ("HEAD", self.head_label), ("LOCAL REF", self.local_label), ("REMOTE REF", self.remote_label), ("STATE", self.state_label)):
            row = QHBoxLayout()
            caption = QLabel(name)
            caption.setFixedWidth(110)
            label.setProperty("class", "status")
            row.addWidget(caption)
            row.addWidget(label, 1)
            status_layout.addLayout(row)
        outer.addWidget(status)

        buttons = QHBoxLayout()
        actions = (("↻ REFRESH", self.refresh_status), ("SCAN BROKEN REFS", self.scan_and_repair_refs), ("REPAIR CURRENT BRANCH", self.repair_current_branch), ("FETCH ORIGIN", self.fetch_origin), ("⚙ SETTINGS", self.open_settings), ("↺ RESTART", self.restart))
        for text, handler in actions:
            button = QPushButton(text)
            button.clicked.connect(handler)
            buttons.addWidget(button)
        outer.addLayout(buttons)
        outer.addWidget(QLabel("RECOVERY LOG"))
        self.log.setReadOnly(True)
        self.log.setFont(QFont("Consolas", 10))
        outer.addWidget(self.log, 1)

    def append_log(self, text: str) -> None:
        self.log.appendPlainText(text.rstrip())
        scrollbar = self.log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def repo_path(self) -> Optional[Path]:
        raw = self.repo_edit.text().strip()
        path = Path(raw).expanduser() if raw else Path.cwd()
        if not path.exists():
            QMessageBox.critical(self, "Git Ref Rescue", f"Path does not exist:\n{path}")
            return None
        root = git_root_from(path)
        if root is None:
            QMessageBox.critical(self, "Git Ref Rescue", f"Not a Git repository:\n{path}")
            return None
        self.repo_edit.setText(str(root))
        return root

    def choose_repo(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select Git repository", self.repo_edit.text())
        if path:
            self.repo_edit.setText(path)
            self.refresh_status()

    def use_current_dir(self) -> None:
        self.repo_edit.setText(str(Path.cwd()))
        self.refresh_status()

    def git_output(self, repo: Path, *args: str, timeout: int = 10) -> str:
        try:
            result = run_git(repo, *args, timeout=timeout)
        except Exception:
            return ""
        return (result.stdout or "").strip() if result.returncode == 0 else ""

    def refresh_status(self) -> None:
        repo = self.repo_path()
        if repo is None:
            return
        branch = current_branch(repo)
        self.branch_label.setText(branch or "(DETACHED / UNRESOLVED)")
        self.head_label.setText(self.git_output(repo, "rev-parse", "--short", "HEAD") or "(BROKEN)")
        if branch:
            self.local_label.setText(resolve_ref(repo, current_branch_refname(branch)) or "(MISSING / BROKEN)")
            self.remote_label.setText(resolve_ref(repo, remote_branch_refname(branch)) or "(MISSING / BROKEN)")
        else:
            self.local_label.setText("(N/A)")
            self.remote_label.setText("(N/A)")
        self.state_label.setText("CLEAN" if not self.git_output(repo, "status", "--short") else "DIRTY / PRESERVED")
        self.append_log(f"[{datetime.now():%H:%M:%S}] branch={self.branch_label.text()} | state={self.state_label.text()}")

    def run_action(self, title: str, func: Callable[[Path], None]) -> None:
        repo = self.repo_path()
        if repo is None:
            return
        self.append_log(f"\n>>> {title.upper()}")
        try:
            func(repo)
            QMessageBox.information(self, "Git Ref Rescue", f"{title} completed.")
        except Exception as exc:
            self.append_log(f"ERROR: {exc}")
            QMessageBox.critical(self, "Git Ref Rescue", f"{title} failed.\n\n{exc}")
        finally:
            self.refresh_status()

    def scan_and_repair_refs(self) -> None:
        def action(repo: Path) -> None:
            repaired = 0
            for refname in iter_loose_refs(repo):
                current = read_ref_value(ref_file(repo, refname))
                if current and object_exists(repo, current):
                    continue
                if refname.startswith("refs/heads/"):
                    sha, reason = best_recovery_commit(repo, refname.removeprefix("refs/heads/"))
                    if sha:
                        repair = write_repaired_ref(repo, refname, sha)
                        repaired += 1
                        self.append_log(f"repaired {refname} -> {sha[:12]} ({reason}; {repair.source})")
            self.append_log(f"scan complete: {repaired} local branch ref(s) repaired; remote refs are never guessed silently")
        self.run_action("scan broken refs", action)

    def repair_current_branch(self) -> None:
        def action(repo: Path) -> None:
            branch = current_branch(repo)
            if not branch:
                raise RuntimeError("Current branch is detached or unresolved; select a branch-based repository.")
            sha, reason = best_recovery_commit(repo, branch)
            if not sha:
                raise RuntimeError(reason)
            repair = write_repaired_ref(repo, current_branch_refname(branch), sha)
            self.append_log(f"local branch repaired: {branch} -> {sha} ({reason})")
            self.append_log(f"backup: {repair.source}")
            self.append_log("index/worktree untouched; review status before committing")
            if not resolve_ref(repo, remote_branch_refname(branch)):
                self.append_log("remote-tracking ref remains unchanged; use FETCH ORIGIN explicitly if desired")
        self.run_action("repair current branch", action)

    def fetch_origin(self) -> None:
        def action(repo: Path) -> None:
            result = run_git(repo, "fetch", "origin", "--prune", timeout=60)
            self.append_log(result.stdout or result.stderr or "(no fetch output)")
            if result.returncode != 0:
                raise RuntimeError(f"git fetch failed with exit code {result.returncode}")
        self.run_action("fetch origin --prune", action)

    def open_settings(self) -> None:
        SettingsDialog(self).exec()

    def restart(self) -> None:
        os.execv(sys.executable, [sys.executable, *sys.argv])


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Git Ref Rescue")
    app.setStyle("Fusion")
    window = GitRefRescueApp()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
