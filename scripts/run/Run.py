import os
import subprocess
import tempfile
import sys

def search_directories_and_files():
    # Start with an empty list
    directories = []

    # Add directories (comment any line freely without breaking syntax)
    directories.append(r"C:\Users\nahid\ms\ms1")
    directories.append(r"C:\Users\nahid\ms\msBackups")
    directories.append(r"C:\Users\nahid\Pictures")
    directories.append("D:\\")
    # directories.append("C:\\Program Files\\WindowsApps")
    # directories.append("C:\\Users\\nahid")

    # Filter out empty or None directories
    directories = [d for d in directories if d and d.strip()]

    # Ignore list
    ignore_list = [".git", ".pyc"]

    # Shortcut list text for F1 display
    shortcuts_text = r"""
Shortcuts available:
  Enter   : Show action menu (Editor/VSCode/Folder/Run/Copy/Terminal) - works with multi-select
  Ctrl-n  : Open file with editor chooser - works with multi-select
  Ctrl-o  : Open file location in Explorer - works with multi-select  
  Ctrl-c  : Copy full file path to clipboard - works with multi-select
  Ctrl-r  : Run file with PowerShell Start-Process - works with multi-select
  Ctrl-p  : Toggle preview window on/off
  F1      : Show this shortcuts help window
  F2      : Toggle between chafa/viu and QuickLook for image preview
  F4      : View bookmarks (open saved bookmarks list)
  F5      : Add current file to bookmarks
  
Multi-select: Use Tab to select multiple files, then use any action
Supports files with spaces in their names!
"""

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

        # Get absolute paths for bookmark scripts
        script_dir = os.path.dirname(os.path.abspath(__file__))
        add_bookmark_script = os.path.join(script_dir, "add_bookmark.py")
        view_bookmarks_script = os.path.join(script_dir, "view_bookmarks.py")
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


        
        # Prepare fzf arguments with PowerShell preview for images and F2 toggle
        fzf_args = [
            "fzf",
            "--multi",
            "--with-nth=1",
            "--delimiter=\t",
            f"--preview=powershell -ExecutionPolicy Bypass -File \"{preview_script_file}\" {{1}}",
            "--preview-window=~3",
            "--preview-window=hidden",   # Start with preview hidden
            "--border",
            "--layout=reverse", 
            "--color=bg:#1e1e1e,fg:#d0d0d0,bg+:#2e2e2e,fg+:#ffffff,hl:#00d9ff,hl+:#00ff00,info:#afaf87,prompt:#d782ff,pointer:#d782ff,marker:#19d600,header:#888888,border:#d782ff",
            f"--bind=enter:execute({batch_file} {{+1}})",
            f"--bind=ctrl-n:execute-silent(python \"{editor_chooser_script}\" {{+1}})",
            "--bind=ctrl-o:execute-silent(explorer.exe /select,{1})",
            "--bind=ctrl-c:execute-silent(echo {1} | clip)",
            "--bind=ctrl-r:execute-silent(powershell -command Start-Process '{1}')",
            f"--bind=f1:execute-silent(cmd /c start cmd /k type {temp_shortcut_file} & pause)",
            f"--bind=f2:execute-silent(powershell -ExecutionPolicy Bypass -File \"{toggle_script_file}\")+refresh-preview",
            f"--bind=f4:execute-silent(start cmd /c python \"{view_bookmarks_script}\")",
            f"--bind=f5:execute-silent(python \"{add_bookmark_script}\" {{1}})",
            "--bind=ctrl-p:toggle-preview",
        ]

        # Start fzf process
        process = subprocess.Popen(fzf_args, stdin=subprocess.PIPE, text=True, encoding='utf-8')

        # Traverse directories and send file paths to fzf's stdin
        for root_dir in directories:
            if not os.path.isdir(root_dir):
                continue

            for root, _, files in os.walk(root_dir, onerror=lambda e: None):
                for file in files:
                    full_path = os.path.join(root, file)

                    # Check against ignore list
                    if any(ignore_item in full_path for ignore_item in ignore_list):
                        continue

                    directory_name = os.path.dirname(full_path)
                    try:
                        process.stdin.write(f"{full_path}\t{directory_name}\n")
                    except BrokenPipeError:
                        break
                else:
                    continue
                break
        
        # Close stdin to signal end of input to fzf
        process.stdin.close()
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

if __name__ == "__main__":
    search_directories_and_files()
