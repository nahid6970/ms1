import os
import subprocess
import tempfile
import sys

def show_action_menu(file_paths):
    """Show action menu and execute selected action for multiple files"""
    if isinstance(file_paths, str):
        file_paths = [file_paths]
    
    files_display = "\n".join([f"  • {os.path.basename(fp)}" for fp in file_paths])
    menu_text = f"""Select action for {len(file_paths)} file(s):
{files_display}

1. Open with VSCode
2. Open folder location(s)
3. Run file(s)

Enter choice (1-3): """
    
    # Create temp file with menu
    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.txt') as temp_file:
        temp_file.write(menu_text)
        menu_file = temp_file.name
    
    try:
        # Show menu in a new command prompt window and get user choice
        cmd = f'cmd /c "type "{menu_file}" && set /p choice=Enter choice: && echo !choice! > "{menu_file}.choice""'
        subprocess.run(cmd, shell=True)
        
        # Read the choice
        choice_file = f"{menu_file}.choice"
        if os.path.exists(choice_file):
            with open(choice_file, 'r') as f:
                choice = f.read().strip()
            
            # Execute based on choice
            if choice == '1':
                # Open all files in VSCode
                for file_path in file_paths:
                    subprocess.run(['cmd', '/c', 'code', file_path])
            elif choice == '2':
                # Open all folder locations
                for file_path in file_paths:
                    subprocess.run(['explorer.exe', '/select,', file_path])
            elif choice == '3':
                # Run all files
                for file_path in file_paths:
                    subprocess.run(['powershell', '-command', f'Start-Process "{file_path}"'])
            
            # Clean up choice file
            os.remove(choice_file)
    
    except Exception as e:
        print(f"Error in menu: {e}", file=sys.stderr)
    finally:
        # Clean up menu file
        if os.path.exists(menu_file):
            os.remove(menu_file)

def search_directories_and_files():
    # Start with an empty list
    directories = []

    # Add directories (comment any line freely without breaking syntax)
    directories.append(r"C:\Users\nahid\ms\ms1")
    directories.append(r"C:\Users\nahid\ms\msBackups")
    directories.append(r"C:\Users\nahid\Pictures")
    # directories.append("D:\\")
    # directories.append("C:\\Program Files\\WindowsApps")
    # directories.append("C:\\Users\\nahid")

    # Filter out empty or None directories
    directories = [d for d in directories if d and d.strip()]

    # Ignore list
    ignore_list = [".git", ".pyc"]

    # Shortcut list text for F1 display
    shortcuts_text = r"""
Shortcuts available:
  Enter   : Show action menu (VSCode/Folder/Run) - works with multi-select
  Ctrl-o  : Open file location in Explorer - works with multi-select
  Ctrl-c  : Copy full file path to clipboard - works with multi-select
  Ctrl-r  : Run file with PowerShell Start-Process - works with multi-select
  F1      : Show this shortcuts help window
  
Multi-select: Use Tab to select multiple files, then use any action
"""

    # Create a temp file with shortcuts text
    temp_shortcut_file = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(shortcuts_text)
            temp_shortcut_file = temp_file.name

        # Create temp script for action menu that handles multiple files
        menu_script = f"""
import sys
import subprocess
import os

def show_action_menu(file_paths_str):
    # Split the file paths (they come as space-separated)
    file_paths = file_paths_str.strip().split()
    if not file_paths:
        return
        
    files_display = "\\n".join([f"  • {{os.path.basename(fp)}}" for fp in file_paths])
    
    menu_options = [
        f"1. Open with VSCode\\t{{len(file_paths)}} file(s)",
        f"2. Open folder location(s)\\t{{len(file_paths)}} file(s)", 
        f"3. Run file(s)\\t{{len(file_paths)}} file(s)"
    ]
    
    try:
        fzf_menu_args = [
            "fzf",
            "--prompt=Select action: ",
            f"--header=Choose action for {{len(file_paths)}} selected file(s):\\n{{files_display}}",
            "--with-nth=1",
            "--delimiter=\\t",
            "--border",
            "--layout=reverse",
            "--height=15",
            "--color=bg:-1,bg+:-1,fg:#ebdbb2,fg+:#ebdbb2,hl:#fe8019,hl+:#fe8019,info:#83a598,prompt:#b8bb26,pointer:#d3869b,marker:#b8bb26,spinner:#fe8019,header:#83a598,preview-bg:-1,border:#665c54"
        ]
        
        process = subprocess.Popen(fzf_menu_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding='utf-8')
        menu_input = '\\n'.join(menu_options)
        stdout, _ = process.communicate(input=menu_input)
        
        if stdout and process.returncode == 0:
            selection = stdout.strip()
            if selection.startswith('1.'):
                # Open all files in VSCode
                for file_path in file_paths:
                    subprocess.run(['cmd', '/c', 'code', file_path])
            elif selection.startswith('2.'):
                # Open all folder locations
                for file_path in file_paths:
                    subprocess.run(['explorer.exe', '/select,', file_path])
            elif selection.startswith('3.'):
                # Run all files
                for file_path in file_paths:
                    subprocess.run(['powershell', '-command', f'Start-Process "{{file_path}}"'])
    
    except Exception as e:
        print(f"Error in menu: {{e}}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Join all arguments as they represent multiple file paths
        file_paths_str = ' '.join(sys.argv[1:])
        show_action_menu(file_paths_str)
"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.py') as menu_temp:
            menu_temp.write(menu_script)
            menu_script_file = menu_temp.name

        # Prepare fzf arguments with fixed bindings for multi-select
        fzf_args = [
            "fzf",
            "--multi",
            "--with-nth=1",
            "--delimiter=\t",
            "--preview=bat --style=plain --color=always --line-range :100 {1}",
            "--preview-window=~3",
            "--border",
            "--layout=reverse",
            "--color=bg:-1,bg+:-1,fg:#ebdbb2,fg+:#ebdbb2,hl:#fe8019,hl+:#fe8019,info:#83a598,prompt:#b8bb26,pointer:#d3869b,marker:#b8bb26,spinner:#fe8019,header:#83a598,preview-bg:-1,border:#665c54",
            # Fixed: Use {+1} for multi-select instead of {1}
            f"--bind=enter:execute(python \"{menu_script_file}\" {{+1}})",
            "--bind=ctrl-o:execute-silent(for %i in ({+1}) do explorer.exe /select,\"%i\")",
            "--bind=ctrl-c:execute-silent(for %i in ({+1}) do echo %i >> %temp%\\clipboard.txt && type %temp%\\clipboard.txt | clip && del %temp%\\clipboard.txt)",
            "--bind=ctrl-r:execute-silent(for %i in ({+1}) do powershell -command Start-Process '%i')",
            f"--bind=f1:execute-silent(cmd /c start cmd /k type \"{temp_shortcut_file}\" & pause)",
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

        # Clean up menu script
        if os.path.exists(menu_script_file):
            os.remove(menu_script_file)

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