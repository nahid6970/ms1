# Startup Manager - Go Web Edition

A modern web-based application for managing Windows startup items, built with Go and served through your browser.

## Features

- ✅ Add, edit, and delete startup items
- ✅ Enable/disable items with checkboxes
- ✅ Search and filter items
- ✅ Generate PowerShell startup script
- ✅ Launch items directly from the GUI
- ✅ Modern web UI with dark theme
- ✅ JSON-based storage (compatible with Python version)
- ✅ Real-time search and filtering
- ✅ Responsive design for mobile/desktop
- 🔄 Registry scanning (planned)

## Installation

### Prerequisites

- Go 1.21 or later
- Windows (for PowerShell script execution)

### Build from source

```bash
# Clone or download the project
git clone <repository-url>
cd startup-manager

# Install dependencies
go mod tidy

# Build the application
go build -o startup-manager.exe

# Run the application
./startup-manager.exe
```

### Quick start

```bash
# Run directly without building
go run main.go

# Then open your browser to http://localhost:8090
```

## Usage

1. **Add Items**: Click "Add Item" to create new startup entries
2. **Enable/Disable**: Use checkboxes to control which items run at startup
3. **Search**: Use the search box to filter items by name or command
4. **Launch**: Double-click items or use the context menu to test commands
5. **PowerShell Script**: The app generates `myStartup.ps1` on your Desktop

### PowerShell Commands Examples

```powershell
# Launch an application
Start-Process "notepad.exe"

# Run with arguments
Start-Process -FilePath "C:\Program Files\App\app.exe" -ArgumentList "/silent"

# Execute a script
python "C:\path\to\script.py"

# Run a command
& "C:\tools\mytool.exe"
```

## File Structure

- `startup_items.json` - Stores your startup items configuration
- `~/Desktop/myStartup.ps1` - Generated PowerShell script for enabled items

## Advantages over Python Version

### ✅ Implemented & Improved
- **Web-based UI** - Access from any browser, no GUI dependencies
- **Better performance** - Compiled Go binary vs interpreted Python
- **Modern design** - Responsive, mobile-friendly interface
- **No dependencies** - Single executable, no Python/tkinter required
- **Cross-platform** - Works on Windows, Mac, Linux
- **Real-time search** - Instant filtering without page reloads
- **Better UX** - Card-based layout, intuitive controls

### 🔄 Not Yet Implemented
- Windows Registry scanning (more complex in Go)
- Desktop notifications

## Dependencies

- **Zero runtime dependencies** - Pure Go standard library
- **No GUI frameworks** - Uses web browser as interface

## Building for Distribution

```bash
# Build optimized binary
go build -ldflags="-s -w" -o startup-manager.exe

# Or use Fyne's packaging tool
go install fyne.io/fyne/v2/cmd/fyne@latest
fyne package -os windows
```

## License

MIT License - feel free to modify and distribute.