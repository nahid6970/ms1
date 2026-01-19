# Symbolink Manager 🔗

A professional, high-performance GUI utility for managing Windows symbolic links and directory junctions. Built with Python, CustomTkinter, and styled with JetBrainsMono NFP.

## ✨ Features

- **Modern Square UI**: A sleek, professional interface with sharp corners and a dark aesthetic.
- **JetBrainsMono NFP**: Optimized for developers with monospaced typography throughout.
- **Real-time Search**: Instant filtering of your symlinks by name, target, or fake path.
- **Modal Management**: Add and edit links in a dedicated, high-width popup window (800px) that handles even the longest file paths.
- **Full CRUD Support**: 
  - **Add (➕)**: Easily create new entries.
  - **Edit (📝)**: Modify existing entries without deleting them.
  - **Delete (🗑️)**: Safely remove management entries.
  - **Fix (🔗)**: Recreate broken or missing links with one click. Now intelligently handles "Points Elsewhere" conflicts by cleaning up the old link first.
  - **Open (📂)**: Instantly open Windows Explorer to the location of any link, with the item pre-selected.
- **Color-Coded Paths**: 
  - **Target (Real)**: Blue themed browse button for the source data.
  - **Fake (Link)**: Purple themed browse button for the link destination.
- **Status Monitoring**: Real-time tracking of link health (Working, Broken, Missing, etc.) displayed right next to the entry name.

## 🛠️ Prerequisites

- **Python 3.x**
- **Administrator Privileges**: Required to create/fix symbolic links on Windows.
- **Font**: [JetBrainsMono Nerd Font](https://www.nerdfonts.com/font-downloads) (Recommended for icon rendering).
- **Dependencies**:
  ```bash
  pip install customtkinter
  ```

## 🚀 How to Use

1. **Install Dependencies**:
   ```bash
   pip install customtkinter
   ```
2. **Run as Administrator**:
   Right-click your terminal and select **"Run as Administrator"**, then:
   ```bash
   python mklink.py
   ```
3. **Manage Entries**:
   - **Search**: Start typing in the search box at the top to filter your list instantly.
   - **Adding**: Click the green **"➕ Add Link"** button.
   - **Editing**: Click the orange **"📝 Edit"** button on any entry to modify its details.
   - **Fixing**: Click the blue **"🔗 Fix"** button if a link is missing or broken.
   - **Opening**: Click the purple **"📂 Open"** button to jump directly to the link's folder.
4. **Browse with Precision**:
   Use the blue **📂 Target** button for the actual folders and the purple **📂 Fake** button for the link location.

## 📁 Project Structure

- `mklink.py`: The core application logic.
- `links.json`: Your persisted link database.
- `README.md`: Project documentation.

## ⚠️ Important Notes

- **Junctions vs Symlinks**: Folders use Junctions (`/J`) for maximum compatibility without Developer Mode.
- **Data Safety**: Removing an entry **only** removes it from the manager. It does not delete your physical files or the existing links on your disk.

## 📝 License

Distributed under the MIT License. Built with ❤️ for organized files.
