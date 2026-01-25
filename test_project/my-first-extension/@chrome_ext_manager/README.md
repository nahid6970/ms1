# Chrome Extension Data Manager

A Python-based solution for managing data from multiple Chrome extensions without manual file downloads.

## How It Works

1. **Python Server**: Runs in the background and listens for data from your extensions
2. **Chrome Extensions**: Send their data directly to the Python server via HTTP
3. **Automatic Organization**: Data is saved to organized folders by extension name with timestamps

## Setup Instructions

### 1. Start the Python Server

```bash
python extension_manager.py
```

The server will run on `http://localhost:8765` and save data to `./extension_data/`

### 2. Configure Your Chrome Extensions

For each extension, you need to:

#### A. Update `manifest.json`

Add these permissions:

```json
{
  "permissions": ["storage"],
  "host_permissions": ["http://localhost:8765/*"]
}
```

#### B. Add Background Script

Create or update `background.js`:

```javascript
const PYTHON_SERVER = 'http://localhost:8765';
const EXTENSION_NAME = 'your_extension_name'; // Folder name
const FILE_NAME = 'data.json'; // Your custom filename

async function sendDataToPython(data) {
  const response = await fetch(PYTHON_SERVER, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      extension_name: EXTENSION_NAME,
      file_name: FILE_NAME,
      data: data
    })
  });
  return await response.json();
}

// Auto-save on storage changes
chrome.storage.local.onChanged.addListener(() => {
  chrome.storage.local.get(null, (items) => {
    sendDataToPython(items);
  });
});
```

#### C. Add Manual Save Button (Optional)

In your popup or options page:

```javascript
// Save button click
document.getElementById('saveBtn').addEventListener('click', () => {
  chrome.storage.local.get(null, (items) => {
    sendDataToPython(items)
      .then(() => alert('Data saved!'))
      .catch(err => alert('Error: ' + err));
  });
});
```

## File Structure

```
extension_data/
├── extension1/
│   └── data_for_ext_1.json
├── highlight_ext/
│   └── highlight.json
├── todo_extension/
│   └── todos.json
└── notes_ext/
    └── my_notes.json
```

Each extension saves to its own folder with your custom filename!

## Configuration Examples

### Extension 1 - Todo App
```javascript
const EXTENSION_NAME = 'extension1';
const FILE_NAME = 'data_for_ext_1.json';
```
Saves to: `extension_data/extension1/data_for_ext_1.json`

### Extension 2 - Highlighter
```javascript
const EXTENSION_NAME = 'highlight_ext';
const FILE_NAME = 'highlight.json';
```
Saves to: `extension_data/highlight_ext/highlight.json`

### Extension 3 - Notes
```javascript
const EXTENSION_NAME = 'notes_ext';
const FILE_NAME = 'my_notes.json';
```
Saves to: `extension_data/notes_ext/my_notes.json`

## Features

- ✅ Automatic data saving when extension storage changes
- ✅ Manual save button support
- ✅ Organized by extension name
- ✅ Timestamped files
- ✅ Server health check endpoint
- ✅ CORS enabled for local development
- ✅ Detailed logging

## Customization

### Change Save Location

Edit `extension_manager.py`:

```python
DATA_DIR = Path('./my_custom_folder')
```

### Change Port

Edit `extension_manager.py`:

```python
PORT = 9000  # Your preferred port
```

Then update `PYTHON_SERVER` in your extension's `background.js`:

```javascript
const PYTHON_SERVER = 'http://localhost:9000';
```

### Custom File Naming

Modify the `do_POST` method in `extension_manager.py`:

```python
filename = f"{extension_name}_custom_{timestamp}.json"
```

## Troubleshooting

**Extension can't connect to server:**
- Make sure Python script is running
- Check that port 8765 is not blocked by firewall
- Verify `host_permissions` in manifest.json

**Data not saving:**
- Check Python console for errors
- Verify extension has correct `EXTENSION_NAME`
- Check browser console for JavaScript errors

**CORS errors:**
- Server already handles CORS, but ensure you're using `http://localhost:8765`
- Don't use `127.0.0.1` - use `localhost`

## Running on Startup (Optional)

### Windows
Create a batch file `start_manager.bat`:
```batch
@echo off
python C:\path\to\extension_manager.py
```

Add to Windows Startup folder.

### Linux/Mac
Add to crontab:
```bash
@reboot python /path/to/extension_manager.py
```

Or create a systemd service.
