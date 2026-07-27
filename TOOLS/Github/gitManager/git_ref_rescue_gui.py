#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from typing import Iterable, Optional


SHA_RE = re.compile(r"^[0-9a-f]{40}$")
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def run_git(repo: Path, *args: str, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
        creationflags=CREATE_NO_WINDOW,
        timeout=timeout,
    )


def git_root_from(path: Path) -> Optional[Path]:
    try:
        result = run_git(path, "rev-parse", "--show-toplevel", timeout=5)
    except Exception:
        result = None
    if result and result.returncode == 0:
        root = Path((result.stdout or "").strip())
        if root.exists():
            return root
    candidate = path
    while True:
        if (candidate / ".git").exists():
            return candidate
        if candidate.parent == candidate:
            break
        candidate = candidate.parent
    return None


def git_dir(repo: Path) -> Path:
    return repo / ".git"


def ref_file(repo: Path, refname: str) -> Path:
    parts = refname.split("/")
    return git_dir(repo).joinpath(*parts)


def is_valid_sha(value: str) -> bool:
    return bool(SHA_RE.fullmatch(value.strip()))


def read_ref_value(path: Path) -> Optional[str]:
    try:
        raw = path.read_text(encoding="utf-8", errors="replace").strip()
    except Exception:
        return None
    return raw if is_valid_sha(raw) else None


def write_ref_value(path: Path, sha: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{sha}\n", encoding="utf-8")


def packed_ref_value(repo: Path, refname: str) -> Optional[str]:
    packed = git_dir(repo) / "packed-refs"
    if not packed.exists():
        return None
    try:
        for line in packed.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("^"):
                continue
            if " " not in line:
                continue
            sha, name = line.split(" ", 1)
            if name == refname and is_valid_sha(sha):
                return sha
    except Exception:
        return None
    return None


def reflog_value(repo: Path, refname: str) -> Optional[str]:
    log_path = git_dir(repo) / "logs" / Path(refname)
    if not log_path.exists():
        return None
    try:
        lines = [line.strip() for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]
    except Exception:
        return None
    for line in reversed(lines):
        parts = line.split()
        if len(parts) >= 2 and is_valid_sha(parts[1]):
            return parts[1]
    return None


def head_branch(repo: Path) -> Optional[str]:
    try:
        result = run_git(repo, "branch", "--show-current", timeout=5)
    except Exception:
        return None
    if result.returncode != 0:
        return None
    branch = (result.stdout or "").strip()
    return branch or None


def resolve_ref(repo: Path, refname: str) -> Optional[str]:
    loose = read_ref_value(ref_file(repo, refname))
    if loose:
        return loose
    packed = packed_ref_value(repo, refname)
    if packed:
        return packed
    reflog = reflog_value(repo, refname)
    if reflog:
        return reflog
    return None


def object_exists(repo: Path, sha: str) -> bool:
    if not is_valid_sha(sha):
        return False
    try:
        result = run_git(repo, "cat-file", "-e", f"{sha}^{{commit}}", timeout=5)
    except Exception:
        return False
    return result.returncode == 0


def current_branch_refname(branch: str) -> str:
    return f"refs/heads/{branch}"


def remote_branch_refname(branch: str) -> str:
    return f"refs/remotes/origin/{branch}"


@dataclass
class RefRepair:
    refname: str
    before: Optional[str]
    after: Optional[str]
    source: Optional[str]


def repair_ref(repo: Path, refname: str) -> Optional[RefRepair]:
    path = ref_file(repo, refname)
    before = read_ref_value(path)
    if before and object_exists(repo, before):
        return RefRepair(refname, before, before, None)

    candidates = [
        ("packed-refs", packed_ref_value(repo, refname)),
        ("reflog", reflog_value(repo, refname)),
    ]
    if refname.startswith("refs/heads/"):
        branch = refname.split("/", 2)[2]
        candidates.append(("origin-tracking", resolve_ref(repo, remote_branch_refname(branch))))
        orig_head = resolve_ref(repo, "ORIG_HEAD")
        candidates.append(("orig-head", orig_head))

    for source, sha in candidates:
        if sha and object_exists(repo, sha):
            write_ref_value(path, sha)
            return RefRepair(refname, before, sha, source)
    return None


def iter_loose_refs(repo: Path) -> Iterable[str]:
    refs_root = git_dir(repo) / "refs"
    if not refs_root.exists():
        return []
    refnames = []
    for path in refs_root.rglob("*"):
        if path.is_file():
            refnames.append("refs/" + path.relative_to(git_dir(repo) / "refs").as_posix())
    return refnames


class GitRefRescueApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Git Ref Rescue")
        self.geometry("960x700")
        self.minsize(860, 620)

        self.repo_var = tk.StringVar(value=str(Path.cwd()))
        self.branch_var = tk.StringVar(value="-")
        self.upstream_var = tk.StringVar(value="-")
        self.head_var = tk.StringVar(value="-")
        self.remote_ref_var = tk.StringVar(value="-")
        self.local_ref_var = tk.StringVar(value="-")
        self.state_var = tk.StringVar(value="Ready")

        self._build_ui()
        self.refresh_status()

    def _build_ui(self) -> None:
        outer = ttk.Frame(self, padding=12)
        outer.pack(fill="both", expand=True)

        repo_row = ttk.Frame(outer)
        repo_row.pack(fill="x")
        ttk.Label(repo_row, text="Repository").pack(side="left")
        ttk.Entry(repo_row, textvariable=self.repo_var).pack(side="left", fill="x", expand=True, padx=8)
        ttk.Button(repo_row, text="Browse", command=self.choose_repo).pack(side="left")
        ttk.Button(repo_row, text="Use Current", command=self.use_current_dir).pack(side="left", padx=(8, 0))

        status_frame = ttk.LabelFrame(outer, text="Status", padding=10)
        status_frame.pack(fill="x", pady=(12, 10))
        grid = ttk.Frame(status_frame)
        grid.pack(fill="x")
        rows = [
            ("Branch", self.branch_var),
            ("Upstream", self.upstream_var),
            ("HEAD", self.head_var),
            ("Local ref", self.local_ref_var),
            ("Remote ref", self.remote_ref_var),
            ("State", self.state_var),
        ]
        for idx, (label, var) in enumerate(rows):
            ttk.Label(grid, text=label, width=12).grid(row=idx, column=0, sticky="w", pady=2)
            ttk.Label(grid, textvariable=var).grid(row=idx, column=1, sticky="w", pady=2)

        button_row = ttk.Frame(outer)
        button_row.pack(fill="x", pady=(0, 10))
        ttk.Button(button_row, text="Refresh", command=self.refresh_status).pack(side="left")
        ttk.Button(button_row, text="Scan Broken Refs", command=self.scan_and_repair_refs).pack(side="left", padx=8)
        ttk.Button(button_row, text="Repair Current Branch", command=self.repair_current_branch).pack(side="left")
        ttk.Button(button_row, text="Fetch Origin", command=self.fetch_origin).pack(side="left", padx=8)
        ttk.Button(button_row, text="Set Upstream", command=self.set_upstream).pack(side="left")

        self.log = ScrolledText(outer, wrap="word", height=22)
        self.log.pack(fill="both", expand=True)
        self.log.configure(state="disabled")

    def choose_repo(self) -> None:
        path = filedialog.askdirectory(initialdir=self.repo_var.get() or str(Path.cwd()))
        if path:
            self.repo_var.set(path)
            self.refresh_status()

    def use_current_dir(self) -> None:
        self.repo_var.set(str(Path.cwd()))
        self.refresh_status()

    def repo_path(self) -> Optional[Path]:
        raw = self.repo_var.get().strip()
        if not raw:
            messagebox.showerror("Git Ref Rescue", "Select a repository path first.")
            return None
        path = Path(raw).expanduser()
        if not path.exists():
            messagebox.showerror("Git Ref Rescue", f"Path does not exist:\n{path}")
            return None
        root = git_root_from(path)
        if root is None:
            messagebox.showerror("Git Ref Rescue", f"Not a git repository:\n{path}")
            return None
        self.repo_var.set(str(root))
        return root

    def append_log(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", text.rstrip() + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def run_action(self, title: str, func) -> None:
        repo = self.repo_path()
        if repo is None:
            return
        self.append_log(f"[{title}] {repo}")
        try:
            func(repo)
        except subprocess.CalledProcessError as exc:
            self.append_log(exc.stdout or "")
            self.append_log(exc.stderr or "")
            messagebox.showerror("Git Ref Rescue", f"{title} failed.\n\n{exc.stderr or exc.stdout or exc}")
        except Exception as exc:
            messagebox.showerror("Git Ref Rescue", f"{title} failed.\n\n{exc}")
        finally:
            self.refresh_status()

    def refresh_status(self) -> None:
        repo = self.repo_path()
        if repo is None:
            return
        branch = head_branch(repo)
        self.branch_var.set(branch or "(detached or unresolved)")
        self.head_var.set(self._git_output(repo, "rev-parse", "--short", "HEAD") or "-")
        if branch:
            upstream = self._git_output(repo, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
            self.upstream_var.set(upstream or "(none)")
            local_ref = resolve_ref(repo, current_branch_refname(branch))
            remote_ref = resolve_ref(repo, remote_branch_refname(branch))
            self.local_ref_var.set(local_ref or "(missing/broken)")
            self.remote_ref_var.set(remote_ref or "(missing/broken)")
        else:
            self.upstream_var.set("(none)")
            self.local_ref_var.set("(n/a)")
            self.remote_ref_var.set("(n/a)")

        status = self._git_output(repo, "status", "--short")
        self.state_var.set("clean" if not status else "dirty")
        self.append_log(f"Branch: {self.branch_var.get()} | Upstream: {self.upstream_var.get()} | State: {self.state_var.get()}")

    def _git_output(self, repo: Path, *args: str, timeout: int = 10) -> str:
        try:
            result = run_git(repo, *args, timeout=timeout)
        except Exception:
            return ""
        if result.returncode != 0:
            return ""
        return (result.stdout or "").strip()

    def fetch_origin(self) -> None:
        def _run(repo: Path) -> None:
            result = run_git(repo, "fetch", "origin", "--prune", timeout=60)
            self.append_log(result.stdout or "")
            self.append_log(result.stderr or "")
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)

        self.run_action("fetch origin --prune", _run)

    def scan_and_repair_refs(self) -> None:
        def _run(repo: Path) -> None:
            repaired = []
            for refname in iter_loose_refs(repo):
                path = ref_file(repo, refname)
                current = read_ref_value(path)
                if current and object_exists(repo, current):
                    continue
                result = repair_ref(repo, refname)
                if result and result.after and result.after != result.before:
                    repaired.append(result)
                    self.append_log(f"repaired {result.refname} from {result.source}: {result.after}")
            if not repaired:
                self.append_log("No broken loose refs found.")

        self.run_action("scan broken refs", _run)

    def set_upstream(self) -> None:
        def _run(repo: Path) -> None:
            branch = head_branch(repo)
            if not branch:
                raise RuntimeError("Current branch could not be resolved. Checkout a branch first.")
            result = run_git(repo, "branch", "--set-upstream-to", f"origin/{branch}", branch, timeout=20)
            self.append_log(result.stdout or "")
            self.append_log(result.stderr or "")
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)

        self.run_action("set upstream", _run)

    def repair_current_branch(self) -> None:
        def _run(repo: Path) -> None:
            branch = head_branch(repo)
            if not branch:
                raise RuntimeError("Current branch could not be resolved. This tool repairs branch-based repos.")

            self.append_log("Step 1: repairing broken loose refs")
            repaired = []
            for refname in (current_branch_refname(branch), remote_branch_refname(branch)):
                result = repair_ref(repo, refname)
                if result and result.after and result.after != result.before:
                    repaired.append(result)
                    self.append_log(f"  repaired {result.refname} from {result.source}: {result.after}")

            self.append_log("Step 2: fetching origin")
            fetch = run_git(repo, "fetch", "origin", "--prune", timeout=60)
            self.append_log(fetch.stdout or "")
            self.append_log(fetch.stderr or "")
            if fetch.returncode != 0:
                # Keep going if local repair already fixed the damaged refs.
                self.append_log("Fetch returned a non-zero exit code; continuing with local repair state.")

            self.append_log("Step 3: refreshing branch refs from fetched data")
            remote_sha = resolve_ref(repo, remote_branch_refname(branch))
            if remote_sha:
                write_ref_value(ref_file(repo, remote_branch_refname(branch)), remote_sha)
                self.append_log(f"  remote-tracking ref now points to {remote_sha}")

            local_sha = resolve_ref(repo, current_branch_refname(branch))
            if not local_sha:
                local_sha = remote_sha or reflog_value(repo, current_branch_refname(branch)) or resolve_ref(repo, "ORIG_HEAD")
            if local_sha:
                write_ref_value(ref_file(repo, current_branch_refname(branch)), local_sha)
                self.append_log(f"  local branch ref now points to {local_sha}")

            self.append_log("Step 4: restoring upstream")
            upstream = run_git(repo, "branch", "--set-upstream-to", f"origin/{branch}", branch, timeout=20)
            self.append_log(upstream.stdout or "")
            self.append_log(upstream.stderr or "")
            if upstream.returncode != 0:
                raise subprocess.CalledProcessError(upstream.returncode, upstream.args, upstream.stdout, upstream.stderr)

        self.run_action("repair current branch", _run)


def main() -> int:
    app = GitRefRescueApp()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
