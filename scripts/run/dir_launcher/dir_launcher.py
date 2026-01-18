import sys
import os
import json
import subprocess

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dir_launcher.json")

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"directories": [], "commands": [], "settings": {"view_mode": "full"}}
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
        if "settings" not in data:
            data["settings"] = {"view_mode": "full"}
        return data

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def run_fzf(items, prompt="Select > ", help_text="", extra_args=None):
    """
    Runs fzf with the given items.
    Returns (key, selection).
    key is 'ctrl-a', 'ctrl-d', 'tab' or '' (for enter).
    Returns (None, None) if cancelled.
    """
    # Use header as help text in a hidden preview window
    # Escape pipe characters for Windows cmd echo
    safe_header = help_text.replace("|", "^|")

    fzf_cmd = [
        "fzf", 
        "--layout=reverse", 
        f"--prompt={prompt} [?] ", 
        f"--preview=echo {safe_header}",
        "--preview-window=up:1:hidden:wrap",
        "--bind=?:toggle-preview",
        "--expect=ctrl-a,ctrl-d,tab,alt-up,alt-down",
        "--color=bg:#1e1e1e,fg:#d0d0d0,bg+:#2e2e2e,fg+:#ffffff,hl:#00d9ff,hl+:#00ff00",
        "--color=info:#afaf87,prompt:#d782ff,pointer:#d782ff,marker:#19d600,header:#888888",
        "--border",
        "--margin=1",
        "--padding=1"
    ]
    
    if extra_args:
        fzf_cmd.extend(extra_args)
    
    try:
        process = subprocess.Popen(
            fzf_cmd, 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=None, 
            text=True
        )
        stdout, _ = process.communicate(input="\n".join(items))
    except FileNotFoundError:
        print("Error: fzf not found in PATH.")
        sys.exit(1)
    
    # fzf returns 0 on match, 1 on no match, 130 on abort
    if process.returncode == 130:
        return None, None
    
    lines = stdout.splitlines()
    if not lines:
        return None, None
        
    key = lines[0]
    selection = lines[1] if len(lines) > 1 else ""
    return key, selection

def move_item(items, item, direction):
    """Moves item up (-1) or down (1) in the list."""
    try:
        idx = items.index(item)
    except ValueError:
        return False
    
    new_idx = idx + direction
    if 0 <= new_idx < len(items):
        items[idx], items[new_idx] = items[new_idx], items[idx]
        return True
    return False

def main():
    while True:
        data = load_data()
        dirs = data.get("directories", [])
        settings = data.get("settings", {"view_mode": "full"})
        view_mode = settings.get("view_mode", "full")
        
        # Prepare content based on view mode
        fzf_items = []
        fzf_args = []
        
        if view_mode == "name":
            # Show "Folder\tFullPath", tell fzf to display only 1st column
            for d in dirs:
                name = os.path.basename(d.rstrip(os.sep).rstrip('/'))
                if not name: name = d # Fallback for root
                fzf_items.append(f"{name}\t{d}")
            fzf_args = ["--delimiter=\t", "--with-nth=1"]
        else:
            # Full path mode
            fzf_items = dirs
            fzf_args = []
            
        key, selection = run_fzf(
            fzf_items, 
            prompt=f"Dir ({view_mode}) > ", 
            help_text="Ctrl-A: Add | Ctrl-D: Del | Tab: View | Alt-Up/Down: Move | Enter: Select",
            extra_args=fzf_args
        )
        
        if key is None:
            # Esc pressed
            break
            
        # Parse selection if in Name mode to get full path
        selected_dir = ""
        if selection:
            if view_mode == "name" and '\t' in selection:
                selected_dir = selection.split('\t')[1]
            else:
                selected_dir = selection

        if key == 'tab':
            # Toggle view mode
            new_mode = "full" if view_mode == "name" else "name"
            settings["view_mode"] = new_mode
            data["settings"] = settings
            save_data(data)
            continue 

        elif key == 'alt-up':
            if selected_dir and move_item(dirs, selected_dir, -1):
                data["directories"] = dirs
                save_data(data)
                
        elif key == 'alt-down':
            if selected_dir and move_item(dirs, selected_dir, 1):
                data["directories"] = dirs
                save_data(data)

        elif key == '':
            if selected_dir:
                handle_directory(selected_dir, data)
        elif key == 'ctrl-a':
            print("\n--- Add New Directory ---")
            new_dir = input("Enter path: ").strip().strip('"').strip("'")
            if new_dir:
                if os.path.isdir(new_dir):
                    if new_dir not in dirs:
                        dirs.append(new_dir)
                        data["directories"] = dirs
                        save_data(data)
                else:
                    input(f"Error: '{new_dir}' is not a valid directory. Press Enter to continue...")
        elif key == 'ctrl-d':
            if selected_dir and selected_dir in dirs:
                # confirm? nah, easy enough to re-add
                dirs.remove(selected_dir)
                data["directories"] = dirs
                save_data(data)

def handle_directory(directory, data):
    while True:
        commands = data.get("commands", [])
        # Use a display string "Name" but map back to full object
        # Or just show names in fzf
        cmd_names = [c["name"] for c in commands]
        
        key, selected_cmd_name = run_fzf(
            cmd_names, 
            prompt=f"[{directory}] Action > ", 
            help_text="Ctrl-A: Add | Ctrl-D: Del | Alt-Up/Down: Move | Enter: Run | Esc: Back"
        )
        
        if key is None:
            return # Back to dir selection

        cmd_obj = None
        if selected_cmd_name:
            cmd_obj = next((c for c in commands if c["name"] == selected_cmd_name), None)

        if key == '':
            if cmd_obj:
                execute_command(cmd_obj["template"], directory)
                sys.exit(0) # Done
        
        elif key == 'alt-up':
            if cmd_obj and move_item(commands, cmd_obj, -1):
                data["commands"] = commands
                save_data(data)

        elif key == 'alt-down':
            if cmd_obj and move_item(commands, cmd_obj, 1):
                data["commands"] = commands
                save_data(data)

        elif key == 'ctrl-a':
            print("\n--- Add New Command ---")
            name = input("Command Name: ").strip()
            if name:
                template = input("Command Template (use {path} as placeholder): ").strip()
                if template:
                    commands.append({"name": name, "template": template})
                    data["commands"] = commands
                    save_data(data)
        elif key == 'ctrl-d':
            if selected_cmd_name:
                data["commands"] = [c for c in commands if c["name"] != selected_cmd_name]
                save_data(data)

def execute_command(template, path):
    final_cmd = template.replace("{path}", path)
    print(f"\nExecuting: {final_cmd}")
    subprocess.run(final_cmd, shell=True)

if __name__ == "__main__":
    main()
