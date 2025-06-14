import os
import subprocess
import tempfile
import sys

def search_directories_and_files():
    # Start with an empty list
    directories = []

    # Add directories (comment any line freely without breaking syntax)
    directories.append("C:\\ms1")
    directories.append("C:\\ms2")
    directories.append("C:\\ms3")
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
  Enter   : Open selected file in VSCode
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
            "--bind=enter:execute-silent(code {+1})",
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