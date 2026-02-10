import winreg
import os

def create_context_group(base_path, group_name, group_label, icon=None):
    """Create a cascading menu group"""
    path = f"{base_path}\\{group_name}"
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
    winreg.SetValueEx(key, "MUIVerb", 0, winreg.REG_SZ, group_label)
    winreg.SetValueEx(key, "SubCommands", 0, winreg.REG_SZ, "")
    if icon:
        winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon)
    winreg.CreateKey(key, "shell")
    winreg.CloseKey(key)
    return path

def create_context_entry(base_path, entry_name, entry_label, command):
    """Create a context menu entry"""
    path = f"{base_path}\\{entry_name}"
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
    winreg.SetValue(key, "", winreg.REG_SZ, entry_label)
    
    cmd_key = winreg.CreateKey(key, "command")
    winreg.SetValue(cmd_key, "", winreg.REG_SZ, command)
    
    winreg.CloseKey(cmd_key)
    winreg.CloseKey(key)

def main():
    # Get the scripts directory
    scripts_dir = os.path.join(os.path.expanduser("~"), ".env_manager", "scripts")
    
    # Define the base paths for context menus
    bases = [
        r"Software\Classes\Directory\shell",
        r"Software\Classes\Directory\Background\shell"
    ]
    
    print("Creating FFMPEG context menu group...")
    
    for base in bases:
        try:
            # Create main FFMPEG group
            ffmpeg_group = create_context_group(base, "FFMPEG", "🎬 FFMPEG Tools")
            print(f"✓ Created FFMPEG group at {base}")
            
            # Add entries under the FFMPEG group
            shell_path = f"{ffmpeg_group}\\shell"
            
            # 1. Convert
            create_context_entry(
                shell_path,
                "Convert",
                "🔄 Convert Video",
                f'powershell.exe -ExecutionPolicy Bypass -File "{os.path.join(scripts_dir, "convert.ps1")}" "%V"'
            )
            print("  ✓ Added Convert")
            
            # 2. Merge
            create_context_entry(
                shell_path,
                "Merge",
                "🔗 Merge Videos",
                f'powershell.exe -ExecutionPolicy Bypass -File "{os.path.join(scripts_dir, "merge.ps1")}" "%V"'
            )
            print("  ✓ Added Merge")
            
            # 3. Trim
            create_context_entry(
                shell_path,
                "Trim",
                "✂️ Trim Video",
                f'powershell.exe -ExecutionPolicy Bypass -File "{os.path.join(scripts_dir, "trim.ps1")}" "%V"'
            )
            print("  ✓ Added Trim")
            
            # 4. Video Dimensions
            create_context_entry(
                shell_path,
                "VidDim",
                "📐 Video Dimensions",
                f'powershell.exe -ExecutionPolicy Bypass -File "{os.path.join(scripts_dir, "vid_dim.ps1")}" "%V"'
            )
            print("  ✓ Added Video Dimensions")
            
            # 5. Android Icon Generator
            create_context_entry(
                shell_path,
                "AndroidIcon",
                "📱 Android Icon Generator",
                f'powershell.exe -ExecutionPolicy Bypass -File "{os.path.join(scripts_dir, "android_icon_generator.ps1")}" "%V"'
            )
            print("  ✓ Added Android Icon Generator")
            
            # 6. Image Resizer
            create_context_entry(
                shell_path,
                "ImageResize",
                "🖼️ Image Resizer",
                f'powershell.exe -ExecutionPolicy Bypass -File "{os.path.join(scripts_dir, "image_resizer.ps1")}" "%V"'
            )
            print("  ✓ Added Image Resizer")
            
            # 7. Image Dimensions
            create_context_entry(
                shell_path,
                "ImageDim",
                "📏 Image Dimensions",
                f'powershell.exe -ExecutionPolicy Bypass -File "{os.path.join(scripts_dir, "image_dimension.ps1")}" "%V"'
            )
            print("  ✓ Added Image Dimensions")
            
        except Exception as e:
            print(f"✗ Error at {base}: {e}")
    
    print("\n✅ FFMPEG context menu group created successfully!")
    print("Right-click on any folder or folder background to see 'FFMPEG Tools' menu.")

if __name__ == "__main__":
    main()
