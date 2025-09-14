import os
import subprocess
import tempfile
import sys

def show_action_menu(file_path):
    """Show action menu and execute selected action"""
    menu_text = f"""Select action for: {os.path.basename(file_path)}

1. Open with VSCode
2. Open folder location
3. Run file

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
                subprocess.run(['code', file_path])
            elif choice == '2':
                subprocess.run(['explorer.exe', '/select,', file_path])
            elif choice == '3':
                subprocess.run(['powershell', '-command', f'Start-Process "{file_path}"'])
            # Choice 4 or anything else: do nothing (cancel)
            
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
  Enter   : Show action menu (VSCode/Folder/Run)
  Ctrl-o  : Open file location in Explorer
  Ctrl-c  : Copy full file path to clipboard
  Ctrl-r  : Run file with PowerShell Start-Process
  F1      : Show this shortcuts help window
"""

    # Create a temp file with shortcuts text
    temp_shortcut_file = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(shortcuts_text)
            temp_shortcut_file = temp_file.name

        # Create temp script for action menu
        current_script = os.path.abspath(__file__)
        menu_script = f"""
import sys
import subprocess
import os

def show_action_menu(file_path):
    menu_options = [
        f"1. Open with VSCode\t{{file_path}}",
        f"2. Open folder location\t{{file_path}}", 
        f"3. Run file\t{{file_path}}"
    ]
    
    try:
        fzf_menu_args = [
            "fzf",
            "--prompt=Select action: ",
            "--header=Choose what to do with the selected file",
            "--with-nth=1",
            "--delimiter=\\t",
            "--border",
            "--layout=reverse",
            "--height=10",
            "--color=bg:#1e1e2e,bg+:#313244,fg:#cdd6f4,fg+:#f5e0dc,hl:#f38ba8,hl+:#f9e2af,info:#89b4fa,prompt:#a6e3a1,pointer:#f38ba8,marker:#f9e2af,spinner:#94e2d5,header:#89b4fa,preview-bg:#1e1e2e,border:#74c7ec"
        ]
        
        process = subprocess.Popen(fzf_menu_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding='utf-8')
        menu_input = '\\n'.join(menu_options)
        stdout, _ = process.communicate(input=menu_input)
        
        if stdout and process.returncode == 0:
            selection = stdout.strip()
            if selection.startswith('1.'):
                subprocess.run(['code', file_path])
            elif selection.startswith('2.'):
                subprocess.run(['explorer.exe', '/select,', file_path])
            elif selection.startswith('3.'):
                subprocess.run(['powershell', '-command', f'Start-Process "{{file_path}}"'])
    
    except Exception as e:
        print(f"Error in menu: {{e}}")

if __name__ == "__main__":
    show_action_menu(sys.argv[1])
"""
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.py') as menu_temp:
            menu_temp.write(menu_script)
            menu_script_file = menu_temp.name

        # Prepare fzf arguments
        fzf_args = [
            "fzf",
            "--multi",
            "--with-nth=1",
            "--delimiter=\t",
            "--preview=bat --style=plain --color=always --line-range :100 {1}",
            "--preview-window=~3",
            "--border",
            "--layout=reverse",
            "--color=bg:#1e1e2e,bg+:#313244,fg:#cdd6f4,fg+:#f5e0dc,hl:#f38ba8,hl+:#f9e2af,info:#89b4fa,prompt:#a6e3a1,pointer:#f38ba8,marker:#f9e2af,spinner:#94e2d5,header:#89b4fa,preview-bg:#1e1e2e,border:#74c7ec",
            f"--bind=enter:execute(python \"{menu_script_file}\" {{+1}})",
            "--bind=ctrl-o:execute-silent(explorer.exe /select,{+1})",
            "--bind=ctrl-c:execute-silent(cmd /c echo {+1} | clip)",
            "--bind=ctrl-r:execute-silent(powershell -command Start-Process '{+1}')",
            f"--bind=f1:execute-silent(cmd /c start cmd /k type \"{temp_shortcut_file}\" & pause)",
        ]

        # Start fzf process
        # We use Popen with PIPE for stdin to feed file paths
        # and inherit stdout/stderr so fzf's TUI is displayed
        process = subprocess.Popen(fzf_args, stdin=subprocess.PIPE, text=True, encoding='utf-8')

        # Traverse directories and send file paths to fzf's stdin
        for root_dir in directories:
            if not os.path.isdir(root_dir):
                # print(f"Warning: Directory not found - {root_dir}", file=sys.stderr)
                continue

            for root, _, files in os.walk(root_dir, onerror=lambda e: None): # onerror to ignore permission errors
                for file in files:
                    full_path = os.path.join(root, file)

                    # Check against ignore list
                    if any(ignore_item in full_path for ignore_item in ignore_list):
                        continue

                    directory_name = os.path.dirname(full_path)
                    try:
                        process.stdin.write(f"{full_path}\t{directory_name}\n")
                    except BrokenPipeError:
                        # fzf might have quit early
                        break
                else: # This else block runs if the inner loop completes without a break
                    continue
                break # This break runs if the inner loop broke (fzf quit)
        
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