#!/usr/bin/env python3
"""Cyberpunk GUI for recovering damaged Git refs without touching user files."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import tkinter as tk
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from typing import Callable, Iterable, Optional


# CYBERPUNK THEME PALETTE (translated from md/THEME_GUIDE.md for Tkinter)
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
FONT = ("Consolas", 10)
FONT_BOLD = ("Consolas", 10, "bold")
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
    """Atomically replace even a ref file containing NUL bytes."""
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
    log_path = git_dir(repo) / "logs" / Path(refname)
    try:
        lines = [line for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines() if line]
    except OSError:
        return None
    for line in reversed(lines):
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
    try:
        result = run_git(repo, "symbolic-ref", "--quiet", "--short", "HEAD", timeout=5)
    except Exception:
        return None
    if result.returncode != 0:
        return None
    branch = (result.stdout or "").strip()
    return branch or None


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
    parents: tuple[str, ...]


@dataclass(frozen=True)
class RefRepair:
    refname: str
    before: Optional[str]
    after: str
    source: str


def commit_info(repo: Path, sha: str) -> Optional[CommitInfo]:
    result = run_git(repo, "show", "-s", "--format=%ct%x00%s%x00%P", sha, timeout=10)
    if result.returncode != 0:
        return None
    parts = (result.stdout or "").strip().split("\x00")
    if len(parts) != 3:
        return None
    try:
        return CommitInfo(sha, int(parts[0]), parts[1], tuple(p for p in parts[2].split() if is_valid_sha(p)))
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
    """Choose a newest normal commit, avoiding autostash/index/WIP snapshots."""
    refname = current_branch_refname(branch)
    direct = read_ref_value(ref_file(repo, refname))
    if direct and object_exists(repo, direct):
        return direct, "existing local ref"
    candidates: dict[str, tuple[str, Optional[CommitInfo]]] = {}
    for source, sha in (("origin tracking ref", resolve_ref(repo, remote_branch_refname(branch))), ("local reflog", reflog_value(repo, refname)), ("ORIG_HEAD", read_ref_value(git_dir(repo) / "ORIG_HEAD"))):
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


class SettingsDialog(tk.Toplevel):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent)
        self.title("⚙ SETTINGS")
        self.configure(bg=CP_BG)
        self.resizable(False, False)
        ttk.Label(self, text="SETTINGS MODULE READY", style="Cyber.TLabel").pack(padx=28, pady=(24, 8))
        ttk.Label(self, text="Future recovery preferences can be added here.", style="Sub.TLabel").pack(padx=28, pady=8)
        ttk.Button(self, text="CLOSE", command=self.destroy, style="Cyber.TButton").pack(pady=(8, 24))


class GitRefRescueApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("GIT REF RESCUE // CYBERPUNK")
        self.geometry("1050x760")
        self.minsize(900, 650)
        self.configure(bg=CP_BG)
        self.repo_var = tk.StringVar(value=str(DEFAULT_REPO))
        self.branch_var = tk.StringVar(value="-")
        self.head_var = tk.StringVar(value="-")
        self.local_ref_var = tk.StringVar(value="-")
        self.remote_ref_var = tk.StringVar(value="-")
        self.state_var = tk.StringVar(value="READY")
        self._configure_theme()
        self._build_ui()
        self.refresh_status()

    def _configure_theme(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Cyber.TFrame", background=CP_BG)
        style.configure("Cyber.TLabel", background=CP_BG, foreground=CP_TEXT, font=FONT)
        style.configure("Sub.TLabel", background=CP_BG, foreground=CP_SUBTEXT, font=("Consolas", 9))
        style.configure("Title.TLabel", background=CP_BG, foreground=CP_YELLOW, font=("Consolas", 16, "bold"))
        style.configure("Status.TLabel", background=CP_PANEL, foreground=CP_CYAN, font=FONT_BOLD)
        style.configure("Cyber.TButton", background=CP_DIM, foreground="white", bordercolor=CP_DIM, padding=(10, 7), font=FONT_BOLD)
        style.map("Cyber.TButton", background=[("active", "#2a2a2a"), ("pressed", CP_YELLOW)], foreground=[("active", CP_YELLOW), ("pressed", CP_BG)])
        style.configure("Cyber.TEntry", fieldbackground=CP_PANEL, foreground=CP_CYAN, bordercolor=CP_DIM, insertcolor=CP_CYAN, padding=5, font=FONT)
        style.configure("Cyber.TLabelframe", background=CP_PANEL, bordercolor=CP_DIM)
        style.configure("Cyber.TLabelframe.Label", background=CP_PANEL, foreground=CP_YELLOW, font=FONT_BOLD)

    def _build_ui(self) -> None:
        outer = ttk.Frame(self, style="Cyber.TFrame", padding=16)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="// GIT REF RESCUE", style="Title.TLabel").pack(anchor="w")
        ttk.Label(outer, text="ATOMIC REF RECOVERY • INDEX/WORKTREE PRESERVED", style="Sub.TLabel").pack(anchor="w", pady=(0, 14))
        repo_row = ttk.Frame(outer, style="Cyber.TFrame")
        repo_row.pack(fill="x", pady=(0, 12))
        ttk.Label(repo_row, text="REPOSITORY", style="Cyber.TLabel").pack(side="left")
        ttk.Entry(repo_row, textvariable=self.repo_var, style="Cyber.TEntry").pack(side="left", fill="x", expand=True, padx=10)
        ttk.Button(repo_row, text="BROWSE", command=self.choose_repo, style="Cyber.TButton").pack(side="left")
        ttk.Button(repo_row, text="USE CURRENT", command=self.use_current_dir, style="Cyber.TButton").pack(side="left", padx=(8, 0))
        status_frame = ttk.LabelFrame(outer, text=" SYSTEM STATUS ", style="Cyber.TLabelframe", padding=12)
        status_frame.pack(fill="x", pady=(0, 12))
        rows = [("BRANCH", self.branch_var), ("HEAD", self.head_var), ("LOCAL REF", self.local_ref_var), ("REMOTE REF", self.remote_ref_var), ("STATE", self.state_var)]
        for row, (label, variable) in enumerate(rows):
            ttk.Label(status_frame, text=label, style="Sub.TLabel", width=14).grid(row=row, column=0, sticky="w", pady=3)
            ttk.Label(status_frame, textvariable=variable, style="Status.TLabel").grid(row=row, column=1, sticky="w", pady=3)
        button_row = ttk.Frame(outer, style="Cyber.TFrame")
        button_row.pack(fill="x", pady=(0, 12))
        buttons = [("↻ REFRESH", self.refresh_status), ("SCAN BROKEN REFS", self.scan_and_repair_refs), ("REPAIR CURRENT BRANCH", self.repair_current_branch), ("FETCH ORIGIN", self.fetch_origin), ("⚙ SETTINGS", self.open_settings), ("↺ RESTART", self.restart)]
        for index, (text, command) in enumerate(buttons):
            ttk.Button(button_row, text=text, command=command, style="Cyber.TButton").pack(side="left", padx=(0 if index == 0 else 8, 0))
        ttk.Label(outer, text="RECOVERY LOG", style="Cyber.TLabel").pack(anchor="w")
        self.log = ScrolledText(outer, wrap="word", height=22, bg=CP_PANEL, fg=CP_CYAN, insertbackground=CP_CYAN, selectbackground=CP_CYAN, selectforeground=CP_BG, relief="flat", borderwidth=1, font=FONT)
        self.log.pack(fill="both", expand=True, pady=(4, 0))

    def append_log(self, text: str) -> None:
        self.log.insert("end", text.rstrip() + "\n")
        self.log.see("end")

    def repo_path(self) -> Optional[Path]:
        raw = self.repo_var.get().strip()
        path = Path(raw).expanduser() if raw else Path.cwd()
        if not path.exists():
            messagebox.showerror("Git Ref Rescue", f"Path does not exist:\n{path}")
            return None
        root = git_root_from(path)
        if root is None:
            messagebox.showerror("Git Ref Rescue", f"Not a Git repository:\n{path}")
            return None
        self.repo_var.set(str(root))
        return root

    def choose_repo(self) -> None:
        path = filedialog.askdirectory(initialdir=self.repo_var.get() or str(Path.cwd()))
        if path:
            self.repo_var.set(path)
            self.refresh_status()

    def use_current_dir(self) -> None:
        self.repo_var.set(str(Path.cwd()))
        self.refresh_status()

    def _git_output(self, repo: Path, *args: str, timeout: int = 10) -> str:
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
        self.branch_var.set(branch or "(DETACHED / UNRESOLVED)")
        self.head_var.set(self._git_output(repo, "rev-parse", "--short", "HEAD") or "(BROKEN)")
        if branch:
            self.local_ref_var.set(resolve_ref(repo, current_branch_refname(branch)) or "(MISSING / BROKEN)")
            self.remote_ref_var.set(resolve_ref(repo, remote_branch_refname(branch)) or "(MISSING / BROKEN)")
        else:
            self.local_ref_var.set("(N/A)")
            self.remote_ref_var.set("(N/A)")
        status = self._git_output(repo, "status", "--short")
        self.state_var.set("CLEAN" if not status else "DIRTY / PRESERVED")
        self.append_log(f"[{datetime.now():%H:%M:%S}] branch={self.branch_var.get()} | state={self.state_var.get()}")

    def run_action(self, title: str, func: Callable[[Path], None]) -> None:
        repo = self.repo_path()
        if repo is None:
            return
        self.append_log(f"\n>>> {title.upper()}")
        try:
            func(repo)
            messagebox.showinfo("Git Ref Rescue", f"{title} completed.")
        except Exception as exc:
            self.append_log(f"ERROR: {exc}")
            messagebox.showerror("Git Ref Rescue", f"{title} failed.\n\n{exc}")
        finally:
            self.refresh_status()

    def scan_and_repair_refs(self) -> None:
        def action(repo: Path) -> None:
            repaired = 0
            for refname in iter_loose_refs(repo):
                if read_ref_value(ref_file(repo, refname)) and object_exists(repo, read_ref_value(ref_file(repo, refname)) or ""):
                    continue
                if refname.startswith("refs/heads/"):
                    branch = refname.removeprefix("refs/heads/")
                    sha, reason = best_recovery_commit(repo, branch)
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
        SettingsDialog(self)

    def restart(self) -> None:
        os.execv(sys.executable, [sys.executable, *sys.argv])


def main() -> int:
    app = GitRefRescueApp()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
