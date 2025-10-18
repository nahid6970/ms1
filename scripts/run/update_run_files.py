import re

def update_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update shortcuts text
    content = content.replace(
        'Shortcuts available:\n  Enter   : Show action menu (VSCode/Folder/Run/Copy/Terminal)',
        'Shortcuts available:\n  Enter   : Show action menu (Editor/VSCode/Folder/Run/Copy/Terminal)\n  Ctrl-n  : Open file with editor chooser - works with multi-select'
    )
    
    # Add Editor option to menu (after Run option)
    content = re.sub(
        r'(f"{pad}{esc\(\'#9efa49\'\)}.*?Run.*?{len\(file_paths\)}",)\n(\s+f"{pad}{esc\(\'#19d600\'\)})',
        r'\1\n        f"{pad}{esc(\'#ff9500\')}  Editor\\x1b[0m\\t{len(file_paths)}",\n\2',
        content
    )
    
    # Add Editor handling in selection (before VSCode)
    # Find the pattern and add Editor handling
    pattern = r'(selection = stdout\.strip\(\)\s+#! Open all files in VSCode\s+if selection\.startswith\()'
    replacement = r'\1selection = stdout.strip()\n            #! Open with editor chooser\n            if selection.startswith(\'\'):\n                script_dir = os.path.dirname(os.path.abspath(__file__))\n                editor_chooser_script = os.path.join(script_dir, "editor_chooser.py")\n                for file_path in file_paths:\n                    subprocess.run(f\'python "{editor_chooser_script}" "{os.path.abspath(file_path)}"\', shell=True)\n            #! Open all files in VSCode\n            elif selection.startswith('
    
    # Change first 'if' to 'if' for Editor, then change VSCode/emacs/nvim 'if' to 'elif'
    lines = content.split('\n')
    new_lines = []
    found_selection = False
    editor_added = False
    
    for i, line in enumerate(lines):
        if 'selection = stdout.strip()' in line and not found_selection:
            found_selection = True
            new_lines.append(line)
        elif found_selection and not editor_added and '#! Open all files in VSCode' in line:
            # Add Editor option before VSCode
            new_lines.append('            #! Open with editor chooser')
            new_lines.append('            if selection.startswith(\'\'):')
            new_lines.append('                script_dir = os.path.dirname(os.path.abspath(__file__))')
            new_lines.append('                editor_chooser_script = os.path.join(script_dir, "editor_chooser.py")')
            new_lines.append('                for file_path in file_paths:')
            new_lines.append('                    subprocess.run(f\'python "{editor_chooser_script}" "{os.path.abspath(file_path)}"\', shell=True)')
            new_lines.append(line)
            editor_added = True
        elif editor_added and i < len(lines) - 1:
            # Change 'if selection.startswith' to 'elif selection.startswith' for VSCode, emacs, nvim
            if '            if selection.startswith' in line and i > 0:
                line = line.replace('            if selection.startswith', '            elif selection.startswith')
            new_lines.append(line)
        else:
            new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    # Add Ctrl+N binding to fzf_args
    # Find the fzf_args section and add the binding
    content = re.sub(
        r'(f"--bind=enter:execute\({batch_file} \{\{\\+1\}\}\)",)',
        r'\1\n            f"--bind=ctrl-n:execute-silent(python \\"{editor_chooser_script}\\" {{1}})",',
        content
    )
    
    # Make sure editor_chooser_script is defined before fzf_args
    if 'editor_chooser_script = os.path.join(script_dir, "editor_chooser.py")' not in content.split('# Prepare fzf arguments')[0]:
        content = content.replace(
            '# Prepare fzf arguments',
            'editor_chooser_script = os.path.join(script_dir, "editor_chooser.py")\n        \n        # Prepare fzf arguments'
        )
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'Updated {filename}')

# Update both files
update_file('Run.py')
update_file('Run_old.py')
print('Done!')
