# Last Session Summary

## Recent Implementation Context
- **Dynamic Folder Menus (`[dynamic:yes]`)**: Submenus can dynamically scan and list folder contents on hover. Added GUI options (`ahk_shortcuts.json`) to ignore specific folders (e.g., `.git`), extensions, and omit empty folders.
- **Native Context Menu Lazy-Loading**: Intercepted Win32 `WM_INITMENUPOPUP` (0x0117) to lazily load dynamic subfolders *only* when opened. This fixed severe UI freezing and lag on mechanical HDDs during eager recursive scanning.
- **CustomMenuGUI Mouse Wheel Scrolling**: Fixed vertical off-screen overflow for CustomMenuGUI (the custom AHK GUI alternative to native menus). Clamped maximum height to the monitor's work area and implemented a `WM_MOUSEWHEEL` (0x020A) handler to allow smooth scrolling through long lists.
- **Menu Separators**: Any item named starting with `*****` is now parsed and rendered as a horizontal separator line in both the native context menu and `CustomMenuGUI`. Keyboard and mouse-hover navigation automatically skip over separators.
- **Reference Docs**: Documented `dynamic` and `folder` tag syntax in `md/SELECTION_MENU.md`.

*Goal for Next AI*: The dynamic folder system is now fully functional, lazy-loaded (fast), and scrollable in both UI modes. Separators are supported in both native and custom menus. Continue assisting the user with any new features they request.
