import winreg
import shlex
import re

def get_default_browser_path():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice') as key:
            prog_id, _ = winreg.QueryValueEx(key, 'ProgId')
            
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, rf'{prog_id}\shell\open\command') as key:
            command, _ = winreg.QueryValueEx(key, '')
            
        match = re.search(r'"([^"]+)"|([^ ]+)', command)
        if match:
            return match.group(1) if match.group(1) else match.group(2)
            
    except Exception as e:
        return f'Error: {e}'
        
print(get_default_browser_path())
