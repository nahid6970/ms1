import os
import sys
import json
import asyncio
import socket
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, ListView, ListItem
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.events import Key, Resize
from rich.text import Text
from rich.style import Style

PORT = 9988

# Map keys to ANSI escape sequences for the PTY
def map_key_to_ansi(key_name, character):
    mapping = {
        "up": "\x1b[A",
        "down": "\x1b[B",
        "right": "\x1b[C",
        "left": "\x1b[D",
        "enter": "\r",
        "tab": "\t",
        "backspace": "\x7f",
        "delete": "\x1b[3~",
        "home": "\x1b[H",
        "end": "\x1b[F",
        "pageup": "\x1b[5~",
        "pagedown": "\x1b[6~",
        "escape": "\x1b",
        "shift+tab": "\x1b[Z",
    }
    
    # Handle Ctrl combinations
    if key_name.startswith("ctrl+"):
        parts = key_name.split("+")
        if len(parts) == 2 and len(parts[1]) == 1:
            char = parts[1].lower()
            return chr(ord(char) - ord('a') + 1)
            
    if key_name in mapping:
        return mapping[key_name]
    
    if character:
        return character
        
    return None

def map_color(color_name):
    if not color_name or color_name == "default":
        return None
    if color_name == "brown":
        return "yellow"
    if color_name == "brightbrown":
        return "bright_yellow"
    if color_name.startswith("bright") and len(color_name) > 6:
        color_base = color_name[6:]
        if color_base == "brown":
            color_base = "yellow"
        return f"bright_{color_base}"
    return color_name

class TerminalWidget(Static, can_focus=True):
    screen_text = reactive(Text())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def update_screen(self, screen_data):
        lines = screen_data.get("lines", [])
        cursor_x = screen_data.get("cursor_x", 0)
        cursor_y = screen_data.get("cursor_y", 0)
        cursor_hidden = screen_data.get("cursor_hidden", False)
        
        text = Text()
        for y, line in enumerate(lines):
            for x, cell in enumerate(line):
                char, fg, bg, bold, italic, underline = cell
                
                is_cursor = (y == cursor_y and x == cursor_x and not cursor_hidden)
                
                # Setup colors
                fg_color = map_color(fg)
                bg_color = map_color(bg)
                
                if is_cursor:
                    fg_color = "black"
                    bg_color = "#3b82f6" # vibrant blue cursor
                    
                style = Style(
                    color=fg_color,
                    bgcolor=bg_color,
                    bold=bold or is_cursor,
                    italic=italic,
                    underline=underline
                )
                text.append(char, style)
            if y < len(lines) - 1:
                text.append("\n")
                
        self.screen_text = text

    def render(self) -> Text:
        return self.screen_text

    def on_key(self, event: Key) -> None:
        event.prevent_default()
        
        to_send = map_key_to_ansi(event.key, event.character)
        if to_send is not None:
            self.app.send_to_server({"type": "keypress", "data": to_send})

class ProjectItem(ListItem):
    def __init__(self, name, info, **kwargs):
        super().__init__(**kwargs)
        self.project_name = name
        self.info = info

    def compose(self) -> ComposeResult:
        # Title of project
        yield Static(Text(self.project_name, style="bold"), classes="proj-title")
        
        # Branch + path combined for compactness
        branch = self.info.get('branch')
        path = self.info.get('path')
        if branch:
            subtext = f"[cyan] {branch}[/cyan] [dim]• {path}[/dim]"
        else:
            subtext = f"[dim]{path}[/dim]"
        yield Static(Text.from_markup(subtext), classes="proj-subtext")

class ProjectSidebar(Vertical):
    def compose(self) -> ComposeResult:
        yield Static("WORKSPACES", id="sidebar-header")
        yield ListView(id="sidebar-list")

class TerminalApp(App):
    CSS = """
    Screen {
        background: #000000;
        color: #d1d5db;
    }
    
    #app-container {
        layout: grid;
        grid-size: 2 1;
        grid-columns: 35 1fr;
        height: 1fr;
    }
    
    ProjectSidebar {
        background: #14161d;
        border-right: solid #222632;
        height: 100%;
    }
    
    #sidebar-header {
        background: #1c1e28;
        color: #64748b;
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
    }
    
    ProjectItem.active-project:hover {
        background: #2563eb;
    }
    
    ProjectItem.running-process {
        border-left: solid #10b981; /* Green vertical indicator bar */
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
    }
    
    #terminal-container {
        height: 100%;
        width: 100%;
        background: #000000;
        padding: 0;
        layout: vertical;
    }
    
    #terminal-header {
        background: #0d0f14;
        color: #94a3b8;
        padding: 0 2;
        height: 1;
        border-bottom: solid #1e293b;
    }
    
    TerminalWidget {
        background: #000000;
        border: none;
        height: 1fr;
        width: 100%;
        padding: 0 1;
        overflow-y: hidden;
    }
    
    TerminalWidget:focus {
        border: none;
    }
    """

    BINDINGS = [
        ("ctrl+q", "quit", "Quit Client"),
        ("ctrl+p", "focus_sidebar", "Focus Sidebar"),
        ("ctrl+t", "focus_terminal", "Focus Terminal"),
        ("ctrl+r", "refresh_branches", "Refresh Branches"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reader = None
        self.writer = None
        self.active_project = None
        self.projects_data = {}
        self.terminal_widget = None
        self.read_task = None
        self.cols = 100
        self.rows = 30

    def compose(self) -> ComposeResult:
        self.terminal_widget = TerminalWidget(id="terminal-view")
        yield Header(show_clock=True)
        with Horizontal(id="app-container"):
            yield ProjectSidebar()
            with Vertical(id="terminal-container"):
                yield Static(Text("Loading workspaces...", style="dim"), id="terminal-header")
                yield self.terminal_widget
        yield Footer()

    async def on_mount(self) -> None:
        try:
            self.reader, self.writer = await asyncio.open_connection("127.0.0.1", PORT)
            self.read_task = asyncio.create_task(self.receive_loop())
            self.send_initial_resize()
            self.terminal_widget.focus()
        except Exception as e:
            self.notify(f"Could not connect to server: {e}", severity="error")

    def send_initial_resize(self):
        size = self.terminal_widget.size
        self.cols = size.width if size.width > 0 else 100
        self.rows = size.height if size.height > 0 else 30
        self.send_to_server({"type": "resize", "cols": self.cols, "rows": self.rows})

    def on_resize(self, event: Resize) -> None:
        new_cols = max(10, event.size.width - 37)
        # 1 line header, 1 line status header, 1 line footer, border
        new_rows = max(5, event.size.height - 4)
        
        if new_cols != self.cols or new_rows != self.rows:
            self.cols = new_cols
            self.rows = new_rows
            self.send_to_server({"type": "resize", "cols": self.cols, "rows": self.rows})

    def send_to_server(self, msg):
        if self.writer:
            try:
                data = json.dumps(msg).encode("utf-8")
                header = len(data).to_bytes(4, byteorder="big")
                self.writer.write(header + data)
                loop = asyncio.get_running_loop()
                loop.create_task(self.writer.drain())
            except Exception:
                pass

    async def receive_loop(self):
        try:
            while True:
                header = await self.reader.readexactly(4)
                length = int.from_bytes(header, byteorder="big")
                data = await self.reader.readexactly(length)
                msg = json.loads(data.decode("utf-8"))
                
                msg_type = msg.get("type")
                if msg_type == "status_update":
                    self.active_project = msg.get("active_project")
                    self.projects_data = msg.get("projects", {})
                    self.update_sidebar()
                    self.update_terminal_header()
                elif msg_type == "screen_update":
                    if msg.get("project") == self.active_project:
                        self.terminal_widget.update_screen(msg.get("screen"))
        except (asyncio.IncompleteReadError, ConnectionError):
            self.notify("Lost connection to server.", severity="error")
        except Exception as e:
            self.notify(f"Reader error: {e}", severity="error")

    def update_sidebar(self):
        try:
            sidebar_list = self.query_one("#sidebar-list", ListView)
            highlighted_idx = sidebar_list.index
            
            sidebar_list.clear()
            
            project_names = sorted(self.projects_data.keys())
            active_idx = 0
            
            for idx, name in enumerate(project_names):
                info = self.projects_data[name]
                item = ProjectItem(name, info, id=f"proj-{name}")
                if name == self.active_project:
                    item.add_class("active-project")
                    active_idx = idx
                if info.get("is_alive"):
                    item.add_class("running-process")
                sidebar_list.append(item)
                
            if highlighted_idx is not None and highlighted_idx < len(project_names):
                sidebar_list.index = highlighted_idx
            else:
                sidebar_list.index = active_idx
        except Exception as e:
            pass

    def update_terminal_header(self):
        try:
            if not self.active_project:
                return
            info = self.projects_data.get(self.active_project)
            if info:
                branch_str = f" [cyan] {info['branch']}[/cyan] •" if info['branch'] else ""
                text = f"📁 [bold #3b82f6]{self.active_project}[/bold #3b82f6] •{branch_str} [dim]{info['path']}[/dim]"
                self.query_one("#terminal-header", Static).update(Text.from_markup(text))
        except Exception as e:
            pass

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if isinstance(item, ProjectItem):
            name = item.project_name
            if name != self.active_project:
                self.active_project = name
                self.send_to_server({"type": "switch_project", "project": name})
                self.terminal_widget.focus()

    def action_focus_sidebar(self) -> None:
        self.query_one("#sidebar-list").focus()

    def action_focus_terminal(self) -> None:
        self.terminal_widget.focus()

    def action_refresh_branches(self) -> None:
        self.send_to_server({"type": "refresh_branches"})
        self.notify("Refreshing git branches...")

    async def on_unmount(self) -> None:
        if self.read_task:
            self.read_task.cancel()
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

if __name__ == "__main__":
    app = TerminalApp()
    app.run()
