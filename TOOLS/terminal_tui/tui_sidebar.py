import os
import sys
import json
import subprocess
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, ListView, ListItem
from textual.containers import Vertical
from textual.events import Mount
from rich.text import Text

BASE_DIR = r"C:\@delta\ms1\TOOLS"
STATE_FILE = r"C:\@delta\ms1\TOOLS\terminal_tui\active_project.json"

class ProjectItem(ListItem):
    def __init__(self, name, path, branch, **kwargs):
        super().__init__(**kwargs)
        self.project_name = name
        self.project_path = path
        self.branch = branch

    def compose(self) -> ComposeResult:
        branch_badge = f" [white on #2c5282]  {self.branch} [/white on #2c5282]" if self.branch else ""
        yield Static(Text.from_markup(f"[bold]{self.project_name}[/bold]{branch_badge}"), classes="proj-title")
        
        # Format path for display
        display_path = self.project_path
        if display_path.lower().startswith(r"c:\users\nahid"):
            display_path = "~" + display_path[len(r"c:\users\nahid"):].replace("\\", "/")
        else:
            display_path = display_path.replace("\\", "/")
            
        yield Static(Text.from_markup(f"[dim]📂 {display_path}[/dim]"), classes="proj-subtext")

class SidebarApp(App):
    CSS = """
    Screen {
        background: #14161d;
        color: #d1d5db;
    }
    
    #sidebar-container {
        height: 100%;
        background: #14161d;
    }
    
    #sidebar-header {
        background: #1c1e28;
        color: #3b82f6;
        text-align: center;
        text-style: bold;
        padding: 1;
        border-bottom: solid #222632;
    }
    
    #sidebar-list {
        background: transparent;
        height: 1fr;
        padding: 0;
    }
    
    ProjectItem {
        padding: 1 2;
        background: transparent;
        border-left: solid #14161d;
        margin: 0;
        height: auto;
    }
    
    ProjectItem:hover {
        background: #1f2330;
    }
    
    ProjectItem.active-project {
        background: #2563eb;
        border-left: solid #3b82f6;
    }
    
    ProjectItem.active-project:hover {
        background: #2563eb;
    }
    
    ProjectItem.active-project Static {
        color: white;
    }
    
    ProjectItem.active-project .proj-subtext {
        color: #93c5fd;
    }
    
    .proj-title {
        color: #f1f5f9;
        margin-bottom: 0;
    }
    
    .proj-subtext {
        color: #64748b;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    """

    BINDINGS = [
        ("ctrl+q", "quit", "Quit Sidebar"),
        ("ctrl+r", "refresh", "Refresh List"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.projects = []
        self.active_project_name = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="sidebar-container"):
            yield Static("📁 WORKSPACES", id="sidebar-header")
            yield ListView(id="sidebar-list")
        yield Footer()

    def on_mount(self) -> None:
        self.load_state()
        self.scan_projects()
        self.populate_list()

    def load_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    state = json.load(f)
                    self.active_project_name = state.get("name")
            except Exception:
                pass

    def save_state(self, name, path):
        try:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump({"name": name, "path": path}, f)
        except Exception as e:
            self.notify(f"Error saving state: {e}", severity="error")

    def get_git_branch(self, path):
        try:
            if os.path.exists(os.path.join(path, ".git")):
                res = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=path,
                    capture_output=True,
                    text=True,
                    timeout=0.5
                )
                return res.stdout.strip()
        except Exception:
            pass
        return ""

    def scan_projects(self):
        self.projects = []
        try:
            entries = os.listdir(BASE_DIR)
            for entry in entries:
                path = os.path.join(BASE_DIR, entry)
                if os.path.isdir(path):
                    if entry.startswith(".") or entry.startswith("_"):
                        continue
                    if entry in ("__pycache__", "ENV", "node_modules", "DesktopOK"):
                        continue
                    branch = self.get_git_branch(path)
                    self.projects.append({
                        "name": entry,
                        "path": path,
                        "branch": branch
                    })
            self.projects.sort(key=lambda x: x["name"].lower())
        except Exception as e:
            self.notify(f"Error scanning: {e}", severity="error")

    def populate_list(self):
        sidebar_list = self.query_one("#sidebar-list", ListView)
        sidebar_list.clear()
        
        active_idx = 0
        for idx, proj in enumerate(self.projects):
            item = ProjectItem(proj["name"], proj["path"], proj["branch"], id=f"proj-{proj['name']}")
            if proj["name"] == self.active_project_name:
                item.add_class("active-project")
                active_idx = idx
            sidebar_list.append(item)
            
        if self.projects:
            sidebar_list.index = active_idx

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if isinstance(item, ProjectItem):
            # Highlight item
            sidebar_list = self.query_one("#sidebar-list", ListView)
            for child in sidebar_list.children:
                child.remove_class("active-project")
            item.add_class("active-project")
            
            self.active_project_name = item.project_name
            self.save_state(item.project_name, item.project_path)
            self.notify(f"Switched to workspace: {item.project_name}")

    def action_refresh(self) -> None:
        self.scan_projects()
        self.populate_list()
        self.notify("Workspaces refreshed.")

if __name__ == "__main__":
    app = SidebarApp()
    app.run()
