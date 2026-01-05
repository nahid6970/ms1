# VS Code State Manager

A modern, high-performance Python GUI application built with PyQt6 for managing and switching between different VS Code state profiles. This tool allows users to maintain multiple workspace configurations and swap them instantly by automating file replacement.

## 🚀 Features

- **Modern Dark UI**: A sleek, premium interface with CSS-driven styling, gradients, and micro-animations.
- **Profile Management**:
    - **Add**: Create new profiles by selecting a source directory and giving it a name.
    - **Edit**: Modify existing profile names or paths.
    - **Delete**: Remove profiles you no longer need.
- **Smart Activation**:
    - Automatically cleans up target files (`state.vscdb` and `state.vscdb.backup`) from the VS Code testing directory.
    - Swaps in files from the selected profile source path.
    - visual feedback: The active profile is highlighted with a distinct glowing gradient.
- **Data Persistence**: Profiles are saved locally in a `profiles.json` file for persistence across sessions.

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Dependencies
Install the required PyQt6 library:
```bash
pip install PyQt6
```

## 📖 Usage

1. **Run the Application**:
   ```bash
   python vsc_manager.py
   ```
2. **Add a Profile**:
   - Click the **+ Add Profile** button.
   - Enter a name (e.g., "Web Dev State") and browse for the folder containing the `.vscdb` files you want to use.
3. **Activate a Profile**:
   - Click the **Activate** button on any profile card.
   - The application will delete the current state files in `C:\Users\nahid\ms\ms1\Testing\Test` and replace them with your profile's files.
   - Only one profile can be active at a time.

## 📂 Project Structure

- `vsc_manager.py`: The main application script containing the PyQt6 GUI and file operation logic.
- `profiles.json`: Stores your configured profiles (Name, Path, Active status).
- `README.md`: Project documentation.

## ⚠️ Important Note
The application is pre-configured to target files in:
`C:\Users\nahid\ms\ms1\Testing\Test`

Ensure this path exists before activating a profile to avoid errors.
