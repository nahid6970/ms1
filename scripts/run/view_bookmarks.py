import json
import os
import subprocess
import tempfile
import sys

def remove_bookmark(file_path, bookmarks_file):
    """Remove a file path from bookmarks.json"""
    if not os.path.exists(bookmarks_file):
        return
    
    try:
        with open(bookmarks_file, 'r', encoding='utf-8') as f:
            bookmarks = json.load(f)
    except json.JSONDecodeError:
        return
    
    if file_path in bookmarks:
        bookmarks.remove(file_path)
        with open(bookmarks_file, 'w', encoding='utf-8') as f:
            json.dump(bookmarks, f, indent=2, ensure_ascii=False)

def reload_bookmarks(bookmarks_file):
    """Output current bookmarks for fzf reload"""
    if not os.path.exists(bookmarks_file):
        return ""
    
    try:
        with open(bookmarks_file, 'r', encoding='utf-8') as f:
            bookmarks = json.load(f)
        valid_bookmarks = [b for b in bookmarks if os.path.exists(b)]
        return "\n".join(valid_bookmarks)
    except:
        return ""

def view_bookmarks():
    """Display bookmarks in fzf and allow actions on selected bookmark"""
    bookmarks_file = r"C:\Users\nahid\script_output\bookmarks.json"
    
    while True:  # Loop to keep showing bookmarks after opening files
        # Load bookmarks
        if not os.path.exists(bookmarks_file):
            print("No bookmarks found. Press F5 to add bookmarks!")
            return
        
        try:
            with open(bookmarks_file, 'r', encoding='utf-8') as f:
                bookmarks = json.load(f)
        except json.JSONDecodeError:
            print("Error reading bookmarks file")
            return
        
        if not bookmarks:
            print("No bookmarks found. Press F5 to add bookmarks!")
            return
        
        # Filter out non-existent files
        valid_bookmarks = [b for b in bookmarks if os.path.exists(b)]
        
        # Update bookmarks file if some were invalid
        if len(valid_bookmarks) != len(bookmarks):
            with open(bookmarks_file, 'w', encoding='utf-8') as f:
                json.dump(valid_bookmarks, f, indent=2, ensure_ascii=False)
        
        if not valid_bookmarks:
            print("All bookmarks point to non-existent files")
            return
        
        # Create preview script
        preview_script_content = '''
param($FilePath)

if (-not (Test-Path $FilePath)) {
    Write-Host "File not found: $FilePath" -ForegroundColor Red
    exit 1
}

$ext = [System.IO.Path]::GetExtension($FilePath).ToLower()
$imageExtensions = @('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.ico')

if ($imageExtensions -contains $ext) {
    try {
        $chafaPath = Get-Command chafa -ErrorAction Stop
        & chafa --size=40x20 --symbols=block --fill=space --stretch $FilePath
        Write-Host ""
        $fileInfo = Get-Item $FilePath
        Write-Host "File: $(Split-Path $FilePath -Leaf)" -ForegroundColor Cyan
        Write-Host "Size: $([math]::Round($fileInfo.Length / 1KB, 2)) KB" -ForegroundColor Gray
        exit 0
    }
    catch {
        try {
            $viuPath = Get-Command viu -ErrorAction Stop
            & viu -w 40 -h 20 $FilePath
            Write-Host ""
            exit 0
        }
        catch {
            Write-Host "[IMAGE FILE]" -ForegroundColor Cyan
            $fileInfo = Get-Item $FilePath
            Write-Host "Size: $([math]::Round($fileInfo.Length / 1KB, 2)) KB"
            exit 0
        }
    }
}

try {
    $batPath = Get-Command bat -ErrorAction Stop
    & bat --style=plain --color=always --line-range :100 $FilePath
}
catch {
    try {
        Get-Content $FilePath -Head 100 -ErrorAction Stop
    }
    catch {
        Write-Host "[BINARY FILE]" -ForegroundColor Yellow
        $fileInfo = Get-Item $FilePath
        Write-Host "Size: $([math]::Round($fileInfo.Length / 1KB, 2)) KB"
    }
}
'''
    
        preview_script_file = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.ps1') as preview_script:
                preview_script.write(preview_script_content)
                preview_script_file = preview_script.name
            
            # Prepare fzf input
            fzf_input = "\n".join(valid_bookmarks)
            
            # Run fzf
            fzf_args = [
                "fzf",
                "--prompt=Bookmarks: ",
                "--header=Enter: Open | Ctrl-O: Explorer | Ctrl-C: Copy | Ctrl-P: Toggle Preview | Del: Remove | ESC: Exit",
                f"--preview=powershell -ExecutionPolicy Bypass -File \"{preview_script_file}\" {{}}",
                "--preview-window=right:60%:border-left",
                "--preview-window=hidden",  # Start with preview hidden
                "--border",
                "--layout=reverse",
                "--color=bg:-1,bg+:#1e1e1e,fg:#d1ff94,fg+:#8fdbff,hl:#fe8019,hl+:#fe8019,info:#83a598,prompt:#b8bb26,pointer:#d3869b,marker:#ff4747,spinner:#fe8019,header:#83a598,preview-bg:-1,border:#d782ff",
                "--bind=ctrl-o:execute-silent(explorer.exe /select,{})",
                "--bind=ctrl-c:execute-silent(echo {} | clip)",
                "--bind=ctrl-p:toggle-preview",
                f"--bind=del:execute-silent(python \"{os.path.abspath(__file__)}\" --remove {{}})+reload(python \"{os.path.abspath(__file__)}\" --reload)"
            ]
            
            process = subprocess.Popen(fzf_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding='utf-8')
            stdout, _ = process.communicate(input=fzf_input)
            
            # If user pressed ESC or cancelled, exit the loop
            if not stdout or process.returncode != 0:
                return
            
            # Open selected bookmark with editor chooser
            selected_file = stdout.strip()
            if selected_file:
                # Get script directory
                script_dir = os.path.dirname(os.path.abspath(__file__))
                editor_chooser = os.path.join(script_dir, "editor_chooser.py")
                subprocess.run(f'python "{editor_chooser}" "{selected_file}"', shell=True)
                # Loop continues, showing bookmarks again
            
        finally:
            if preview_script_file and os.path.exists(preview_script_file):
                try:
                    os.remove(preview_script_file)
                except:
                    pass

if __name__ == "__main__":
    bookmarks_file = r"C:\Users\nahid\script_output\bookmarks.json"
    
    # Handle command line arguments for remove/reload
    if len(sys.argv) > 1:
        if sys.argv[1] == "--remove" and len(sys.argv) > 2:
            remove_bookmark(sys.argv[2], bookmarks_file)
        elif sys.argv[1] == "--reload":
            print(reload_bookmarks(bookmarks_file))
    else:
        view_bookmarks()
