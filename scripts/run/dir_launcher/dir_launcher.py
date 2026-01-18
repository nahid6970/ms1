import sys
import os
import json
import subprocess

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dir_launcher.json")

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"directories": [], "commands": []}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def run_fzf(items, prompt="Select > ", header=""):
    """
    Runs fzf with the given items.
    Returns (key, selection).
    key is 'ctrl-a', 'ctrl-d' or '' (for enter).
    Returns (None, None) if cancelled.
    """
    fzf_cmd = [
        "fzf", 
        "--layout=reverse", 
        f"--prompt={prompt}", 
        f"--header={header}", 
        "--expect=ctrl-a,ctrl-d"
    ]
    
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

def main():
    while True:
        data = load_data()
        dirs = data.get("directories", [])
        
        key, selected_dir = run_fzf(
            dirs, 
            prompt="Dir > ", 
            header="Ctrl-A: Add Path | Ctrl-D: Remove Path | Enter: Select"
        )
        
        if key is None:
            # Esc pressed
            break
            
        if key == '':
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
            header="Ctrl-A: Add Cmd | Ctrl-D: Remove Cmd | Enter: Run | Esc: Back"
        )
        
        if key is None:
            return # Back to dir selection

        if key == '':
            if selected_cmd_name:
                cmd_obj = next((c for c in commands if c["name"] == selected_cmd_name), None)
                if cmd_obj:
                    execute_command(cmd_obj["template"], directory)
                    sys.exit(0) # Done
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
