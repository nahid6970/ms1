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
  Enter   : Show action menu (VSCode/Folder/Run/Copy/Terminal) - works with multi-select
  Ctrl-o  : Open file location in Explorer - works with multi-select  
  Ctrl-c  : Copy full file path to clipboard - works with multi-select
  Ctrl-r  : Run file with PowerShell Start-Process - works with multi-select
  F1      : Show this shortcuts help window
  
Multi-select: Use Tab to select multiple files, then use any action
Supports files with spaces in their names!
"""

    # Create PowerShell preview script with image support
    preview_script_content = '''
param($FilePath)

if (-not (Test-Path $FilePath)) {
    Write-Host "File not found: $FilePath" -ForegroundColor Red
    exit 1
}

$ext = [System.IO.Path]::GetExtension($FilePath).ToLower()
$imageExtensions = @('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.ico')

if ($imageExtensions -contains $ext) {
    # Try chafa for image preview with better sizing
    try {
        $chafaPath = Get-Command chafa -ErrorAction Stop
        # Use smaller dimensions that fit better in preview pane
        & chafa --size=40x20 --symbols=block --fill=space --stretch $FilePath
        Write-Host ""
        # Show file info below image
        $fileInfo = Get-Item $FilePath
        Write-Host "File: $(Split-Path $FilePath -Leaf)" -ForegroundColor Cyan
        Write-Host "Size: $([math]::Round($fileInfo.Length / 1KB, 2)) KB" -ForegroundColor Gray
        Write-Host "Modified: $($fileInfo.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))" -ForegroundColor Gray
        exit 0
    }
    catch {
        # Try viu with smaller dimensions
        try {
            $viuPath = Get-Command viu -ErrorAction Stop
            & viu -w 40 -h 20 $FilePath
            Write-Host ""
            $fileInfo = Get-Item $FilePath
            Write-Host "File: $(Split-Path $FilePath -Leaf)" -ForegroundColor Cyan
            Write-Host "Size: $([math]::Round($fileInfo.Length / 1KB, 2)) KB" -ForegroundColor Gray
            exit 0
        }
        catch {
            # Fallback: show image info
            Write-Host ""
            Write-Host "[IMAGE FILE]" -ForegroundColor Cyan
            Write-Host "File: $(Split-Path $FilePath -Leaf)"
            Write-Host "Extension: $ext"
            $fileInfo = Get-Item $FilePath
            Write-Host "Size: $([math]::Round($fileInfo.Length / 1KB, 2)) KB"
            Write-Host "Dimensions: $(try { Add-Type -AssemblyName System.Drawing; $img = [System.Drawing.Image]::FromFile($FilePath); "$($img.Width)x$($img.Height)"; $img.Dispose() } catch { "Unknown" })"
            Write-Host "Modified: $($fileInfo.LastWriteTime)"
            Write-Host ""
            Write-Host "(Install chafa for image preview: scoop install chafa)" -ForegroundColor Yellow
            exit 0
        }
    }
}

# For non-image files, try bat first
try {
    $batPath = Get-Command bat -ErrorAction Stop
    & bat --style=plain --color=always --line-range :100 $FilePath
}
catch {
    # Fallback to Get-Content for text files
    try {
        Write-Host "[TEXT FILE PREVIEW]" -ForegroundColor Green
        Get-Content $FilePath -Head 100 -ErrorAction Stop
    }
    catch {
        Write-Host "[BINARY FILE - Cannot preview]" -ForegroundColor Yellow
        Write-Host "File: $(Split-Path $FilePath -Leaf)"
        $fileInfo = Get-Item $FilePath
        Write-Host "Size: $([math]::Round($fileInfo.Length / 1KB, 2)) KB"
        Write-Host "Modified: $($fileInfo.LastWriteTime)"
    }
}
'''

    # Create temp files
    temp_shortcut_file = None
    preview_script_file = None
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(shortcuts_text)
            temp_shortcut_file = temp_file.name

        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.ps1') as preview_script:
            preview_script.write(preview_script_content)
            preview_script_file = preview_script.name

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
    
    # ---------- coloured, padded menu lines --------------------------
    pad = "  "
    menu_options = [
        f"{pad}\x1b[1;31m  Run\x1b[0m\t{len(file_paths)}",
        f"{pad}\x1b[1;34m  VSCode\x1b[0m\t{len(file_paths)}",
        f"{pad}\x1b[1;33m  folder\x1b[0m\t{len(file_paths)}",
        f"{pad}\x1b[38;5;181m  Terminal\x1b[0m\t{len(file_paths)}",  # #E0AFA0
        f"{pad}\x1b[1;32m 󰴠 Copy path\x1b[0m\t{len(file_paths)}",
        f"{pad}\x1b[1;91m 󰆴 Delete\x1b[0m\t{len(file_paths)}",
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
            "--color=bg:-1,bg+:-1,fg:#ebdbb2,fg+:#ebdbb2,hl:#fe8019,hl+:#fe8019,info:#83a598,prompt:#b8bb26,pointer:#d3869b,marker:#b8bb26,spinner:#fe8019,header:#83a598,preview-bg:-1,border:#665c54"
        ]
        
        process = subprocess.Popen(fzf_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding='utf-8')
        menu_input = '\\n'.join(menu_options)
        stdout, _ = process.communicate(input=menu_input)
        
        if stdout and process.returncode == 0:
            selection = stdout.strip()
            #! Open all files in VSCode
            if selection.startswith(''):
                for file_path in file_paths:
                    subprocess.run(f'code "{os.path.abspath(file_path)}"', shell=True)
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
python "{menu_script_path}" "!temp_file!"
'''

        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.bat') as batch_temp:
            batch_temp.write(batch_content)
            batch_file = batch_temp.name

        # Prepare fzf arguments with PowerShell preview for images
        fzf_args = [
            "fzf",
            "--multi",
            "--with-nth=1",
            "--delimiter=\t",
            f"--preview=powershell -ExecutionPolicy Bypass -File \"{preview_script_file}\" {{1}}",
            "--preview-window=~3",
            "--preview-window=hidden",   # was "~3"
            "--border",
            "--layout=reverse", 
            "--color=bg:-1,bg+:-1,fg:#d1ff94,fg+:#8fdbff,hl:#fe8019,hl+:#fe8019,info:#83a598,prompt:#b8bb26,pointer:#d3869b,marker:#ff4747,spinner:#fe8019,header:#83a598,preview-bg:-1,border:#d782ff",
            f"--bind=enter:execute({batch_file} {{+1}})",
            "--bind=ctrl-o:execute-silent(explorer.exe /select,{1})",
            "--bind=ctrl-c:execute-silent(echo {1} | clip)",
            "--bind=ctrl-r:execute-silent(powershell -command Start-Process '{1}')",
            f"--bind=f1:execute-silent(cmd /c start cmd /k type {temp_shortcut_file} & pause)",
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
        for temp_file in [batch_file, menu_script_path, preview_script_file]:
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
        # Clean up the temporary file
        if temp_shortcut_file and os.path.exists(temp_shortcut_file):
            os.remove(temp_shortcut_file)

if __name__ == "__main__":
    search_directories_and_files()