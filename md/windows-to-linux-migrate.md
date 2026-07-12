# Windows to Linux Python Migration Prompt
Please help me migrate this Python script so that it runs seamlessly on both Windows and Linux (cross-platform compatibility). 

Please follow these guidelines:
1. **Preserve Windows Functionality**: The script must remain 100% functional on Windows. Use platform checks (e.g., `os.name != 'nt'`) to branch OS-specific logic.
2. **Path Normalization**: Ensure paths are handled correctly on both systems. If the script loads settings or databases containing hardcoded Windows paths (like backslashes or drive letters `C:\`), implement a dynamic path normalization helper (e.g., translating `C:\` to the user's home directory prefix and backslashes to forward slashes when running on Linux).
3. **System Commands / Folder Opening**: Replace Windows-only subprocesses (like opening directories via `explorer.exe`) with cross-platform alternatives (e.g., check for `os.startfile` first, then fall back to `xdg-open` on Linux).
4. **Add Executability**: Add a Unix shebang (`#!/usr/bin/env python3`) to the top of the file so it can be run directly on Linux.
5. **Change Strategy**:
   - Aim for minimal, clean changes.
   - If the script can be migrated with simple local modifications, proceed and show me the code/diff.
   - If migrating requires major restructuring or potentially breaking changes, please list the issues first and ask for my approval before modifying the code.
