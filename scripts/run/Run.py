import os
import subprocess
import tempfile
import sys
import json
import ctypes

ctypes.windll.kernel32.SetConsoleTitleW("RUNNER")

BOOKMARKS_FILE = r"C:\@delta\db\FZF_launcher\bookmarks.json"
COLLAPSED_FILE = r"C:\@delta\db\FZF_launcher\collapsed.json"

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
    
    idx = next((i for i, b in enumerate(bookmarks) if b['path'] == file_path), -1)
    if idx == -1: return
    new_idx = idx + direction
    if 0 <= new_idx < len(bookmarks):
        bookmarks[idx], bookmarks[new_idx] = bookmarks[new_idx], bookmarks[idx]
        with open(BOOKMARKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(bookmarks, f, indent=2, ensure_ascii=False)


def search_directories_and_files():
    # Load search roots from config
    config_file = r"C:\@delta\db\FZF_launcher\config.json"
    directories = []
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                cfg = json.load(f)
                roots = cfg.get("search_roots", {})
                directories = [path for path, enabled in roots.items() if enabled]
        except: pass
    
    # Fallback to defaults if config is empty or missing
    if not directories:
        directories = [
            r"C:\@delta\ms1",
            r"C:\@delta\db",
            r"C:\@delta\msBackups",
            r"C:\Users\nahid\Pictures",
            "D:\\"
        ]

    # Filter out empty or None directories
    directories = [d for d in directories if d and d.strip()]

    # Ignore list (for initial load check)
    ignore_list = [".git", ".pyc"]

    # Shortcut list text for display
    shortcuts_text = r"""┌───────────────────────────────────────────────────────────────────────────┐
│                            SHORTCUTS MENU                                 │
├───────────────────────────────────────────────────────────────────────────┤
│  F2: Img Mode   F3: View Mode  F4: Refresh    F5: Bookmark   F6: Rename   │
│  F7: Configuration             Ctrl-H: Full Help GUI                      │
│                                                                           │
│  Ctrl-C: Copy   Ctrl-E: Toggle Collapse       Ctrl-N: Editor              │
│  Ctrl-O: Folder Ctrl-P: Preview Ctrl-R: Run   Alt-Up/Down: Move Bookmark  │
│  Enter: Action Menu     Tab: Multi-select     ?: Toggle this header       │
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
    
    if ($previewMode -eq "chafa") {{
        # Try chafa for image preview with better sizing
        try {{
            $chafaPath = Get-Command chafa -ErrorAction Stop
            # Use smaller dimensions that fit better in preview pane
            & chafa --size=40x20 --symbols=block --fill=space --stretch $FilePath
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
                & viu -w 40 -h 20 $FilePath
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
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.abspath(__file__)
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


        # View mode state file for F3 toggle (full path vs filename)
        view_mode_file = r"C:\@delta\db\FZF_launcher\run_settings.txt"
        if not os.path.exists(view_mode_file):
            os.makedirs(os.path.dirname(view_mode_file), exist_ok=True)
            with open(view_mode_file, 'w') as f:
                f.write("full")
        
        # Create file feeder script that outputs files in different formats based on view mode
        bookmarks_file = r"C:\@delta\db\FZF_launcher\bookmarks.json"
        config_file = r"C:\@delta\db\FZF_launcher\config.json"
        feeder_script_content = f'''
import os
import sys
import json

# Fix Unicode encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

view_mode_file = r"{view_mode_file}"
bookmarks_file = r"{bookmarks_file}"
config_file = r"{config_file}"
directories = {repr(directories)}

# Read current view mode
view_mode = "full"
if os.path.exists(view_mode_file):
    with open(view_mode_file, 'r') as f:
        view_mode = f.read().strip()

# Toggle mode if requested
if len(sys.argv) > 1 and sys.argv[1] == "--toggle":
    view_mode = "name" if view_mode == "full" else "full"
    with open(view_mode_file, 'w') as f:
        f.write(view_mode)

# Load config
config = {{
    "theme": {{"folder_normal": 208, "folder_bookmark": 51, "file_normal": 250, "file_bookmark": 121}},
    "visibility": {{
        ".git": False, "__pycache__": False, "node_modules": False, ".venv": False, 
        ".vscode": False, "obj": False, "bin": False
    }}
}}
if os.path.exists(config_file):
    try:
        with open(config_file, 'r') as f:
            data = json.load(f)
            if "theme" in data: config["theme"].update(data["theme"])
            if "visibility" in data: config["visibility"] = data["visibility"]
            elif "ignore_list" in data:
                for item in data["ignore_list"]: config["visibility"][item] = False
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
collapsed_file = r"C:\@delta\db\FZF_launcher\collapsed.json"
if os.path.exists(collapsed_file):
    try:
        with open(collapsed_file, 'r', encoding='utf-8') as f:
            collapsed = set(os.path.normpath(p).lower() for p in json.load(f))
    except:
        pass

# Helper function to format display
def format_display(full_path, is_bookmarked, depth=0):
    indent = "  " * depth
    is_dir = os.path.isdir(full_path)
    is_collapsed = is_dir and os.path.normpath(full_path).lower() in collapsed
    
    indicator = ""
    if is_dir:
        indicator = " ▸" if is_collapsed else " ▾"
        
    marker = f"{{indent}}* " if is_bookmarked else f"{{indent}}  "
    
    custom_name = ""
    if is_bookmarked:
        bm = next((b for b in bookmarks if b['path'] == full_path), None)
        if bm:
            custom_name = bm.get('name', '')

    if custom_name:
        display = f"{{marker}}{{custom_name}}{{indicator}}"
    elif view_mode == "name":
        path_norm = full_path.rstrip(os.sep)
        name = os.path.basename(path_norm)
        if not name and ":" in path_norm:
            name = path_norm
            parent = ""
        else:
            parent = os.path.basename(os.path.dirname(path_norm))
        display = f"{{marker}}{{name}}{{indicator}} ({{parent}})"
    else:
        display = f"{{marker}}{{full_path}}{{indicator}}"
    
    if is_dir:
        if is_bookmarked:
            display = f"\033[38;5;{{theme['folder_bookmark']}}m{{display}}\033[0m"
        else:
            display = f"\033[38;5;{{theme['folder_normal']}}m{{display}}\033[0m"
    elif is_bookmarked:
        display = f"\033[38;5;{{theme['file_bookmark']}}m{{display}}\033[0m"
    else:
        display = f"\033[38;5;{{theme['file_normal']}}m{{display}}\033[0m"
    
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

# Traverse tree and collect ordered bookmarks with depths
ordered_bookmarks = []
def traverse(bm_item, depth):
    ordered_bookmarks.append((bm_item, depth))
    for child in children_map.get(bm_item['path'], []):
        traverse(child, depth + 1)

for root in roots:
    traverse(root, 0)

# Output bookmarked files first in tree order
for bm_item, depth in ordered_bookmarks:
    bm = bm_item['path']
    if os.path.exists(bm):
        display = format_display(bm, True, depth)
        print(f"{{display}}\\t{{bm}}")

# Helper to get depth of path relative to search root
def get_path_depth(root_dir, path):
    try:
        rel = os.path.relpath(path, root_dir)
        if rel == ".":
            return 0
        return len(rel.split(os.sep))
    except:
        return 0

# Output other files and directories
printed_paths = set()
for root_dir in directories:
    if not os.path.isdir(root_dir):
        continue
    for root, dirs, files in os.walk(root_dir, onerror=lambda e: None):
        # Prune ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_list and not any(i in d for i in ignore_list)]
        
        # Check if root is collapsed
        root_norm = os.path.normpath(root).lower()
        is_collapsed = root_norm in collapsed
        
        # Process the current directory (root)
        if root not in printed_paths:
            # Final check to avoid showing ignored root paths
            if not any(i in root for i in ignore_list):
                depth = get_path_depth(root_dir, root)
                display = format_display(root, False, depth)
                print(f"{{display}}\\t{{root}}")
                printed_paths.add(root)
                
        if is_collapsed:
            dirs[:] = []  # Don't walk into subdirectories
            continue     # Skip processing files in this directory
        
        # Process files in this directory
        for file in files:
            full_path = os.path.join(root, file)
            if full_path in printed_paths:
                continue
            if any(i in full_path for i in ignore_list):
                continue
            depth = get_path_depth(root_dir, full_path)
            display = format_display(full_path, False, depth)
            print(f"{{display}}\\t{{full_path}}")
            printed_paths.add(full_path)
'''
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.py') as feeder_script:
            feeder_script.write(feeder_script_content)
            feeder_script_file = feeder_script.name
        
        # Create bookmark reorder script for Alt+Up/Down
        bookmark_reorder_script_content = f'''
import sys
import json
import os

bookmarks_file = r"{bookmarks_file}"

def move_bookmark(file_path, direction):
    if not os.path.exists(bookmarks_file):
        return
    try:
        with open(bookmarks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            bookmarks = [b if isinstance(b, dict) else {{"path": b, "name": ""}} for b in data]
    except:
        return
    
    idx = next((i for i, b in enumerate(bookmarks) if b['path'] == file_path), -1)
    if idx == -1: return
    
    new_idx = idx + direction
    if 0 <= new_idx < len(bookmarks):
        bookmarks[idx], bookmarks[new_idx] = bookmarks[new_idx], bookmarks[idx]
        with open(bookmarks_file, 'w', encoding='utf-8') as f:
            json.dump(bookmarks, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        direction = -1 if sys.argv[1] == "up" else 1
        file_path = sys.argv[2]
        move_bookmark(file_path, direction)
'''
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.py') as reorder_script:
            reorder_script.write(bookmark_reorder_script_content)
            bookmark_reorder_script_file = reorder_script.name
        
        # Shortcut help header (toggled by ?)
        help_header = r"""┌───────────────────────────────────────────────────────────────────────────┐
│                            SHORTCUTS MENU                                 │
├───────────────────────────────────────────────────────────────────────────┤
│  [ FUNCTION KEYS ]                                                        │
│  F2        : Toggle image preview mode (chafa/viu vs QuickLook)           │
│  F3        : Toggle view mode (Full Path vs Filename)                     │
│  F4        : Refresh file list                                            │
│  F5        : Toggle bookmark on/off (Prompts for custom name)             │
│  F6        : Rename bookmark custom name                                  │
│  F7        : Configuration                                                │
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
            f"--bind=f5:execute(python \"{script_path}\" --toggle-bookmark {{2}})+reload(python \"{feeder_script_file}\")",
            f"--bind=f6:execute(python \"{script_path}\" --rename-bookmark {{2}})+reload(python \"{feeder_script_file}\")",
            f"--bind=f7:execute(python \"{os.path.join(script_dir, 'configurator_gui.py')}\")+reload(python \"{feeder_script_file}\")",
            f"--bind=ctrl-h:execute(python \"{os.path.join(script_dir, 'configurator_gui.py')}\" --help)+reload(python \"{feeder_script_file}\")",
            "--bind=ctrl-p:toggle-preview",
            "--bind=?:toggle-header",
            "--bind=start:toggle-header",
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

