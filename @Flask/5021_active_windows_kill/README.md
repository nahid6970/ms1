# Active Windows Manager

A simple Flask application to monitor and manage active windows on Windows.

## Features
- **List Active Windows:** Displays all currently visible windows grouped by application.
- **Single Window View:** Applications with only one window are shown in a simple list.
- **Grouped View:** Multiple windows from the same application (like Chrome or VS Code) are grouped in an accordion.
- **Force Kill:** Kill individual windows or all processes of an application directly from the web interface.
- **Auto-Refresh:** Easily refresh the list to see current active windows.

## Requirements
- Windows OS
- Python 3.x
- `flask`
- `pywin32`
- `psutil`

## Setup and Run
1. Install dependencies:
   ```bash
   pip install flask pywin32 psutil
   ```
2. Run the application:
   ```bash
   python app.py
   ```
3. Open your browser and navigate to:
   `http://localhost:5021`

## Usage
- Click the **Refresh** button to update the list of active windows.
- Click the **red cross icon** next to a window title to kill that specific process.
- Click **Kill All** in an application group to terminate all instances of that application.
