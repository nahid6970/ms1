# Active Windows Manager

A refined Flask application for monitoring, managing, and forcefully terminating active windows on Windows systems.

## Key Features
- **Real-time Search:** Instantly filter active windows or applications using the integrated search bar.
- **Dynamic Grouping:** Automatically groups multiple windows of the same application (e.g., Chrome tabs, VS Code instances) for a cleaner view.
- **Smart Prioritization:** Grouped applications are sorted to appear at the top of the list.
- **Persistent Blocklist:** 
  - Hide unwanted background apps with a single click.
  - Manage your blocklist via the settings modal.
  - Blocklist persists across application restarts in `blocklist.json`.
- **Process Termination:**
  - **Kill Window:** Terminate specific windows instantly.
  - **Kill All:** Force-close all running instances of a specific application.
- **High-Quality Icons:** Displays application icons with transparency support for better visibility.
- **Workspace Support:** Enhanced window detection works with tiling window managers like **Komorebi**.

## Prerequisites
- **Operating System:** Windows 10/11
- **Python:** 3.x
- **Dependencies:**
  - `flask`
  - `pywin32`
  - `psutil`
  - `pillow`

## Installation
1. Install the required Python packages:
   ```bash
   pip install flask pywin32 psutil pillow
   ```

## Running the Application
1. Start the server:
   ```bash
   python app.py
   ```
2. Access the dashboard:
   Open your browser to `http://localhost:5021`

## Interface Guide
- **Search Bar:** Type to filter the list of windows.
- **Gear Icon (Settings):** View and manage blocked applications.
- **Eye-Slash Icon:** Block an application from appearing in the list.
- **Red Cross Icon:** Terminate the process associated with that window.
- **Kill All Button:** Close all processes of that specific application.
- **Refresh Icon:** Manually reload the window list.
