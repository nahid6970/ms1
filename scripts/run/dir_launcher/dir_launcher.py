import sys
import os
import json
import subprocess

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dir_launcher.json")

# ANSI Colors
C_RESET = "\033[0m"
C_CYAN = "\033[36m"
C_GREEN = "\033[32m"
C_GREY = "\033[90m"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"directories": [], "commands": [], "settings": {"view_mode": "full"}}
    
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
        
    # Migration: Ensure directories are objects
    migrated = False
    new_dirs = []
    for d in data.get("directories", []):
        if isinstance(d, str):
            new_dirs.append({"path": d, "category": "General"})
            migrated = True
        else:
            new_dirs.append(d)
    data["directories"] = new_dirs
    
    # Migration: Ensure commands have category
    new_cmds = []
    for c in data.get("commands", []):
        if "category" not in c:
            c["category"] = "General"
            migrated = True
        new_cmds.append(c)
    data["commands"] = new_cmds
    
    if "settings" not in data:
        data["settings"] = {"view_mode": "full"}
        migrated = True

    if migrated:
        save_data(data)
        
    return data

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def run_fzf(items, prompt="Select > ", help_text="", extra_args=None):
    """
    Runs fzf with the given items.
    Items should be a list of strings.
    Returns (key, selection_string).
    """
    safe_header = help_text.replace("|", "^|")

    fzf_cmd = [
        "fzf", 
        "--ansi",
        "--layout=reverse", 
        f"--prompt={prompt} [?] ", 
        f"--preview=echo {safe_header}",
        "--preview-window=up:1:hidden:wrap",
        "--bind=?:toggle-preview",
        "--expect=ctrl-a,ctrl-d,ctrl-e,tab,alt-up,alt-down",
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
    
    if process.returncode == 130:
        return None, None
    
    lines = stdout.splitlines()
    if not lines:
        return None, None
        
    key = lines[0]
    selection = lines[1] if len(lines) > 1 else ""
    return key, selection

def move_item(items, index, direction):
    """Moves item at index up (-1) or down (1)."""
    new_idx = index + direction
    if 0 <= new_idx < len(items):
        items[index], items[new_idx] = items[new_idx], items[index]
        return True
    return False

def get_selection_index(selection):
    """Extracts index from string 'Index\tContent'"""
    if not selection: return -1
    try:
        return int(selection.split('\t')[0])
    except:
        return -1

def main():
    while True:
        data = load_data()
        dirs = data.get("directories", []) # List of dicts
        settings = data.get("settings", {"view_mode": "full"})
        view_mode = settings.get("view_mode", "full")
        
        # Format for FZF: "Index \t DisplayString"
        # Display: "[Category] Path/Name"
        fzf_items = []
        max_cat_len = 0
        if dirs:
            max_cat_len = max(len(d.get("category", "")) for d in dirs)
        
        for idx, d in enumerate(dirs):
            cat = d.get("category", "General")
            path = d.get("path", "")
            
            # Pad category for alignment
            cat_display = f"{C_CYAN}[{cat}]{C_RESET}".ljust(max_cat_len + 12) # +12 for ansi codes roughly
            
            custom_name = d.get("name", "")
            
            if view_mode == "name":
                if custom_name:
                    display_name = custom_name
                else:
                    display_name = os.path.basename(path.rstrip(os.sep).rstrip('/'))
                    if not display_name: display_name = path
                
                display = f"{cat_display} {display_name}"
            else:
                display = f"{cat_display} {path}"
                if custom_name:
                    display += f" ({custom_name})"
            
            fzf_items.append(f"{idx}\t{display}")

        # Hide index (column 1) from display
        fzf_args = ["--delimiter=\t", "--with-nth=2.."]
            
        key, selection = run_fzf(
            fzf_items, 
            prompt=f"Dir ({view_mode}) > ", 
            help_text="Ctrl-A: Add | Ctrl-E: Edit | Ctrl-D: Del | Tab: View | Alt-Up/Down: Move | Enter: Select",
            extra_args=fzf_args
        )
        
        if key is None:
            break
            
        idx = get_selection_index(selection)

        if key == 'tab':
            new_mode = "full" if view_mode == "name" else "name"
            settings["view_mode"] = new_mode
            data["settings"] = settings
            save_data(data)
            continue 

        elif key == 'alt-up':
            if idx != -1 and move_item(dirs, idx, -1):
                data["directories"] = dirs
                save_data(data)
                
        elif key == 'alt-down':
            if idx != -1 and move_item(dirs, idx, 1):
                data["directories"] = dirs
                save_data(data)

        elif key == '':
            if idx != -1 and idx < len(dirs):
                handle_directory(dirs[idx], data) # Pass specific dir object and full data
        
        elif key == 'ctrl-a':
            print("\n--- Add New Directory ---")
            new_dir = input("Enter path: ").strip().strip('"').strip("'")
            if new_dir:
                if os.path.isdir(new_dir):
                    cat = input("Category (default 'General'): ").strip()
                    if not cat: cat = "General"
                    
                    name = input("Display Name (optional): ").strip()

                    # Check duplicates (by path)
                    if not any(d["path"] == new_dir for d in dirs):
                        new_entry = {"path": new_dir, "category": cat}
                        if name: new_entry["name"] = name
                        dirs.append(new_entry)
                        data["directories"] = dirs
                        save_data(data)
                else:
                    input(f"Error: '{new_dir}' is not a valid directory. Press Enter to continue...")
        
        elif key == 'ctrl-e':
            if idx != -1 and idx < len(dirs):
                curr = dirs[idx]
                print(f"\n--- Edit Directory [{curr['path']}] ---")
                
                new_path = input(f"New Path (Enter to keep '{curr['path']}'): ").strip().strip('"').strip("'")
                if not new_path: 
                    new_path = curr['path']
                
                new_cat = input(f"New Category (Enter to keep '{curr.get('category', 'General')}'): ").strip()
                if not new_cat:
                    new_cat = curr.get('category', 'General')
                
                curr_name = curr.get("name", "")
                new_name = input(f"New Display Name (Enter to keep '{curr_name}'): ").strip()
                if not new_name:
                    new_name = curr_name

                if new_path != curr['path'] and not os.path.isdir(new_path):
                     input(f"Error: '{new_path}' is not a valid directory. Press Enter to cancel edit...")
                else:
                    new_entry = {"path": new_path, "category": new_cat}
                    if new_name: new_entry["name"] = new_name
                    dirs[idx] = new_entry
                    data["directories"] = dirs
                    save_data(data)

        elif key == 'ctrl-d':
            if idx != -1 and idx < len(dirs):
                dirs.pop(idx)
                data["directories"] = dirs
                save_data(data)

def handle_directory(dir_obj, data):
    # dir_obj is {"path": "...", "category": "..."}
    directory_path = dir_obj.get("path")
    
    while True:
        # Re-load commands each time to sync
        # But we need to use the passed 'data' for commands since 'main' loaded it. 
        # Actually better to reload to ensure consistency? 
        # For simple tool, using boolean logic is fine.
        commands = data.get("commands", [])
        
        fzf_items = []
        max_cat_len = 0
        if commands:
            max_cat_len = max(len(c.get("category", "")) for c in commands)
            
        for idx, c in enumerate(commands):
            cat = c.get("category", "General")
            name = c.get("name", "Unknown")
            cat_display = f"{C_CYAN}[{cat}]{C_RESET}".ljust(max_cat_len + 12)
            display = f"{cat_display} {name}"
            fzf_items.append(f"{idx}\t{display}")
            
        fzf_args = ["--delimiter=\t", "--with-nth=2.."]
        
        key, selection = run_fzf(
            fzf_items, 
            prompt=f"[{os.path.basename(directory_path)}] Action > ", 
            help_text="Ctrl-A: Add | Ctrl-D: Del | Alt-Up/Down: Move | Enter: Run | Esc: Back",
            extra_args=fzf_args
        )
        
        if key is None:
            return 

        idx = get_selection_index(selection)
        
        if key == '':
            if idx != -1 and idx < len(commands):
                execute_command(commands[idx]["template"], directory_path)
                sys.exit(0)
        
        elif key == 'alt-up':
            if idx != -1 and move_item(commands, idx, -1):
                data["commands"] = commands
                save_data(data)

        elif key == 'alt-down':
            if idx != -1 and move_item(commands, idx, 1):
                data["commands"] = commands
                save_data(data)

        elif key == 'ctrl-a':
            print("\n--- Add New Command ---")
            name = input("Command Name: ").strip()
            if name:
                template = input("Command Template (use {path} as placeholder): ").strip()
                if template:
                    cat = input("Category (default 'General'): ").strip()
                    if not cat: cat = "General"
                    commands.append({"name": name, "template": template, "category": cat})
                    data["commands"] = commands
                    save_data(data)
                    
        elif key == 'ctrl-e':
            if idx != -1 and idx < len(commands):
                curr = commands[idx]
                print(f"\n--- Edit Command [{curr['name']}] ---")
                
                new_name = input(f"New Name (Enter to keep '{curr['name']}'): ").strip()
                if not new_name: new_name = curr['name']
                
                new_temp = input(f"New Template (Enter to keep current): ").strip()
                if not new_temp: new_temp = curr['template']
                
                new_cat = input(f"New Category (Enter to keep '{curr.get('category', 'General')}'): ").strip()
                if not new_cat: new_cat = curr.get('category', 'General')
                
                commands[idx] = {"name": new_name, "template": new_temp, "category": new_cat}
                data["commands"] = commands
                save_data(data)

        elif key == 'ctrl-d':
            if idx != -1 and idx < len(commands):
                commands.pop(idx)
                data["commands"] = commands
                save_data(data)

def execute_command(template, path):
    final_cmd = template.replace("{path}", path)
    print(f"\nExecuting: {final_cmd}")
    subprocess.run(final_cmd, shell=True)

if __name__ == "__main__":
    main()
