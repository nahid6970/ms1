# Symbolink Manager 🔗

A modern, GUI-based utility for managing Windows symbolic links and directory junctions, built with Python and CustomTkinter.

## ✨ Features

- **Intuitive GUI**: Clean and modern interface powered by `customtkinter`.
- **Dual Support**: Handle both **Folder Junctions** and **File Symbolic Links**.
- **Real-time Status Monitoring**: Automatically checks if your links are:
  - ✅ **Working**: Link exists and points to the correct target.
  - ❌ **Broken**: Target folder/file is missing.
  - ⚠️ **Missing Link**: The shortcut itself has been deleted.
  - 🔄 **Points Elsewhere**: The link exists but points to a different location.
- **Easy Management**: Add, remove, and fix links with just a few clicks.
- **Persistence**: Saves your managed links to a local `links.json` file for future sessions.
- **One-Click Fix**: Recreate missing or broken links directly from the interface.

## 🛠️ Prerequisites

- **Python 3.x**
- **Administrator Privileges**: Creating symbolic links on Windows requires the script to be run with elevated permissions.
- **Dependencies**:
  ```bash
  pip install customtkinter
  ```

## 🚀 How to Use

1. **Install Dependencies**:
   Run `pip install customtkinter` in your terminal.
2. **Run as Administrator**:
   Right-click your terminal (or IDE) and select **"Run as Administrator"**, then run:
   ```bash
   python mklink.py
   ```
3. **Adding a Link**:
   - Click the green **"+" button** in the top-right corner.
   - In the popup window:
     - Provide a name for the entry.
     - Select the type (**Folder** or **File**).
     - Browse for the **Target Path** (where the actual data lives).
     - Browse for the **Fake Path** (where you want the link to appear).
     - Click **Add Entry**.
4. **Creating the Link**:
   - If the link doesn't exist yet, click the **Fix/Link** button in the list to trigger the Windows `mklink` command.

## 📁 File Structure

- `mklink.py`: The main application script.
- `links.json`: Stores the configuration and paths of your managed links (auto-generated).

## ⚠️ Important Notes

- **Junctions vs Symlinks**: By default, folder links are created as Junctions (`/J`), which do not require special developer mode settings in Windows, though Administrator rights are still needed.
- **Data Safety**: Deleting an entry from the manager **will not** delete the files in your target folder. It only removes the management entry and doesn't delete the link itself from your filesystem (you must do that manually or use the "Fix" logic to update).

## 📝 License

Distributed under the MIT License. Feel free to use and modify!
