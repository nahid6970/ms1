# Last Session Summary

## Done So Far
- **⭐ Favourites Section**: Added collapsible Favourites category to aggregate shortcuts of all types, including toggling, edit field synchronization, and persistence.
- **`[cmd:]` Shell Syntax**: Introduced Selection Menu tags `[cmd:]`, `[shell:]`, and `[show:]` to run command line prompts from selection menus.
- **Dynamic Folder Menus (`[dynamic:yes]`)**: Introduced dynamic scanning of folders and subdirectories on hover.
- **Ignore Lists / Exclusions**: Added GUI options (saved in `ahk_shortcuts.json`) to ignore folder names, file extensions, and omit empty folders from dynamic menus.
- **Win32 Native Menu Lazy Loading**: Intercepted low-level Win32 `WM_INITMENUPOPUP` (0x0117) messages in AHK to lazy-load dynamic folder submenus just-in-time, completely fixing mechanical HDD lag for native menus.
- **Mouse Wheel Scrolling**: Resolved vertical overflow in CustomMenuGUI for folders with many items by clamping the GUI window to the monitor height and adding `WM_MOUSEWHEEL` interception to allow scrolling up and down through the list smoothly.
- **Docs Update**: Added the `dynamic` tag parameters to [SELECTION_MENU.md](file:///C:/@delta/ms1/@AutoHotKey/shortcut_manager/md/SELECTION_MENU.md).
