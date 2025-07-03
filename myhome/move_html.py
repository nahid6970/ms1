import os
import shutil

templates_dir = r'C:\ms1\myhome\templates'
html_file = r'C:\ms1\myhome\myhome_input.html'

os.makedirs(templates_dir, exist_ok=True)
shutil.move(html_file, templates_dir)

print(f"Moved {html_file} to {templates_dir}")