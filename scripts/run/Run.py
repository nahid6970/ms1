import os
import subprocess
import tempfile
import sys
import json
import ctypes

ctypes.windll.kernel32.SetConsoleTitleW("RUNNER")
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

script_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.abspath(__file__)
BOOKMARKS_FILE = os.path.join(script_dir, "bookmarks.json")
COLLAPSED_FILE = os.path.join(script_dir, "collapsed.json")
CONFIG_FILE = os.path.join(script_dir, "config.json")

# Apply saved font face and size if present
try:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
            theme = cfg.get("theme", {})
            font_face = theme.get("font_face", None)
            font_size = theme.get("font_size", 16)
            if font_face:
                LF_FACESIZE = 32
                STD_OUTPUT_HANDLE = -11
                class COORD(ctypes.Structure):
                    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]
                class CONSOLE_FONT_INFOEX(ctypes.Structure):
                    _fields_ = [
                        ("cbSize", ctypes.c_ulong),
                        ("nFont", ctypes.c_ulong),
                        ("dwFontSize", COORD),
                        ("FontFamily", ctypes.c_uint),
                        ("FontWeight", ctypes.c_uint),
                        ("FaceName", ctypes.c_wchar * LF_FACESIZE)
                    ]
                handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
                font_info = CONSOLE_FONT_INFOEX()
                font_info.cbSize = ctypes.sizeof(CONSOLE_FONT_INFOEX)
                font_info.dwFontSize.X = 0
                font_info.dwFontSize.Y = font_size
                font_info.FontFamily = 54
                font_info.FontWeight = 400
                font_info.FaceName = font_face
                ctypes.windll.kernel32.SetCurrentConsoleFontEx(handle, False, ctypes.byref(font_info))
except:
    pass

# Clean up deprecated run_settings.txt if it exists
try:
    old_settings = os.path.join(script_dir, "run_settings.txt")
    if os.path.exists(old_settings):
        os.remove(old_settings)
except:
    pass

def toggle_collapse(file_path):
    if not os.path.isdir(file_path):
        return
    dir_path = os.path.dirname(COLLAPSED_FILE)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    collapsed = []
    if os.path.exists(COLLAPSED_FILE):
        try:
            with open(COLLAPSED_FILE, 'r', encoding='utf-8') as f:
                collapsed = json.load(f)
        except:
            pass
    norm_path = os.path.normpath(file_path)
    norm_path_lower = norm_path.lower()
    existing = next((p for p in collapsed if os.path.normpath(p).lower() == norm_path_lower), None)
    if existing:
        collapsed.remove(existing)
    else:
        collapsed.append(norm_path)
    with open(COLLAPSED_FILE, 'w', encoding='utf-8') as f:
        json.dump(collapsed, f, indent=2, ensure_ascii=False)

def reset_collapsed():
    if os.path.exists(COLLAPSED_FILE):
        try:
            with open(COLLAPSED_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)
        except:
            pass

def toggle_bookmark(file_path):
    dir_path = os.path.dirname(BOOKMARKS_FILE)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    bookmarks = []
    if os.path.exists(BOOKMARKS_FILE):
        try:
            with open(BOOKMARKS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                bookmarks = [b if isinstance(b, dict) else {"path": b, "name": ""} for b in data]
        except: pass
    
    existing = next((b for b in bookmarks if b['path'] == file_path), None)
    if existing:
        bookmarks.remove(existing)
    else:
        # Open console device directly for interactive input
        try:
            con_path = 'CON' if os.name == 'nt' else '/dev/tty'
            with open(con_path, 'r') as f_in:
                print(f"\n\033[96mBookmarking: {file_path}\033[0m")
                print("Enter custom name (leave empty for default, Ctrl+C to cancel): ", end='', flush=True)
                name = f_in.readline().strip()
                bookmarks.append({"path": file_path, "name": name})
        except KeyboardInterrupt:
            print("\n\033[91mCancelled bookmark addition.\033[0m")
            return
        except Exception as e:
            # Fallback for non-interactive environments
            bookmarks.append({"path": file_path, "name": ""})
        
    with open(BOOKMARKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(bookmarks, f, indent=2, ensure_ascii=False)

def move_bookmark(file_path, direction):
    if not os.path.exists(BOOKMARKS_FILE): return
    try:
        with open(BOOKMARKS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            bookmarks = [b if isinstance(b, dict) else {"path": b, "name": ""} for b in data]
    except: return
    
    def is_descendant(parent, child):
        p = os.path.normpath(parent).lower()
        c = os.path.normpath(child).lower()
        if p == c: return False
        return c.startswith(p + os.sep) or (p.endswith(os.sep) and c.startswith(p))

    # Determine parent for each bookmark
    parent_map = {}
    for bm in bookmarks:
        path = bm['path']
        ancestors = [other for other in bookmarks if is_descendant(other['path'], path)]
        if not ancestors:
            parent_map[path] = None
        else:
            closest = max(ancestors, key=lambda x: len(x['path']))
            parent_map[path] = closest['path']

    target_idx = next((i for i, b in enumerate(bookmarks) if b['path'] == file_path), -1)
    if target_idx == -1: return
    
    target_path = bookmarks[target_idx]['path']
    parent_path = parent_map[target_path]
    
    # Get siblings and sort them by their current index in the flat list
    siblings = [b for b in bookmarks if parent_map[b['path']] == parent_path]
    siblings.sort(key=lambda b: bookmarks.index(b))
    
    sib_idx = next((i for i, b in enumerate(siblings) if b['path'] == target_path), -1)
    if sib_idx == -1: return
    
    new_sib_idx = sib_idx + direction
    if 0 <= new_sib_idx < len(siblings):
        sibling_to_swap = siblings[new_sib_idx]
        idx_to_swap = bookmarks.index(sibling_to_swap)
        
        # Swap target and sibling in the flat list
        bookmarks[target_idx], bookmarks[idx_to_swap] = bookmarks[idx_to_swap], bookmarks[target_idx]
        
        # Save bookmarks
        with open(BOOKMARKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(bookmarks, f, indent=2, ensure_ascii=False)


def load_config():
    default_roots = {
        r"C:\@delta\ms1": True,
        r"C:\@delta\db": True,
        r"C:\@delta\msBackups": True,
        r"C:\Users\nahid\Pictures": True,
        "D:\\": True
    }
    default_icons = {
        ".py": {"icon": "🐍", "color": 220},
        ".json": {"icon": "⚙️", "color": 215},
        ".md": {"icon": "📝", "color": 39},
        ".txt": {"icon": "📄", "color": 250},
        ".png, .jpg, .jpeg, .gif, .webp": {"icon": "🖼️", "color": 197},
        ".ico, .svg, .css": {"icon": "🎨", "color": 39},
        ".html": {"icon": "🌐", "color": 202},
        ".js, .ts": {"icon": "📜", "color": 220},
        ".cpp, .h, .cs": {"icon": "⚙️", "color": 110},
        ".go": {"icon": "🐹", "color": 81},
        ".rs": {"icon": "🦀", "color": 208},
        ".pdf": {"icon": "📕", "color": 196},
        ".zip, .tar, .gz, .7z": {"icon": "📦", "color": 220},
        "folder": {"icon": "📁", "color": 208}
    }
    config = {
        "search_roots": default_roots,
        "visibility": {
            ".git": False, "__pycache__": False, "node_modules": False, ".venv": False,
            ".vscode": False, "obj": False, "bin": False
        },
        "theme": {
            "folder_normal": 208,
            "folder_bookmark": 51,
            "file_normal": 250,
            "file_bookmark": 121
        },
        "show_collapse_indicators": True,
        "extension_icons": default_icons,
        "show_extension_dots": True,
        "show_extension_commas": True
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "search_roots" in data and data["search_roots"]:
                    config["search_roots"] = data["search_roots"]
                if "visibility" in data:
                    config["visibility"] = data["visibility"]
                if "theme" in data:
                    config["theme"].update(data["theme"])
                if "show_collapse_indicators" in data:
                    config["show_collapse_indicators"] = data["show_collapse_indicators"]
                if "extension_icons" in data:
                    config["extension_icons"] = data["extension_icons"]
                if "show_extension_dots" in data:
                    config["show_extension_dots"] = data["show_extension_dots"]
                if "show_extension_commas" in data:
                    config["show_extension_commas"] = data["show_extension_commas"]
                if "bookmarked_config_setting" in data:
                    config["bookmarked_config_setting"] = data["bookmarked_config_setting"]
        except:
            pass
            
    # Save default config if file does not exist, or save populated roots if missing/empty
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if "search_roots" not in data or not data["search_roots"] or "extension_icons" not in data or "show_extension_dots" not in data or "show_extension_commas" not in data:
                save_config(config)
        except:
            pass
    else:
        save_config(config)
        
    return config

def save_config(config):
    dir_path = os.path.dirname(CONFIG_FILE)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def list_roots():
    def rgb_to_256(r: int, g: int, b: int) -> int:
        if r == g == b:
            if r < 8:   return 16
            if r > 248: return 231
            return int(((r - 8) / 247) * 24) + 232
        def _cube(x):
            if x < 48:            return 0
            if x < 115:           return 1
            return int((x - 55) / 40) if x < 175 else 5
        r6, g6, b6 = _cube(r), _cube(g), _cube(b)
        return 16 + 36 * r6 + 6 * g6 + b6

    def esc(rgb: str) -> str:
        rgb = rgb.lstrip('#')
        r, g, b = int(rgb[0:2], 16), int(rgb[2:4], 16), int(rgb[4:6], 16)
        return f'\x1b[38;5;{rgb_to_256(r,g,b)}m'

    print(f"  {esc('#9efa49')}[+] Add New Search Root\x1b[0m")
    
    config = load_config()
    roots = config.get("search_roots", {})
    for path, enabled in roots.items():
        if enabled:
            print(f"  {esc('#9efa49')}[x]\x1b[0m  {path}")
        else:
            print(f"  {esc('#808080')}[ ]\x1b[0m  {path}")

def toggle_root(selected_line):
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    clean_line = ansi_escape.sub('', selected_line).strip()
    
    if clean_line.startswith("[+]"):
        try:
            con_path = 'CON' if os.name == 'nt' else '/dev/tty'
            with open(con_path, 'r', encoding='utf-8') as f_in:
                print("\nEnter directory path to add: ", end='', flush=True)
                path = f_in.readline().strip()
                
            if path:
                path = path.strip('\'"')
                if os.path.isdir(path):
                    abs_path = os.path.abspath(path)
                    config = load_config()
                    config.setdefault("search_roots", {})[abs_path] = True
                    save_config(config)
                    print(f"\n\033[92mSuccessfully added search root: {abs_path}\033[0m")
                else:
                    print(f"\n\033[91mError: '{path}' is not a valid directory.\033[0m")
                import time; time.sleep(1.5)
        except KeyboardInterrupt:
            return
    else:
        clean_sel = clean_line[5:]
        config = load_config()
        roots = config.get("search_roots", {})
        if clean_sel in roots:
            roots[clean_sel] = not roots[clean_sel]
            save_config(config)

def delete_root(selected_line):
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    clean_line = ansi_escape.sub('', selected_line).strip()
    
    if not clean_line.startswith("[+]"):
        clean_sel = clean_line[5:]
        config = load_config()
        roots = config.get("search_roots", {})
        if clean_sel in roots:
            del roots[clean_sel]
            save_config(config)

def list_ignores():
    def rgb_to_256(r: int, g: int, b: int) -> int:
        if r == g == b:
            if r < 8:   return 16
            if r > 248: return 231
            return int(((r - 8) / 247) * 24) + 232
        def _cube(x):
            if x < 48:            return 0
            if x < 115:           return 1
            return int((x - 55) / 40) if x < 175 else 5
        r6, g6, b6 = _cube(r), _cube(g), _cube(b)
        return 16 + 36 * r6 + 6 * g6 + b6

    def esc(rgb: str) -> str:
        rgb = rgb.lstrip('#')
        r, g, b = int(rgb[0:2], 16), int(rgb[2:4], 16), int(rgb[4:6], 16)
        return f'\x1b[38;5;{rgb_to_256(r,g,b)}m'

    print(f"  {esc('#faf069')}[+] Add New Ignored Pattern\x1b[0m")
    
    config = load_config()
    visibility = config.get("visibility", {})
    for pattern, visible in visibility.items():
        if not visible:
            print(f"  {esc('#ff934b')}[x]\x1b[0m  {pattern} (Ignored)")
        else:
            print(f"  {esc('#808080')}[ ]\x1b[0m  {pattern} (Visible)")

def toggle_ignore(selected_line):
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    clean_line = ansi_escape.sub('', selected_line).strip()
    
    if clean_line.startswith("[+]"):
        try:
            con_path = 'CON' if os.name == 'nt' else '/dev/tty'
            with open(con_path, 'r', encoding='utf-8') as f_in:
                print("\nEnter pattern/name to ignore (e.g. node_modules): ", end='', flush=True)
                pattern = f_in.readline().strip()
                
            if pattern:
                raw_parts = [x.strip() for x in pattern.replace(',', ' ').split()]
                patterns = [p for p in raw_parts if p]
                if patterns:
                    config = load_config()
                    visibility = config.setdefault("visibility", {})
                    for p in patterns:
                        visibility[p] = False
                    save_config(config)
                    print(f"\n\033[92mSuccessfully added to ignore list: {', '.join(patterns)}\033[0m")
                    import time; time.sleep(1.5)
        except KeyboardInterrupt:
            return
    else:
        clean_pat = clean_line[5:]
        if " (" in clean_pat:
            pattern = clean_pat.rsplit(" (", 1)[0]
            config = load_config()
            visibility = config.get("visibility", {})
            if pattern in visibility:
                visibility[pattern] = not visibility[pattern]
                save_config(config)

def delete_ignore(selected_line):
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    clean_line = ansi_escape.sub('', selected_line).strip()
    
    if not clean_line.startswith("[+]"):
        clean_pat = clean_line[5:]
        if " (" in clean_pat:
            pattern = clean_pat.rsplit(" (", 1)[0]
            config = load_config()
            visibility = config.get("visibility", {})
            if pattern in visibility:
                del visibility[pattern]
                save_config(config)

def manage_roots_menu():
    fzf_args = [
        "fzf",
        "--ansi",
        "--track",
        "--id-nth=2..",
        "--prompt=Manage Search Roots > ",
        "--layout=reverse",
        "--border",
        "--header=Enter: Toggle/Add  |  Alt-D/Del: Delete",
        f"--bind=enter:execute(python \"{script_path}\" --toggle-root {{}})+reload(python \"{script_path}\" --list-roots)",
        f"--bind=alt-d:execute(python \"{script_path}\" --delete-root {{}})+reload(python \"{script_path}\" --list-roots)",
        f"--bind=del:execute(python \"{script_path}\" --delete-root {{}})+reload(python \"{script_path}\" --list-roots)",
        "--color=bg:#1e1e1e,fg:#d0d0d0,bg+:#2e2e2e,fg+:#ffffff,hl:#00d9ff,hl+:#00ff00,info:#afaf87,prompt:#d782ff,pointer:#d782ff,marker:#19d600,header:#888888,border:#d782ff"
    ]
    
    p_feed = subprocess.Popen(
        ["python", script_path, "--list-roots"],
        stdout=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )
    
    p_fzf = subprocess.Popen(
        fzf_args,
        stdin=p_feed.stdout,
        stdout=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )
    p_feed.stdout.close()
    p_fzf.communicate()

def manage_ignores_menu():
    fzf_args = [
        "fzf",
        "--ansi",
        "--track",
        "--id-nth=2..",
        "--prompt=Manage Ignored Patterns > ",
        "--layout=reverse",
        "--border",
        "--header=Enter: Toggle/Add  |  Alt-D/Del: Delete",
        f"--bind=enter:execute(python \"{script_path}\" --toggle-ignore {{}})+reload(python \"{script_path}\" --list-ignores)",
        f"--bind=alt-d:execute(python \"{script_path}\" --delete-ignore {{}})+reload(python \"{script_path}\" --list-ignores)",
        f"--bind=del:execute(python \"{script_path}\" --delete-ignore {{}})+reload(python \"{script_path}\" --list-ignores)",
        "--color=bg:#1e1e1e,fg:#d0d0d0,bg+:#2e2e2e,fg+:#ffffff,hl:#00d9ff,hl+:#00ff00,info:#afaf87,prompt:#d782ff,pointer:#d782ff,marker:#19d600,header:#888888,border:#d782ff"
    ]
    
    p_feed = subprocess.Popen(
        ["python", script_path, "--list-ignores"],
        stdout=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )
    
    p_fzf = subprocess.Popen(
        fzf_args,
        stdin=p_feed.stdout,
        stdout=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )
    p_feed.stdout.close()
    p_fzf.communicate()

def list_colors():
    for i in range(256):
        print(f"\x1b[38;5;{i}m  Color {i:03d}  ■■■■■■■■■■\x1b[0m")

def select_color(category_name):
    fzf_args = [
        "fzf",
        "--ansi",
        f"--prompt=Select Color for {category_name} > ",
        "--layout=reverse",
        "--border",
        "--header=Arrow keys to browse  |  Type color number to filter"
    ]
    p_feed = subprocess.Popen(
        ["python", script_path, "--list-colors-raw"],
        stdout=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )
    p_fzf = subprocess.Popen(
        fzf_args,
        stdin=p_feed.stdout,
        stdout=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )
    p_feed.stdout.close()
    stdout, _ = p_fzf.communicate()
    if stdout and p_fzf.returncode == 0:
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_line = ansi_escape.sub('', stdout.strip())
        try:
            color_str = clean_line.split()[1]
            return int(color_str)
        except:
            pass
    return None

def configure_single_icon_menu(ext_key):
    ctypes.windll.kernel32.SetConsoleTitleW(f"Runner - Configure Icon for {ext_key}")
    
    def rgb_to_256(r: int, g: int, b: int) -> int:
        if r == g == b:
            if r < 8:   return 16
            if r > 248: return 231
            return int(((r - 8) / 247) * 24) + 232
        def _cube(x):
            if x < 48:            return 0
            if x < 115:           return 1
            return int((x - 55) / 40) if x < 175 else 5
        r6, g6, b6 = _cube(r), _cube(g), _cube(b)
        return 16 + 36 * r6 + 6 * g6 + b6

    def esc(rgb: str) -> str:
        rgb = rgb.lstrip('#')
        r, g, b = int(rgb[0:2], 16), int(rgb[2:4], 16), int(rgb[4:6], 16)
        return f'\x1b[38;5;{rgb_to_256(r,g,b)}m'

    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    while True:
        config = load_config()
        icon_map = config.get("extension_icons", {})
        
        if ext_key not in icon_map:
            break
            
        entry = icon_map[ext_key]
        icon = ""
        color = 250
        if isinstance(entry, dict):
            icon = entry.get("icon", "")
            color = entry.get("color", 250)
        else:
            icon = entry
            
        pad = "  "
        options = [
            f"{pad}{esc('#9efa49')}[I] Change Icon Glyph\x1b[0m (Current: '{icon}')",
            f"{pad}{esc('#00f0ff')}[C] Change Icon Color\x1b[0m (Current: \x1b[38;5;{color}m{color}\x1b[0m)",
            f"{pad}{esc('#faf069')}[M] Modify This Extension List\x1b[0m",
            f"{pad}{esc('#d782ff')}[U] Combine with another extension list\x1b[0m",
            f"{pad}{esc('#ff5757')}[D] Delete Extension Icon mapping\x1b[0m",
            f"{pad}{esc('#808080')}[B] Back to Icon List\x1b[0m",
        ]
        
        fzf = subprocess.Popen(
            [
                "fzf", 
                "--ansi",
                f"--prompt=Configure {ext_key} > ", 
                "--layout=reverse", 
                "--border", 
                f"--header=Configure settings for {ext_key} icon",
                "--color=bg:#1e1e1e,fg:#d0d0d0,bg+:#2e2e2e,fg+:#ffffff,hl:#00d9ff,hl+:#00ff00,info:#afaf87,prompt:#d782ff,pointer:#d782ff,marker:#19d600,header:#888888,border:#d782ff"
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        stdout, _ = fzf.communicate(input="\n".join(options))
        if not stdout or fzf.returncode != 0:
            break
            
        choice = ansi_escape.sub('', stdout.strip())
        if choice.startswith("[B]"):
            break
            
        elif choice.startswith("[I]"):
            try:
                con_path = 'CON' if os.name == 'nt' else '/dev/tty'
                with open(con_path, 'r', encoding='utf-8') as f_in:
                    print(f"\nEnter new icon glyph for {ext_key} (current: '{icon}'): ", end='', flush=True)
                    new_icon = f_in.readline().strip()
                    if new_icon:
                        if isinstance(entry, dict):
                            entry["icon"] = new_icon
                        else:
                            icon_map[ext_key] = {"icon": new_icon, "color": color}
                        save_config(config)
            except KeyboardInterrupt:
                pass
                
        elif choice.startswith("[C]"):
            new_color = select_color(f"Icon: {ext_key}")
            if new_color is not None:
                if isinstance(entry, dict):
                    entry["color"] = new_color
                else:
                    icon_map[ext_key] = {"icon": icon, "color": new_color}
                save_config(config)
                
        elif choice.startswith("[M]"):
            try:
                con_path = 'CON' if os.name == 'nt' else '/dev/tty'
                with open(con_path, 'r', encoding='utf-8') as f_in:
                    print(f"\nEnter new list of extensions for this icon (current: '{ext_key}'): ", end='', flush=True)
                    val = f_in.readline().strip().lower()
                    if val:
                        raw_parts = [x.strip() for x in val.replace(',', ' ').split()]
                        parts = []
                        for part in raw_parts:
                            if not part:
                                continue
                            if part != "folder" and not part.startswith("."):
                                part = "." + part
                            parts.append(part)
                            
                        if parts:
                            new_key = ", ".join(parts)
                            if new_key != ext_key:
                                # Copy current properties to new key, delete old key
                                icon_map[new_key] = entry
                                if ext_key in icon_map:
                                    del icon_map[ext_key]
                                save_config(config)
                                ext_key = new_key # Keep submenu open for new key!
                                print(f"\n\033[92mSuccessfully updated extension list to: {new_key}\033[0m")
                                import time; time.sleep(1.5)
            except KeyboardInterrupt:
                pass
                
        elif choice.startswith("[U]"):
            show_dots = config.get("show_extension_dots", True)
            show_commas = config.get("show_extension_commas", True)
            
            def format_ext_list(k):
                parts = [x.strip() for x in k.replace(',', ' ').split()]
                cleaned = []
                for p in parts:
                    if not p:
                        continue
                    if not show_dots and p.startswith("."):
                        cleaned.append(p[1:])
                    elif show_dots and not p.startswith("."):
                        cleaned.append("." + p)
                    else:
                        cleaned.append(p)
                separator = ", " if show_commas else " "
                return separator.join(cleaned)
                
            other_options = []
            other_choices_map = {}
            for other_ext, other_entry in sorted(icon_map.items()):
                if other_ext == ext_key or other_ext == "folder":
                    continue
                other_icon = ""
                other_color = 250
                if isinstance(other_entry, dict):
                    other_icon = other_entry.get("icon", "")
                    other_color = other_entry.get("color", 250)
                else:
                    other_icon = other_entry
                    
                other_icon_width = sum(2 if ord(c) > 0x2000 or 0x1f300 <= ord(c) <= 0x1f9ff else 1 for c in other_icon)
                other_icon_pad = " " * max(1, 3 - other_icon_width)
                colored_icon = f"\x1b[38;5;{other_color}m{other_icon}\x1b[0m{other_icon_pad}"
                
                display_ext = format_ext_list(other_ext)
                option_line = f"{display_ext:<20} {colored_icon}"
                other_options.append(option_line)
                other_choices_map[ansi_escape.sub('', option_line).strip()] = other_ext
                
            if not other_options:
                print("\n\033[91mNo other extensions found to combine with.\033[0m")
                import time; time.sleep(1.5)
                continue
                
            fzf_combine = subprocess.Popen(
                [
                    "fzf", 
                    "--ansi",
                    f"--prompt=Combine {ext_key} with > ", 
                    "--layout=reverse", 
                    "--border", 
                    f"--header=Combine {ext_key} with another list (Target settings will be used)",
                    "--color=bg:#1e1e1e,fg:#d0d0d0,bg+:#2e2e2e,fg+:#ffffff,hl:#00d9ff,hl+:#00ff00,info:#afaf87,prompt:#d782ff,pointer:#d782ff,marker:#19d600,header:#888888,border:#d782ff"
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            stdout_c, _ = fzf_combine.communicate(input="\n".join(other_options))
            if stdout_c and fzf_combine.returncode == 0:
                selected_choice = ansi_escape.sub('', stdout_c.strip())
                target_key = other_choices_map.get(selected_choice)
                if target_key:
                    target_parts = [x.strip() for x in target_key.replace(',', ' ').split() if x.strip()]
                    current_parts = [x.strip() for x in ext_key.replace(',', ' ').split() if x.strip()]
                    combined_parts = target_parts + current_parts
                    combined_key = ", ".join(combined_parts)
                    
                    icon_map[combined_key] = icon_map[target_key]
                    
                    if target_key in icon_map:
                        del icon_map[target_key]
                    if ext_key in icon_map:
                        del icon_map[ext_key]
                        
                    save_config(config)
                    print(f"\n\033[92mSuccessfully combined into: {combined_key}\033[0m")
                    import time; time.sleep(1.5)
                    break
                
        elif choice.startswith("[D]"):
            del icon_map[ext_key]
            save_config(config)
            print(f"\n\033[91mDeleted icon mapping for {ext_key}.\033[0m")
            import time; time.sleep(1.0)
            break

def manage_icon_colors_menu():
    ctypes.windll.kernel32.SetConsoleTitleW("Runner - Icon Colors Configuration")
    
    def rgb_to_256(r: int, g: int, b: int) -> int:
        if r == g == b:
            if r < 8:   return 16
            if r > 248: return 231
            return int(((r - 8) / 247) * 24) + 232
        def _cube(x):
            if x < 48:            return 0
            if x < 115:           return 1
            return int((x - 55) / 40) if x < 175 else 5
        r6, g6, b6 = _cube(r), _cube(g), _cube(b)
        return 16 + 36 * r6 + 6 * g6 + b6

    def esc(rgb: str) -> str:
        rgb = rgb.lstrip('#')
        r, g, b = int(rgb[0:2], 16), int(rgb[2:4], 16), int(rgb[4:6], 16)
        return f'\x1b[38;5;{rgb_to_256(r,g,b)}m'

    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    while True:
        config = load_config()
        icon_map = config.get("extension_icons", {})
        
        show_dots = config.get("show_extension_dots", True)
        show_commas = config.get("show_extension_commas", True)
        
        dots_status = "Show Dots" if show_dots else "Hide Dots"
        commas_status = "Show Commas" if show_commas else "Hide Commas"
        
        def format_ext_list(ext_key):
            if ext_key == "folder":
                return "folder"
            parts = [x.strip() for x in ext_key.replace(',', ' ').split()]
            cleaned = []
            for p in parts:
                if not p:
                    continue
                if not show_dots and p.startswith("."):
                    cleaned.append(p[1:])
                elif show_dots and not p.startswith("."):
                    cleaned.append("." + p)
                else:
                    cleaned.append(p)
            separator = ", " if show_commas else " "
            return separator.join(cleaned)
            
        display_map = {}
        for ext in icon_map.keys():
            display_map[ext] = format_ext_list(ext)
            
        max_ext_len = max((len(val) for val in display_map.values()), default=10)
        col_width = max(10, max_ext_len)
        
        pad = "  "
        options = [
            f"{pad}{esc('#9efa49')}[+] Add New Extension Icon\x1b[0m",
            f"{pad}{esc('#faf069')}[.] Toggle Extension Dots\x1b[0m (Current: {dots_status})",
            f"{pad}{esc('#00f0ff')}[,] Toggle Extension Commas\x1b[0m (Current: {commas_status})"
        ]
        
        choices_map = {}
        for ext, entry in sorted(icon_map.items()):
            icon = ""
            color = 250
            if isinstance(entry, dict):
                icon = entry.get("icon", "")
                color = entry.get("color", 250)
            else:
                icon = entry
            
            icon_width = sum(2 if ord(c) > 0x2000 or 0x1f300 <= ord(c) <= 0x1f9ff else 1 for c in icon)
            icon_pad = " " * max(1, 3 - icon_width)
            colored_icon = f"\x1b[38;5;{color}m{icon}\x1b[0m{icon_pad}"
            
            display_ext = display_map[ext]
            option_line = f"{pad}{display_ext:<{col_width}} {colored_icon} (Current Color: \x1b[38;5;{color}m{color}\x1b[0m)"
            options.append(option_line)
            
            clean_opt = ansi_escape.sub('', option_line).strip()
            choices_map[clean_opt] = ext
            
        options.append(f"{pad}{esc('#808080')}Return to Theme Colors Menu\x1b[0m")
        
        fzf = subprocess.Popen(
            [
                "fzf", 
                "--ansi",
                "--prompt=Icon Colors > ", 
                "--layout=reverse", 
                "--border", 
                "--header=Configure Icon Colors (F5: Toggle Bookmark)",
                "--expect=f5",
                "--color=bg:#1e1e1e,fg:#d0d0d0,bg+:#2e2e2e,fg+:#ffffff,hl:#00d9ff,hl+:#00ff00,info:#afaf87,prompt:#d782ff,pointer:#d782ff,marker:#19d600,header:#888888,border:#d782ff"
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        stdout, _ = fzf.communicate(input="\n".join(options))
        if not stdout or fzf.returncode != 0:
            break
            
        lines = stdout.splitlines()
        if len(lines) < 2:
            break
        key_pressed = lines[0].strip()
        chosen_line = lines[1]
        
        choice = ansi_escape.sub('', chosen_line).strip()
        if "Return to Theme Colors Menu" in choice:
            break
            
        if "[.] Toggle Extension Dots" in choice:
            config["show_extension_dots"] = not show_dots
            save_config(config)
            continue
            
        if "[,] Toggle Extension Commas" in choice:
            config["show_extension_commas"] = not show_commas
            save_config(config)
            continue
            
        is_add = "[+] Add New Extension Icon" in choice
        ext_key = ""
        
        if key_pressed == "f5":
            target_ext = choices_map.get(choice)
            if target_ext:
                bookmark = config.get("bookmarked_config_setting")
                if isinstance(bookmark, dict) and bookmark.get("key") == target_ext and bookmark.get("type") == "icon_color":
                    config["bookmarked_config_setting"] = None
                    print(f"\n\033[93mRemoved bookmark from icon: {target_ext}\033[0m")
                else:
                    config["bookmarked_config_setting"] = {"type": "icon_color", "key": target_ext, "label": f"Configure {target_ext} Icon"}
                    print(f"\n\033[92mBookmarked icon setting: {target_ext}\033[0m")
                save_config(config)
                import time; time.sleep(1.0)
            continue
            
        if is_add:
            try:
                con_path = 'CON' if os.name == 'nt' else '/dev/tty'
                with open(con_path, 'r', encoding='utf-8') as f_in:
                    print("\nEnter extension(s) to add (e.g. .py or .7z, .rar, .zip): ", end='', flush=True)
                    val = f_in.readline().strip().lower()
                    if val:
                        raw_parts = [x.strip() for x in val.replace(',', ' ').split()]
                        added_keys = []
                        for part in raw_parts:
                            if not part:
                                continue
                            if part != "folder" and not part.startswith("."):
                                part = "." + part
                            added_keys.append(part)
                            
                        if added_keys:
                            ext_key = ", ".join(added_keys)
                            if ext_key not in icon_map:
                                icon_map[ext_key] = {"icon": "📄" if ext_key != "folder" else "📁", "color": 250}
                                save_config(config)
            except KeyboardInterrupt:
                pass
        else:
            ext_key = choices_map.get(choice)
                
        if ext_key:
            configure_single_icon_menu(ext_key)

def manage_colors_menu():
    ctypes.windll.kernel32.SetConsoleTitleW("Runner - Theme Color Configuration")
    
    def rgb_to_256(r: int, g: int, b: int) -> int:
        if r == g == b:
            if r < 8:   return 16
            if r > 248: return 231
            return int(((r - 8) / 247) * 24) + 232
        def _cube(x):
            if x < 48:            return 0
            if x < 115:           return 1
            return int((x - 55) / 40) if x < 175 else 5
        r6, g6, b6 = _cube(r), _cube(g), _cube(b)
        return 16 + 36 * r6 + 6 * g6 + b6

    def esc(rgb: str) -> str:
        rgb = rgb.lstrip('#')
        r, g, b = int(rgb[0:2], 16), int(rgb[2:4], 16), int(rgb[4:6], 16)
        return f'\x1b[38;5;{rgb_to_256(r,g,b)}m'

    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    while True:
        config = load_config()
        theme = config.get("theme", {
            "folder_normal": 208,
            "folder_bookmark": 51,
            "file_normal": 250,
            "file_bookmark": 121
        })
        bookmark = config.get("bookmarked_config_setting")
        
        pad = "  "
        options = [
            f"{pad}{esc('#9efa49')}Normal Folder Color\x1b[0m (Current: \x1b[38;5;{theme.get('folder_normal', 208)}m{theme.get('folder_normal', 208)}\x1b[0m)",
            f"{pad}{esc('#00f0ff')}Bookmark Folder Color\x1b[0m (Current: \x1b[38;5;{theme.get('folder_bookmark', 51)}m{theme.get('folder_bookmark', 51)}\x1b[0m)",
            f"{pad}{esc('#ffffff')}Normal File Color\x1b[0m (Current: \x1b[38;5;{theme.get('file_normal', 250)}m{theme.get('file_normal', 250)}\x1b[0m)",
            f"{pad}{esc('#ff934b')}Bookmark File Color\x1b[0m (Current: \x1b[38;5;{theme.get('file_bookmark', 121)}m{theme.get('file_bookmark', 121)}\x1b[0m)",
            f"{pad}{esc('#d782ff')}Configure Icon Colors\x1b[0m",
            f"{pad}{esc('#ff5757')}Reset to Default Colors\x1b[0m",
            f"{pad}{esc('#808080')}Return to Main Menu\x1b[0m",
        ]
        
        fzf = subprocess.Popen(
            [
                "fzf", 
                "--ansi",
                "--prompt=Theme Config > ", 
                "--layout=reverse", 
                "--border", 
                "--header=Configure Colors (F5: Toggle Bookmark)",
                "--expect=f5",
                "--color=bg:#1e1e1e,fg:#d0d0d0,bg+:#2e2e2e,fg+:#ffffff,hl:#00d9ff,hl+:#00ff00,info:#afaf87,prompt:#d782ff,pointer:#d782ff,marker:#19d600,header:#888888,border:#d782ff"
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        stdout, _ = fzf.communicate(input="\n".join(options))
        if not stdout or fzf.returncode != 0:
            break
            
        lines = stdout.splitlines()
        if len(lines) < 2:
            break
        key_pressed = lines[0].strip()
        chosen_line = lines[1]
        
        choice = ansi_escape.sub('', chosen_line).strip()
        if "Return to Main Menu" in choice:
            break
            
        bm_info = None
        if "Normal Folder Color" in choice:
            bm_info = {"type": "theme_color", "key": "folder_normal", "label": "Normal Folder Color"}
        elif "Bookmark Folder Color" in choice:
            bm_info = {"type": "theme_color", "key": "folder_bookmark", "label": "Bookmark Folder Color"}
        elif "Normal File Color" in choice:
            bm_info = {"type": "theme_color", "key": "file_normal", "label": "Normal File Color"}
        elif "Bookmark File Color" in choice:
            bm_info = {"type": "theme_color", "key": "file_bookmark", "label": "Bookmark File Color"}
        elif "Configure Icon Colors" in choice:
            bm_info = {"type": "theme_color", "key": "icon_colors", "label": "Configure Icon Colors"}
            
        if key_pressed == "f5":
            if bm_info:
                if isinstance(bookmark, dict) and bookmark.get("key") == bm_info["key"] and bookmark.get("type") == "theme_color":
                    config["bookmarked_config_setting"] = None
                    print(f"\n\033[93mRemoved bookmark from setting: {choice}\033[0m")
                else:
                    config["bookmarked_config_setting"] = bm_info
                    print(f"\n\033[92mBookmarked sub-setting: {choice}\033[0m")
                save_config(config)
                import time; time.sleep(1.0)
            continue
            
        if "Normal Folder Color" in choice:
            color = select_color("Normal Folder")
            if color is not None:
                config.setdefault("theme", {})["folder_normal"] = color
                save_config(config)
                
        elif "Bookmark Folder Color" in choice:
            color = select_color("Bookmark Folder")
            if color is not None:
                config.setdefault("theme", {})["folder_bookmark"] = color
                save_config(config)
                
        elif "Normal File Color" in choice:
            color = select_color("Normal File")
            if color is not None:
                config.setdefault("theme", {})["file_normal"] = color
                save_config(config)
                
        elif "Bookmark File Color" in choice:
            color = select_color("Bookmark File")
            if color is not None:
                config.setdefault("theme", {})["file_bookmark"] = color
                save_config(config)
                
        elif "Configure Icon Colors" in choice:
            manage_icon_colors_menu()
                
        elif "Reset to Default" in choice:
            config["theme"] = {
                "folder_normal": 208,
                "folder_bookmark": 51,
                "file_normal": 250,
                "file_bookmark": 121
            }
            save_config(config)
            print("\033[92mReset colors to default.\033[0m")
            import time; time.sleep(1.0)

def view_shortcuts_menu():
    ctypes.windll.kernel32.SetConsoleTitleW("Runner - Keyboard Shortcuts Guide")
    
    shortcuts = [
        "Enter       : Show Action Menu (Run/Editor/Folder/Terminal/Copy)",
        "Tab         : Multi-select items",
        "F2          : Toggle image preview mode (Chafa/Viu vs QuickLook)",
        "F3          : Toggle View Mode (Full Path vs Filename)",
        "F4          : Refresh file list",
        "F5          : Toggle bookmark on/off (Prompts for custom name)",
        "F6          : Rename bookmark custom name",
        "F7 / Ctrl-H : Open Terminal Configuration Menu",
        "Ctrl-C      : Copy full path to clipboard",
        "Ctrl-E      : Toggle folder collapse/expand",
        "Ctrl-N      : Open selected file(s) with Editor Chooser",
        "Ctrl-O      : Open file or folder location in Explorer",
        "Ctrl-P      : Toggle preview window on/off",
        "Ctrl-R      : Run file using PowerShell",
        "Alt-E       : Expand and reset all collapsed folders",
        "Alt-Up      : Move bookmark up in custom order",
        "Alt-Down    : Move bookmark down in custom order",
        "Escape      : Exit / Close Runner"
    ]
    
    fzf = subprocess.Popen(
        [
            "fzf",
            "--prompt=Shortcuts Guide > ",
            "--layout=reverse",
            "--border",
            "--header=Press Enter or Escape to return to Main Config Menu",
            "--color=bg:#1e1e1e,fg:#d0d0d0,bg+:#2e2e2e,fg+:#ffffff,hl:#00d9ff,hl+:#00ff00,info:#afaf87,prompt:#d782ff,pointer:#d782ff,marker:#19d600,header:#888888,border:#d782ff"
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )
    fzf.communicate(input="\n".join(shortcuts))

def get_installed_fonts():
    import winreg
    fonts = set()
    try:
        reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
            for i in range(winreg.QueryInfoKey(key)[1]):
                name, _, _ = winreg.EnumValue(key, i)
                clean_name = name.split("(")[0].strip()
                for suffix in ["Bold", "Italic", "Regular", "Semibold", "Light", "Oblique"]:
                    if clean_name.endswith(" " + suffix):
                        clean_name = clean_name[:-len(" " + suffix)].strip()
                if clean_name:
                    fonts.add(clean_name)
    except:
        pass
    if not fonts:
        fonts = {"Consolas", "Cascadia Code", "Lucida Console", "Courier New", "Fira Code", "JetBrains Mono"}
    return sorted(list(fonts))

def set_console_font(font_name, font_size=16):
    try:
        LF_FACESIZE = 32
        STD_OUTPUT_HANDLE = -11
        
        class COORD(ctypes.Structure):
            _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

        class CONSOLE_FONT_INFOEX(ctypes.Structure):
            _fields_ = [
                ("cbSize", ctypes.c_ulong),
                ("nFont", ctypes.c_ulong),
                ("dwFontSize", COORD),
                ("FontFamily", ctypes.c_uint),
                ("FontWeight", ctypes.c_uint),
                ("FaceName", ctypes.c_wchar * LF_FACESIZE)
            ]
            
        handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        font_info = CONSOLE_FONT_INFOEX()
        font_info.cbSize = ctypes.sizeof(CONSOLE_FONT_INFOEX)
        
        font_info.dwFontSize.X = 0
        font_info.dwFontSize.Y = font_size
        font_info.FontFamily = 54
        font_info.FontWeight = 400
        font_info.FaceName = font_name
        
        ctypes.windll.kernel32.SetCurrentConsoleFontEx(handle, False, ctypes.byref(font_info))
    except:
        pass

def manage_font_menu():
    ctypes.windll.kernel32.SetConsoleTitleW("Runner - Console Font Configuration")
    
    def rgb_to_256(r: int, g: int, b: int) -> int:
        if r == g == b:
            if r < 8:   return 16
            if r > 248: return 231
            return int(((r - 8) / 247) * 24) + 232
        def _cube(x):
            if x < 48:            return 0
            if x < 115:           return 1
            return int((x - 55) / 40) if x < 175 else 5
        r6, g6, b6 = _cube(r), _cube(g), _cube(b)
        return 16 + 36 * r6 + 6 * g6 + b6

    def esc(rgb: str) -> str:
        rgb = rgb.lstrip('#')
        r, g, b = int(rgb[0:2], 16), int(rgb[2:4], 16), int(rgb[4:6], 16)
        return f'\x1b[38;5;{rgb_to_256(r,g,b)}m'

    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    while True:
        config = load_config()
        theme = config.setdefault("theme", {})
        curr_font = theme.get("font_face", "Default Console Font")
        curr_size = theme.get("font_size", 16)
        
        pad = "  "
        options = [
            f"{pad}{esc('#9efa49')}Select Font Family\x1b[0m (Current: {curr_font})",
            f"{pad}{esc('#00f0ff')}Select Font Size\x1b[0m (Current: {curr_size}pt)",
            f"{pad}{esc('#ff5757')}Reset Font to Default\x1b[0m",
            f"{pad}{esc('#808080')}Return to Main Menu\x1b[0m",
        ]
        
        fzf = subprocess.Popen(
            [
                "fzf", 
                "--ansi",
                "--prompt=Font Config > ", 
                "--layout=reverse", 
                "--border", 
                "--header=Configure Console Font (Applies to classic conhost sessions)",
                "--color=bg:#1e1e1e,fg:#d0d0d0,bg+:#2e2e2e,fg+:#ffffff,hl:#00d9ff,hl+:#00ff00,info:#afaf87,prompt:#d782ff,pointer:#d782ff,marker:#19d600,header:#888888,border:#d782ff"
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        stdout, _ = fzf.communicate(input="\n".join(options))
        if not stdout or fzf.returncode != 0:
            break
            
        choice = ansi_escape.sub('', stdout.strip())
        if "Return to Main Menu" in choice:
            break
            
        elif "Select Font Family" in choice:
            fonts = get_installed_fonts()
            fzf_font = subprocess.Popen(
                [
                    "fzf",
                    "--prompt=Select Font Family > ",
                    "--layout=reverse",
                    "--border",
                    "--header=Search and select system font",
                    "--color=bg:#1e1e1e,fg:#d0d0d0,bg+:#2e2e2e,fg+:#ffffff,hl:#00d9ff,hl+:#00ff00,info:#afaf87,prompt:#d782ff,pointer:#d782ff,marker:#19d600,header:#888888,border:#d782ff"
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            out_font, _ = fzf_font.communicate(input="\n".join(fonts))
            if out_font and fzf_font.returncode == 0:
                selected_font = out_font.strip()
                theme["font_face"] = selected_font
                save_config(config)
                set_console_font(selected_font, curr_size)
                print(f"\033[92mApplied font: {selected_font}\033[0m")
                import time; time.sleep(1.0)
                
        elif "Select Font Size" in choice:
            sizes = ["10", "12", "14", "16", "18", "20", "22", "24", "26", "28", "32", "36", "40"]
            fzf_size = subprocess.Popen(
                [
                    "fzf",
                    "--prompt=Select Font Size > ",
                    "--layout=reverse",
                    "--border",
                    "--color=bg:#1e1e1e,fg:#d0d0d0,bg+:#2e2e2e,fg+:#ffffff,hl:#00d9ff,hl+:#00ff00,info:#afaf87,prompt:#d782ff,pointer:#d782ff,marker:#19d600,header:#888888,border:#d782ff"
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            out_size, _ = fzf_size.communicate(input="\n".join(sizes))
            if out_size and fzf_size.returncode == 0:
                selected_size = int(out_size.strip())
                theme["font_size"] = selected_size
                save_config(config)
                if "font_face" in theme:
                    set_console_font(theme["font_face"], selected_size)
                print(f"\033[92mApplied font size: {selected_size}pt\033[0m")
                import time; time.sleep(1.0)
                
        elif "Reset Font" in choice:
            if "font_face" in theme:
                del theme["font_face"]
            theme["font_size"] = 16
            save_config(config)
            print("\033[92mReset font configuration to default.\033[0m")
            import time; time.sleep(1.0)

def configure_menu():
    # Setup terminal title
    ctypes.windll.kernel32.SetConsoleTitleW("Runner - Configuration Menu")
    
    # ANSI RGB helpers
    def rgb_to_256(r: int, g: int, b: int) -> int:
        if r == g == b:
            if r < 8:   return 16
            if r > 248: return 231
            return int(((r - 8) / 247) * 24) + 232
        def _cube(x):
            if x < 48:            return 0
            if x < 115:           return 1
            return int((x - 55) / 40) if x < 175 else 5
        r6, g6, b6 = _cube(r), _cube(g), _cube(b)
        return 16 + 36 * r6 + 6 * g6 + b6

    def esc(rgb: str) -> str:
        rgb = rgb.lstrip('#')
        r, g, b = int(rgb[0:2], 16), int(rgb[2:4], 16), int(rgb[4:6], 16)
        return f'\x1b[38;5;{rgb_to_256(r,g,b)}m'

    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    while True:
        config = load_config()
        show_signs = config.get("show_collapse_indicators", True)
        signs_status = "Show signs" if show_signs else "Hide signs"
        bookmark = config.get("bookmarked_config_setting")
        
        pad = "  "
        option_templates = {
            "[D]": f"{pad}{esc('#9efa49')}[D] Configure Search Roots (Directories)\x1b[0m",
            "[I]": f"{pad}{esc('#faf069')}[I] Configure Ignored Patterns\x1b[0m",
            "[C]": f"{pad}{esc('#00f0ff')}[C] Configure Theme Colors\x1b[0m",
            "[F]": f"{pad}{esc('#ff934b')}[F] Configure Console Font\x1b[0m",
            "[S]": f"{pad}{esc('#d782ff')}[S] Toggle Folder Signs ([+] / [-])\x1b[0m (Current: {signs_status})",
            "[K]": f"{pad}{esc('#ff5757')}[K] View Keyboard Shortcuts\x1b[0m",
            "[O]": f"{pad}{esc('#ffffff')}[O] Open Config JSON in Notepad\x1b[0m",
            "[X]": f"{pad}{esc('#808080')}[X] Exit Configuration\x1b[0m",
        }
        
        options = []
        choices_map = {}
        # Prepend the bookmarked item at the top if present
        if bookmark and isinstance(bookmark, dict):
            bm_type = bookmark.get("type")
            bm_key = bookmark.get("key")
            bm_label = bookmark.get("label", "")
            
            if bm_type == "main":
                starred_opt = option_templates.get(bm_key, "").replace(pad, "⭐ ")
                if starred_opt:
                    options.append(starred_opt)
                    clean_opt = ansi_escape.sub('', starred_opt).strip()
                    choices_map[clean_opt] = {"type": "main", "key": bm_key}
            elif bm_type == "theme_color":
                color_color = esc('#00f0ff')
                if bm_key == "folder_normal":   color_color = esc('#9efa49')
                elif bm_key == "folder_bookmark": color_color = esc('#00f0ff')
                elif bm_key == "file_normal":    color_color = esc('#ffffff')
                elif bm_key == "file_bookmark":  color_color = esc('#ff934b')
                elif bm_key == "icon_colors":    color_color = esc('#d782ff')
                
                starred_opt = f"⭐ {color_color}{bm_label}\x1b[0m"
                options.append(starred_opt)
                clean_opt = ansi_escape.sub('', starred_opt).strip()
                choices_map[clean_opt] = {"type": "theme_color", "key": bm_key}
            elif bm_type == "icon_color":
                starred_opt = f"⭐ {esc('#d782ff')}Configure {bm_key} Icon\x1b[0m"
                options.append(starred_opt)
                clean_opt = ansi_escape.sub('', starred_opt).strip()
                choices_map[clean_opt] = {"type": "icon_color", "key": bm_key}
            
        for k, v in option_templates.items():
            if bookmark and isinstance(bookmark, dict) and bookmark.get("type") == "main" and k == bookmark.get("key"):
                continue
            options.append(v)
            clean_v = ansi_escape.sub('', v).strip()
            choices_map[clean_v] = {"type": "main", "key": k}
            
        # Run FZF to choose option
        fzf = subprocess.Popen(
            [
                "fzf", 
                "--ansi",
                "--prompt=Config Menu > ", 
                "--layout=reverse", 
                "--border", 
                "--header=Runner Terminal Configurator (F5: Toggle Bookmark)",
                "--expect=f5",
                "--color=bg:#1e1e1e,fg:#d0d0d0,bg+:#2e2e2e,fg+:#ffffff,hl:#00d9ff,hl+:#00ff00,info:#afaf87,prompt:#d782ff,pointer:#d782ff,marker:#19d600,header:#888888,border:#d782ff"
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        stdout, _ = fzf.communicate(input="\n".join(options))
        if not stdout or fzf.returncode != 0:
            break
            
        lines = stdout.splitlines()
        if len(lines) < 2:
            break
        key_pressed = lines[0].strip()
        chosen_line = lines[1]
        
        choice = ansi_escape.sub('', chosen_line).strip()
        selected_bm = choices_map.get(choice)
        
        if key_pressed == "f5":
            if selected_bm:
                bm_type = selected_bm["type"]
                bm_key = selected_bm["key"]
                
                if bm_type == "main" and bm_key == "[X]":
                    continue
                    
                if isinstance(bookmark, dict) and bookmark.get("type") == bm_type and bookmark.get("key") == bm_key:
                    config["bookmarked_config_setting"] = None
                    print(f"\n\033[93mRemoved bookmark\033[0m")
                else:
                    if bm_type == "main":
                        label = choice.replace("⭐ ", "").strip()
                        config["bookmarked_config_setting"] = {"type": "main", "key": bm_key, "label": label}
                    elif bm_type == "theme_color":
                        label = choice.replace("⭐ ", "").strip()
                        if " (Current:" in label:
                            label = label.split(" (Current:")[0].strip()
                        config["bookmarked_config_setting"] = {"type": "theme_color", "key": bm_key, "label": label}
                    elif bm_type == "icon_color":
                        config["bookmarked_config_setting"] = {"type": "icon_color", "key": bm_key, "label": f"Configure {bm_key} Icon"}
                        
                    print(f"\n\033[92mBookmarked setting successfully!\033[0m")
                save_config(config)
                import time; time.sleep(1.0)
            continue
            
        if selected_bm:
            bm_type = selected_bm["type"]
            bm_key = selected_bm["key"]
            
            if bm_type == "main":
                if bm_key == "[X]":
                    break
                choice = bm_key
            else:
                if bm_type == "theme_color":
                    label_mapping = {
                        "folder_normal": "Normal Folder",
                        "folder_bookmark": "Bookmark Folder",
                        "file_normal": "Normal File",
                        "file_bookmark": "Bookmark File"
                    }
                    if bm_key == "icon_colors":
                        manage_icon_colors_menu()
                    elif bm_key in label_mapping:
                        color = select_color(label_mapping[bm_key])
                        if color is not None:
                            config.setdefault("theme", {})[bm_key] = color
                            save_config(config)
                elif bm_type == "icon_color":
                    configure_single_icon_menu(bm_key)
                continue
            
        if choice.startswith("[D]"):
            manage_roots_menu()
            
        elif choice.startswith("[I]"):
            manage_ignores_menu()
            
        elif choice.startswith("[C]"):
            manage_colors_menu()
            
        elif choice.startswith("[F]"):
            manage_font_menu()
            
        elif choice.startswith("[S]"):
            config["show_collapse_indicators"] = not show_signs
            save_config(config)
            
        elif choice.startswith("[K]"):
            view_shortcuts_menu()
            
        elif choice.startswith("[O]"):
            subprocess.run(["notepad.exe", CONFIG_FILE])
            
    # Restore original title
    ctypes.windll.kernel32.SetConsoleTitleW("RUNNER")

def search_directories_and_files():
    # Load search roots from config
    config = load_config()
    roots = config.get("search_roots", {})
    directories = [path for path, enabled in roots.items() if enabled]

    # Filter out empty or None directories
    directories = [d for d in directories if d and d.strip()]

    # Ignore list (for initial load check)
    ignore_list = [".git", ".pyc"]

    # Shortcut list text for display
    shortcuts_text = r"""┌───────────────────────────────────────────────────────────────────────────┐
│                            SHORTCUTS MENU                                 │
├───────────────────────────────────────────────────────────────────────────┤
│  F2: Img Mode   F3: View Mode  F4: Refresh    F5: Bookmark   F6: Rename   │
│  F7: Configure  Alt-R: Ref/Top Ctrl-H: Configure                          │
│                                                                           │
│  Ctrl-C: Copy   Ctrl-E: Toggle Collapse       Alt-E: Expand All           │
│  Ctrl-N: Editor Ctrl-O: Folder Ctrl-P: Preview Ctrl-R: Run                 │
│  Alt-Up/Down: Move Bookmark    Enter: Menu     Tab: Select   ?: Toggle    │
└───────────────────────────────────────────────────────────────────────────┘"""

    # Create a state file to track preview mode (chafa vs quicklook)
    state_file = os.path.join(tempfile.gettempdir(), "fzf_preview_mode.txt")
    
    # Initialize with chafa mode if file doesn't exist
    if not os.path.exists(state_file):
        with open(state_file, 'w') as f:
            f.write("chafa")

    # Create PowerShell preview script with image support and toggle functionality
    preview_script_content = f'''
param($FilePath)

if (-not (Test-Path $FilePath)) {{
    Write-Host "File not found: $FilePath" -ForegroundColor Red
    exit 1
}}

# Read current preview mode from state file
$stateFile = "{state_file}"
$previewMode = "chafa"
if (Test-Path $stateFile) {{
    $previewMode = Get-Content $stateFile -Raw
    $previewMode = $previewMode.Trim()
}}

$ext = [System.IO.Path]::GetExtension($FilePath).ToLower()
$imageExtensions = @('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.ico')

if ($imageExtensions -contains $ext) {{
    if ($previewMode -eq "quicklook") {{
        # Use QuickLook for image preview
        try {{
            $quickLookPath = "C:\\Users\\nahid\\AppData\\Local\\Programs\\QuickLook\\QuickLook.exe"
            if (Test-Path $quickLookPath) {{
                Start-Process $quickLookPath -ArgumentList $FilePath -WindowStyle Hidden
                Write-Host ""
                Write-Host "[QUICKLOOK MODE - Image opened in QuickLook]" -ForegroundColor Green
                $fileInfo = Get-Item $FilePath
                Write-Host "File: $(Split-Path $FilePath -Leaf)" -ForegroundColor Cyan
                Write-Host "Size: $([math]::Round($fileInfo.Length / 1KB, 2)) KB" -ForegroundColor Gray
                Write-Host "Modified: $($fileInfo.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))" -ForegroundColor Gray
                Write-Host ""
                Write-Host "Press F2 to switch to chafa/viu preview mode" -ForegroundColor Yellow
                exit 0
            }} else {{
                Write-Host "QuickLook not found at expected location" -ForegroundColor Red
                Write-Host "Falling back to chafa/viu..." -ForegroundColor Yellow
                $previewMode = "chafa"
            }}
        }}
        catch {{
            Write-Host "Error launching QuickLook, falling back to chafa/viu" -ForegroundColor Yellow
            $previewMode = "chafa"
        }}
    }}
    
    $tempFile = $null
    $previewPath = $FilePath
    if ($ext -eq ".ico") {{
        try {{
            Add-Type -AssemblyName System.Drawing
            $ico = New-Object System.Drawing.Icon($FilePath)
            $bmp = $ico.ToBitmap()
            $tempFile = [System.IO.Path]::GetTempFileName() + ".png"
            $bmp.Save($tempFile, [System.Drawing.Imaging.ImageFormat]::Png)
            $ico.Dispose()
            $bmp.Dispose()
            $previewPath = $tempFile
        }} catch {{}}
    }}

    if ($previewMode -eq "chafa") {{
        # Try chafa for image preview with better sizing
        try {{
            $chafaPath = Get-Command chafa -ErrorAction Stop
            # Use smaller dimensions that fit better in preview pane
            & chafa --size=40x20 --symbols=block --fill=space --stretch $previewPath
            if ($tempFile -and (Test-Path $tempFile)) {{ Remove-Item $tempFile -Force }}
            Write-Host ""
            # Show file info below image
            $fileInfo = Get-Item $FilePath
            Write-Host "[CHAFA MODE]" -ForegroundColor Green
            Write-Host "File: $(Split-Path $FilePath -Leaf)" -ForegroundColor Cyan
            Write-Host "Size: $([math]::Round($fileInfo.Length / 1KB, 2)) KB" -ForegroundColor Gray
            Write-Host "Modified: $($fileInfo.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))" -ForegroundColor Gray
            Write-Host ""
            Write-Host "Press F2 to switch to QuickLook mode" -ForegroundColor Yellow
            exit 0
        }}
        catch {{
            # Try viu with smaller dimensions
            try {{
                $viuPath = Get-Command viu -ErrorAction Stop
                & viu -w 40 -h 20 $previewPath
                if ($tempFile -and (Test-Path $tempFile)) {{ Remove-Item $tempFile -Force }}
                Write-Host ""
                $fileInfo = Get-Item $FilePath
                Write-Host "[VIU MODE]" -ForegroundColor Green
                Write-Host "File: $(Split-Path $FilePath -Leaf)" -ForegroundColor Cyan
                Write-Host "Size: $([math]::Round($fileInfo.Length / 1KB, 2)) KB" -ForegroundColor Gray
                Write-Host ""
                Write-Host "Press F2 to switch to QuickLook mode" -ForegroundColor Yellow
                exit 0
            }}
            catch {{
                if ($tempFile -and (Test-Path $tempFile)) {{ Remove-Item $tempFile -Force }}
                # Fallback: show image info
                Write-Host ""
                Write-Host "[IMAGE FILE - No preview tool available]" -ForegroundColor Cyan
                Write-Host "File: $(Split-Path $FilePath -Leaf)"
                Write-Host "Extension: $ext"
                $fileInfo = Get-Item $FilePath
                Write-Host "Size: $([math]::Round($fileInfo.Length / 1KB, 2)) KB"
                Write-Host "Dimensions: $(try {{ Add-Type -AssemblyName System.Drawing; $img = [System.Drawing.Image]::FromFile($FilePath); "$($img.Width)x$($img.Height)"; $img.Dispose() }} catch {{ "Unknown" }})"
                Write-Host "Modified: $($fileInfo.LastWriteTime)"
                Write-Host ""
                Write-Host "(Install chafa: scoop install chafa or viu: scoop install viu)" -ForegroundColor Yellow
                Write-Host "Press F2 to switch to QuickLook mode" -ForegroundColor Yellow
                exit 0
            }}
        }}
    }}
}}

# For non-image files, try bat first
try {{
    $batPath = Get-Command bat -ErrorAction Stop
    & bat --style=plain --color=always --line-range :100 $FilePath
}}
catch {{
    # Fallback to Get-Content for text files
    try {{
        Write-Host "[TEXT FILE PREVIEW]" -ForegroundColor Green
        Get-Content $FilePath -Head 100 -ErrorAction Stop
    }}
    catch {{
        Write-Host "[BINARY FILE - Cannot preview]" -ForegroundColor Yellow
        Write-Host "File: $(Split-Path $FilePath -Leaf)"
        $fileInfo = Get-Item $FilePath
        Write-Host "Size: $([math]::Round($fileInfo.Length / 1KB, 2)) KB"
        Write-Host "Modified: $($fileInfo.LastWriteTime)"
    }}
}}
'''

    # Create toggle script for F2 functionality
    toggle_script_content = f'''
$stateFile = "{state_file}"
$currentMode = "chafa"

if (Test-Path $stateFile) {{
    $currentMode = Get-Content $stateFile -Raw
    $currentMode = $currentMode.Trim()
}}

if ($currentMode -eq "chafa") {{
    Set-Content $stateFile "quicklook"
    Write-Host "Switched to QuickLook mode" -ForegroundColor Green
}} else {{
    Set-Content $stateFile "chafa"
    Write-Host "Switched to chafa/viu mode" -ForegroundColor Green
}}

Start-Sleep -Milliseconds 500
'''

    # Create temp files
    temp_shortcut_file = None
    preview_script_file = None
    toggle_script_file = None
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(shortcuts_text)
            temp_shortcut_file = temp_file.name

        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.ps1') as preview_script:
            preview_script.write(preview_script_content)
            preview_script_file = preview_script.name

        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.ps1') as toggle_script:
            toggle_script.write(toggle_script_content)
            toggle_script_file = toggle_script.name

        # Get absolute paths for scripts
        editor_chooser_script = os.path.join(script_dir, "editor_chooser.py")

        # Create the menu handler Python script
        menu_script_content = '''
import sys
import os
import subprocess
import tempfile

def show_fzf_menu():
    # Read file paths from temp file
    if len(sys.argv) < 2:
        return
    
    temp_file_path = sys.argv[1]
    file_paths = []
    
    if os.path.exists(temp_file_path):
        with open(temp_file_path, 'r', encoding='utf-8') as f:
            file_paths = [line.strip() for line in f if line.strip()]
        os.remove(temp_file_path)
    
    if not file_paths:
        return
    
    files_display = "\\n".join([f"  • {os.path.basename(fp)}" for fp in file_paths])
    
    # ------------------------------------------------------------------
    # 1.  RGB → 256-colour converter
    # ------------------------------------------------------------------
    def rgb_to_256(r: int, g: int, b: int) -> int:
        """Return the closest xterm-256 colour index for an (r,g,b) triplet."""
        if r == g == b:                       # greyscale shortcut
            if r < 8:   return 16
            if r > 248: return 231
            return int(((r - 8) / 247) * 24) + 232

        # Colour cube (6×6×6 = 216 colours, indices 16–231)
        def _cube(x):                       # map 0-255 → 0-5
            if x < 48:            return 0
            if x < 115:           return 1
            return int((x - 55) / 40) if x < 175 else 5
        r6, g6, b6 = _cube(r), _cube(g), _cube(b)
        return 16 + 36 * r6 + 6 * g6 + b6

    # ------------------------------------------------------------------
    # 2.  Helper that builds the escape sequence from an RGB hex string
    # ------------------------------------------------------------------
    def esc(rgb: str) -> str:
        """#rrggbb  ->  \x1b[38;5;NNNm"""
        rgb = rgb.lstrip('#')
        r, g, b = int(rgb[0:2], 16), int(rgb[2:4], 16), int(rgb[4:6], 16)
        return f'\x1b[38;5;{rgb_to_256(r,g,b)}m'

    # ---------- coloured, padded menu lines --------------------------
    pad = "  "
    menu_options = [
        f"{pad}{esc('#9efa49')}  Run\x1b[0m\t{len(file_paths)}",
        f"{pad}{esc('#19d600')}  Editor\x1b[0m\t{len(file_paths)}",
        f"{pad}{esc('#faf069')}  Folder\x1b[0m\t{len(file_paths)}",
        f"{pad}{esc('#ffffff')}  Terminal\x1b[0m\t{len(file_paths)}",
        f"{pad}{esc('#ffffff')} 󰴠 Copy path\x1b[0m\t{len(file_paths)}",
        f"{pad}{esc('#ff5757')} 󰆴 Delete\x1b[0m\t{len(file_paths)}",
    ]
    # ------------------------------------------------------------------
    
    preview_file_path = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as preview_file:
            preview_file.write(files_display)
            preview_file_path = preview_file.name

        fzf_args = [
            "fzf",
            "--ansi",                       # << keep colours
            "--prompt=Select action: ",
            "--layout=reverse", 
            f"--header=Choose action for {len(file_paths)} selected file(s):",
            "--with-nth=1",
            "--delimiter=\t",
            "--border",
            "--height=100%",                 # taller window
            f"--preview=bat --color=always --style=plain {preview_file_path} || type {preview_file_path}",
            "--preview-window=right:60%:border-left",
            "--color=bg:#1e1e1e,fg:#d0d0d0,bg+:#2e2e2e,fg+:#ffffff,hl:#00d9ff,hl+:#00ff00,info:#afaf87,prompt:#d782ff,pointer:#d782ff,marker:#19d600,header:#888888,border:#d782ff"
        ]
        
        process = subprocess.Popen(fzf_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding='utf-8')
        menu_input = '\\n'.join(menu_options)
        stdout, _ = process.communicate(input=menu_input)
        
        if stdout and process.returncode == 0:
            selection = stdout.strip()
            #! Open files with Editor Chooser
            if selection.startswith(''):
                if len(sys.argv) > 2:
                    editor_chooser_script = sys.argv[2]
                    # We need to run the editor chooser with the python interpreter
                    subprocess.run(['python', editor_chooser_script] + file_paths)


            #! Open all folder locations
            elif selection.startswith(''):
                for file_path in file_paths:
                    if os.path.isdir(file_path):
                        subprocess.run(['explorer.exe', file_path])
                    else:
                        subprocess.run(['explorer.exe', '/select,', file_path])
            #! Run all files
            elif selection.startswith(''):
                for file_path in file_paths:
                    subprocess.run(['powershell', '-command', f'Start-Process -FilePath "{file_path}"'])
            elif selection.startswith('󰴠'):
                # Copy all file paths to clipboard
                paths_text = '\\n'.join(file_paths)
                subprocess.run(['powershell', '-command', f'Set-Clipboard -Value "{paths_text}"'], shell=True)
            #! Open terminal in file directory
            elif selection.startswith(''):
                for file_path in file_paths:
                    dir_path = os.path.dirname(os.path.abspath(file_path))
                    # subprocess.run(f'start cmd /k "cd /d "{dir_path}""', shell=True)
                    subprocess.run(['start', 'pwsh', '-NoExit', '-Command', f'Set-Location "{dir_path}"'], shell=True)
            #! Delete files without confirmation
            elif selection.startswith('󰆴'): # Delete
                for file_path in file_paths:
                    try:
                        os.remove(file_path)
                    except OSError as e:
                        print(f"Error deleting {file_path}: {e}")

    except Exception as e:
        print(f"Error in menu: {e}")
    finally:
        if preview_file_path and os.path.exists(preview_file_path):
            os.remove(preview_file_path)

if __name__ == "__main__":
    show_fzf_menu()
'''

        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.py') as menu_script_file:
            menu_script_file.write(menu_script_content)
            menu_script_path = menu_script_file.name

        # Create simple batch file
        batch_content = f'''@echo off
setlocal enabledelayedexpansion

rem Create a temp file for the selected paths
set "temp_file=%temp%\\fzf_selected_%random%.txt"

rem Write each argument to the temp file (one per line)
:writeloop
if "%~1"=="" goto done
echo %~1 >> "!temp_file!"
shift
goto writeloop

:done

rem Call the Python menu script
python "{menu_script_path}" "!temp_file!" "{editor_chooser_script}"
'''

        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.bat') as batch_temp:
            batch_temp.write(batch_content)
            batch_file = batch_temp.name


        # Create file feeder script that outputs files in different formats based on view mode
        bookmarks_file = os.path.join(script_dir, "bookmarks.json")
        config_file = os.path.join(script_dir, "config.json")
        feeder_script_content = f'''
import os
import sys
import json

# Fix Unicode encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
        sys.stdout.flush()
    except OSError:
        sys.exit(0)

bookmarks_file = r"{bookmarks_file}"
config_file = r"{config_file}"
collapsed_file = r"{COLLAPSED_FILE}"
directories = {repr(directories)}

# Load config
config = {{
    "theme": {{"folder_normal": 208, "folder_bookmark": 51, "file_normal": 250, "file_bookmark": 121}},
    "visibility": {{
        ".git": False, "__pycache__": False, "node_modules": False, ".venv": False, 
        ".vscode": False, "obj": False, "bin": False
    }},
    "view_mode": "full",
    "show_collapse_indicators": True,
    "extension_icons": {{
        ".py": {{"icon": "🐍", "color": 220}},
        ".json": {{"icon": "⚙️", "color": 215}},
        ".md": {{"icon": "📝", "color": 39}},
        ".txt": {{"icon": "📄", "color": 250}},
        ".png": {{"icon": "🖼️", "color": 197}},
        ".jpg": {{"icon": "🖼️", "color": 197}},
        ".jpeg": {{"icon": "🖼️", "color": 197}},
        ".gif": {{"icon": "🖼️", "color": 197}},
        ".webp": {{"icon": "🖼️", "color": 197}},
        ".ico": {{"icon": "🎨", "color": 39}},
        ".svg": {{"icon": "🎨", "color": 39}},
        ".html": {{"icon": "🌐", "color": 202}},
        ".css": {{"icon": "🎨", "color": 39}},
        ".js": {{"icon": "📜", "color": 220}},
        ".ts": {{"icon": "📜", "color": 39}},
        ".cpp": {{"icon": "⚙️", "color": 110}},
        ".h": {{"icon": "⚙️", "color": 110}},
        ".cs": {{"icon": "⚙️", "color": 110}},
        ".go": {{"icon": "🐹", "color": 81}},
        ".rs": {{"icon": "🦀", "color": 208}},
        ".pdf": {{"icon": "📕", "color": 196}},
        ".zip": {{"icon": "📦", "color": 220}},
        ".tar": {{"icon": "📦", "color": 220}},
        ".gz": {{"icon": "📦", "color": 220}},
        ".7z": {{"icon": "📦", "color": 220}},
        "folder": {{"icon": "📁", "color": 208}}
    }}
}}
if os.path.exists(config_file):
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if "theme" in data: config["theme"].update(data["theme"])
            if "visibility" in data: config["visibility"] = data["visibility"]
            if "view_mode" in data: config["view_mode"] = data["view_mode"]
            if "show_collapse_indicators" in data: config["show_collapse_indicators"] = data["show_collapse_indicators"]
            if "extension_icons" in data: config["extension_icons"] = data["extension_icons"]
    except: pass

view_mode = config["view_mode"]

# Toggle mode if requested
if len(sys.argv) > 1 and sys.argv[1] == "--toggle":
    view_mode = "name" if view_mode == "full" else "full"
    config["view_mode"] = view_mode
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except: pass

theme = config["theme"]
# Ignore list is now defined as anything marked False in visibility
ignore_list = [k for k, v in config["visibility"].items() if v == False]

# Load bookmarks
bookmarks = []
if os.path.exists(bookmarks_file):
    try:
        with open(bookmarks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            bookmarks = [b if isinstance(b, dict) else {{"path": b, "name": ""}} for b in data]
    except:
        bookmarks = []

# Load collapsed folders
collapsed = set()
if os.path.exists(collapsed_file):
    try:
        with open(collapsed_file, 'r', encoding='utf-8') as f:
            collapsed = set(os.path.normpath(p).lower() for p in json.load(f))
    except:
        pass

# Helper function to format display
def format_display(full_path, is_bookmarked, tree_prefix=""):
    is_dir = os.path.isdir(full_path)
    is_collapsed = is_dir and os.path.normpath(full_path).lower() in collapsed
    
    indicator = ""
    if is_dir and config.get("show_collapse_indicators", True):
        indicator = "[+] " if is_collapsed else "[-] "
        
    marker = "* " if is_bookmarked else ""
    
    # Determine colors and icons
    icon = ""
    icon_map = config.get("extension_icons", {{}})
    
    if is_dir:
        if is_bookmarked:
            line_color = theme['folder_bookmark']
        else:
            line_color = theme['folder_normal']
            
        entry = icon_map.get("folder", {{}})
        if isinstance(entry, dict):
            folder_icon = entry.get("icon", "📁")
            icon_color = entry.get("color", line_color)
        else:
            folder_icon = entry
            icon_color = line_color
            
        if folder_icon:
            icon_width = sum(2 if ord(c) > 0x2000 or 0x1f300 <= ord(c) <= 0x1f9ff else 1 for c in folder_icon)
            padding = " " * max(1, 3 - icon_width)
            icon = f"\033[38;5;{{icon_color}}m{{folder_icon}}\033[38;5;{{line_color}}m{{padding}}"
    else:
        if is_bookmarked:
            line_color = theme['file_bookmark']
        else:
            line_color = theme['file_normal']
            
        ext = os.path.splitext(full_path)[1].lower()
        file_icon = None
        icon_color = line_color
        
        # Find matching key in icon_map (which could be a group key like ".7z, .rar, .zip")
        for key, entry in icon_map.items():
            if key == "folder":
                continue
            extensions = [x.strip().lower() for x in key.replace(',', ' ').split()]
            if ext in extensions:
                if isinstance(entry, dict):
                    file_icon = entry.get("icon", "📄")
                    icon_color = entry.get("color", line_color)
                else:
                    file_icon = entry
                    icon_color = line_color
                break
                
        # If no match, fallback to default file icon "📄"
        if not file_icon:
            file_icon = "📄"
            icon_color = line_color
            
        if file_icon:
            icon_width = sum(2 if ord(c) > 0x2000 or 0x1f300 <= ord(c) <= 0x1f9ff else 1 for c in file_icon)
            padding = " " * max(1, 3 - icon_width)
            icon = f"\033[38;5;{{icon_color}}m{{file_icon}}\033[38;5;{{line_color}}m{{padding}}"
        
    custom_name = ""
    if is_bookmarked:
        bm = next((b for b in bookmarks if b['path'] == full_path), None)
        if bm:
            custom_name = bm.get('name', '')

    if custom_name:
        display = f"{{marker}}{{tree_prefix}}{{indicator}}{{icon}}{{custom_name}}"
    elif view_mode == "name":
        path_norm = full_path.rstrip(os.sep)
        name = os.path.basename(path_norm)
        if not name and ":" in path_norm:
            name = path_norm
            parent = ""
        else:
            parent = os.path.basename(os.path.dirname(path_norm))
        display = f"{{marker}}{{tree_prefix}}{{indicator}}{{icon}}{{name}} ({{parent}})"
    else:
        display = f"{{marker}}{{tree_prefix}}{{indicator}}{{icon}}{{full_path}}"
    
    display = f"\033[38;5;{{line_color}}m{{display}}\033[0m"
    return display

# Helper to check if child is descendant of parent
def is_descendant(parent_path, child_path):
    p = os.path.normpath(parent_path).lower()
    c = os.path.normpath(child_path).lower()
    if p == c:
        return False
    return c.startswith(p + os.sep) or (p.endswith(os.sep) and c.startswith(p))

# Deduplicate bookmarks by path (case-insensitive, normalized)
seen_bms = set()
unique_bookmarks = []
for bm_item in bookmarks:
    p_norm = os.path.normpath(bm_item['path']).lower()
    if p_norm not in seen_bms:
        seen_bms.add(p_norm)
        unique_bookmarks.append(bm_item)
bookmarks = unique_bookmarks

# Build hierarchy
roots = []
children_map = {{}}
for bm_item in bookmarks:
    path = bm_item['path']
    ancestors = [other for other in bookmarks if is_descendant(other['path'], path)]
    if not ancestors:
        roots.append(bm_item)
    else:
        # closest ancestor has the longest path
        closest = max(ancestors, key=lambda x: len(x['path']))
        children_map.setdefault(closest['path'], []).append(bm_item)

# Sort roots and children according to their index in the flat bookmarks list
bm_paths = [b['path'] for b in bookmarks]
def bookmark_sort_key(item):
    try:
        return bm_paths.index(item['path'])
    except:
        return 999999

roots.sort(key=bookmark_sort_key)
for path in children_map:
    children_map[path].sort(key=bookmark_sort_key)

# Traverse tree and collect ordered bookmarks with depths
ordered_bookmarks = []
def traverse(bm_item, prefix, is_root, is_final):
    if is_root:
        tree_prefix = ""
        next_prefix = ""
    else:
        connector = "└── " if is_final else "├── "
        tree_prefix = prefix + connector
        next_prefix = prefix + ("    " if is_final else "│   ")
        
    ordered_bookmarks.append((bm_item, tree_prefix))
    
    children = children_map.get(bm_item['path'], [])
    n = len(children)
    for idx, child in enumerate(children):
        traverse(child, next_prefix, False, idx == n - 1)

n_roots = len(roots)
for idx, root in enumerate(roots):
    traverse(root, "", True, idx == n_roots - 1)

# Output bookmarked files first in tree order
for bm_item, tree_prefix in ordered_bookmarks:
    bm = bm_item['path']
    if os.path.exists(bm):
        display = format_display(bm, True, tree_prefix)
        safe_print(f"{{display}}\\t{{bm}}")

# Recursive tree walk helper to output files/folders with connectors
def walk_tree(root_dir, prefix="", is_final=True):
    try:
        entries = os.listdir(root_dir)
    except:
        return
        
    valid_entries = []
    for name in entries:
        full_path = os.path.join(root_dir, name)
        if name in ignore_list or any(i in name for i in ignore_list):
            continue
        if full_path in printed_paths:
            continue
        valid_entries.append(name)
        
    def entry_sort_key(name):
        full_path = os.path.join(root_dir, name)
        is_dir = os.path.isdir(full_path)
        return (is_dir, name.lower())
        
    valid_entries.sort(key=entry_sort_key)
    
    n = len(valid_entries)
    for idx, name in enumerate(valid_entries):
        full_path = os.path.join(root_dir, name)
        is_entry_final = (idx == n - 1)
        
        connector = "└── " if is_entry_final else "├── "
        next_prefix = prefix + ("    " if is_entry_final else "│   ")
        
        is_dir = os.path.isdir(full_path)
        is_collapsed = is_dir and os.path.normpath(full_path).lower() in collapsed
        
        display = format_display(full_path, False, prefix + connector)
        safe_print(f"{{display}}\\t{{full_path}}")
        printed_paths.add(full_path)
        
        if is_dir and not is_collapsed:
            walk_tree(full_path, next_prefix, is_entry_final)

# Output other files and directories
printed_paths = set()
for root_dir in directories:
    if not os.path.isdir(root_dir):
        continue
    if root_dir in printed_paths:
        continue
        
    # Print the root directory itself (depth 0, no tree connector)
    display = format_display(root_dir, False, "")
    safe_print(f"{{display}}\\t{{root_dir}}")
    printed_paths.add(root_dir)
    
    root_norm = os.path.normpath(root_dir).lower()
    is_collapsed = root_norm in collapsed
    if not is_collapsed:
        walk_tree(root_dir, "", True)
'''
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.py') as feeder_script:
            feeder_script.write(feeder_script_content)
            feeder_script_file = feeder_script.name
        

           # Shortcut help header (toggled by ?)
        help_header = r"""┌───────────────────────────────────────────────────────────────────────────┐
│                            SHORTCUTS MENU                                 │
├───────────────────────────────────────────────────────────────────────────┤
│  [ FUNCTION KEYS ]                                                        │
│  F2        : Toggle image preview mode (chafa/viu vs QuickLook)           │
│  F3        : Toggle view mode (Full Path vs Filename)                     │
│  F4        : Refresh file list (keeps focus)                              │
│  Alt-R     : Refresh file list (resets to top)                            │
│  F5        : Toggle bookmark on/off (Prompts for custom name)             │
│  F6        : Rename bookmark custom name                                  │
│  F7        : Terminal Configurator (roots/ignores)                         │
│                                                                           │
│  [ CONTROL KEYS ]                                                         │
│  Ctrl-C    : Copy full file path to clipboard                             │
│  Ctrl-E    : Toggle collapse/expand on folder                             │
│  Ctrl-N    : Open file with Editor Chooser                                │
│  Ctrl-O    : Open file location in Explorer                               │
│  Ctrl-P    : Toggle preview window on/off                                 │
│  Ctrl-R    : Run file with PowerShell Start-Process                       │
│                                                                           │
│  [ NAVIGATION & OTHER ]                                                   │
│  Alt-E     : Expand/reset all collapsed folders                           │
│  Alt-Up    : Move bookmarked file up in order                             │
│  Alt-Down  : Move bookmarked file down in order                           │
│  Enter     : Show action menu (Editor/Folder/Run/Copy/Terminal)           │
│  Tab       : Multi-select files                                           │
│  ?         : Toggle this shortcuts help header                            │
└───────────────────────────────────────────────────────────────────────────┘"""
          
        fzf_args = [
            "fzf",
            "--ansi",
            "--multi",
            "--no-sort",
            "--exact",
            "--track",
            "--id-nth=2",
            "--with-nth=1",
            "--delimiter=\t",
            "--prompt=Search [?] > ",
            "--header-first",
            "--no-header",
            f"--header={help_header}",
            f"--preview=powershell -ExecutionPolicy Bypass -File \"{preview_script_file}\" {{2}}",
            "--preview-window=right:50%:hidden",
            "--border",
            "--layout=reverse",
            "--color=bg:#1e1e1e,fg:#d0d0d0,bg+:#2e2e2e,fg+:#ffffff,hl:#00d9ff,hl+:#00ff00,info:#afaf87,prompt:#d782ff,pointer:#d782ff,marker:#19d600,header:#888888,border:#d782ff",
            f"--bind=enter:execute({batch_file} {{+2}})",
            f"--bind=ctrl-e:execute-silent(python \"{script_path}\" --toggle-collapse {{2}})+reload(python \"{feeder_script_file}\")",
            f"--bind=ctrl-n:execute-silent(python \"{editor_chooser_script}\" {{+2}})",
            f"--bind=ctrl-o:execute-silent(python \"{script_path}\" --open-item {{2}})",
            "--bind=ctrl-c:execute-silent(echo {2} | clip)",
            "--bind=ctrl-r:execute-silent(powershell -command Start-Process '{2}')",
            f"--bind=f2:execute-silent(powershell -ExecutionPolicy Bypass -File \"{toggle_script_file}\")+refresh-preview",
            f"--bind=f3:reload(python \"{feeder_script_file}\" --toggle)",
            f"--bind=f4:reload(python \"{feeder_script_file}\")",
            f"--bind=alt-r:reload(python \"{feeder_script_file}\")+first",
            f"--bind=f5:execute(python \"{script_path}\" --toggle-bookmark {{2}})+reload(python \"{feeder_script_file}\")",
            f"--bind=f6:execute(python \"{script_path}\" --rename-bookmark {{2}})+reload(python \"{feeder_script_file}\")",
            f"--bind=f7:execute(python \"{script_path}\" --configure)+reload(python \"{feeder_script_file}\")",
            f"--bind=ctrl-h:execute(python \"{script_path}\" --configure)+reload(python \"{feeder_script_file}\")",
            "--bind=ctrl-p:toggle-preview",
            "--bind=?:toggle-header",
            "--bind=start:toggle-header",
            f"--bind=alt-e:execute-silent(python \"{script_path}\" --reset-collapsed)+reload(python \"{feeder_script_file}\")",
            f"--bind=alt-up:execute-silent(python \"{script_path}\" --move-bookmark up {{2}})+reload(python \"{feeder_script_file}\")+up",
            f"--bind=alt-down:execute-silent(python \"{script_path}\" --move-bookmark down {{2}})+reload(python \"{feeder_script_file}\")+down",
        ]

        # Start fzf process with initial file feed from feeder script
        # Use the feeder script for initial load to respect saved view mode and show bookmarks first
        initial_feed = subprocess.Popen(
            ['python', feeder_script_file],
            stdout=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        process = subprocess.Popen(fzf_args, stdin=initial_feed.stdout, text=True, encoding='utf-8')
        initial_feed.stdout.close()  # Allow feeder to receive SIGPIPE if fzf exits
        process.wait()

        # Clean up temp files
        for temp_file in [batch_file, menu_script_path, preview_script_file, toggle_script_file]:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

    except FileNotFoundError:
        print("Error: 'fzf' or 'bat' command not found.", file=sys.stderr)
        print("Please ensure fzf and bat are installed and in your system's PATH.", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
    finally:
        # Clean up the temporary file and state file
        if temp_shortcut_file and os.path.exists(temp_shortcut_file):
            os.remove(temp_shortcut_file)
        
        # Clean up state file when program exits
        state_file = os.path.join(tempfile.gettempdir(), "fzf_preview_mode.txt")
        if os.path.exists(state_file):
            try:
                os.remove(state_file)
            except:
                pass

def rename_bookmark(file_path):
    if not os.path.exists(BOOKMARKS_FILE): return
    try:
        with open(BOOKMARKS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            bookmarks = [b if isinstance(b, dict) else {"path": b, "name": ""} for b in data]
    except: return
    
    bm = next((b for b in bookmarks if b['path'] == file_path), None)
    if not bm:
        print(f"\n\033[93mItem is not bookmarked. Bookmark it first (F5).\033[0m")
        import time
        time.sleep(1)
        return
        
    try:
        con_path = 'CON' if os.name == 'nt' else '/dev/tty'
        with open(con_path, 'r') as f_in:
            print(f"\n\033[96mRenaming Bookmark: {file_path}\033[0m")
            print(f"Current name: {bm.get('name', 'None')}")
            print("Enter new custom name (leave empty for default, Ctrl+C to cancel): ", end='', flush=True)
            new_name = f_in.readline().strip()
            bm['name'] = new_name
    except KeyboardInterrupt:
        print("\n\033[91mCancelled renaming.\033[0m")
        import time
        time.sleep(1)
        return
    except Exception as e:
        print(f"Error: {e}")
        import time
        time.sleep(1)
        return
        
    with open(BOOKMARKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(bookmarks, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--toggle-bookmark" and len(sys.argv) > 2:
            toggle_bookmark(sys.argv[2])
            sys.exit(0)
        elif sys.argv[1] == "--toggle-collapse" and len(sys.argv) > 2:
            toggle_collapse(sys.argv[2])
            sys.exit(0)
        elif sys.argv[1] == "--reset-collapsed":
            reset_collapsed()
            sys.exit(0)
        elif sys.argv[1] == "--configure":
            configure_menu()
            sys.exit(0)
        elif sys.argv[1] == "--list-roots":
            list_roots()
            sys.exit(0)
        elif sys.argv[1] == "--toggle-root" and len(sys.argv) > 2:
            toggle_root(sys.argv[2])
            sys.exit(0)
        elif sys.argv[1] == "--delete-root" and len(sys.argv) > 2:
            delete_root(sys.argv[2])
            sys.exit(0)
        elif sys.argv[1] == "--list-ignores":
            list_ignores()
            sys.exit(0)
        elif sys.argv[1] == "--list-colors-raw":
            list_colors()
            sys.exit(0)
        elif sys.argv[1] == "--toggle-ignore" and len(sys.argv) > 2:
            toggle_ignore(sys.argv[2])
            sys.exit(0)
        elif sys.argv[1] == "--delete-ignore" and len(sys.argv) > 2:
            delete_ignore(sys.argv[2])
            sys.exit(0)
        elif sys.argv[1] == "--rename-bookmark" and len(sys.argv) > 2:
            rename_bookmark(sys.argv[2])
            sys.exit(0)
        elif sys.argv[1] == "--move-bookmark" and len(sys.argv) > 3:
            direction = -1 if sys.argv[2] == "up" else 1
            move_bookmark(sys.argv[3], direction)
            sys.exit(0)
        elif sys.argv[1] == "--open-item" and len(sys.argv) > 2:
            path = sys.argv[2]
            if os.path.isdir(path):
                subprocess.run(['explorer.exe', path])
            else:
                subprocess.run(['explorer.exe', '/select,', path])
            sys.exit(0)
    
    search_directories_and_files()

