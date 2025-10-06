import sys
import json
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QDesktopWidget, QWidget, QVBoxLayout, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, pyqtSlot, QObject, QPoint
from PyQt5.QtGui import QPalette
from PyQt5.QtWebChannel import QWebChannel

class FolderManager(QObject):
    def __init__(self, html_window):
        super().__init__()
        self.html_window = html_window
        self.json_file = "folders.json"
        self.folders = self.load_folders()
    
    def load_folders(self):
        """Load folders from JSON file"""
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading folders: {e}")
            return []
    
    def save_folders(self):
        """Save folders to JSON file"""
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(self.folders, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving folders: {e}")
    
    @pyqtSlot(result=str)
    def get_folders(self):
        """Return folders as JSON string"""
        return json.dumps(self.folders)
    
    @pyqtSlot()
    def add_folder(self):
        """Open folder dialog and add selected folder"""
        folder_path = QFileDialog.getExistingDirectory(
            self.html_window, 
            "Select Folder", 
            os.path.expanduser("~")
        )
        
        if folder_path:
            folder_info = {
                "name": os.path.basename(folder_path),
                "path": folder_path,
                "id": len(self.folders)
            }
            self.folders.append(folder_info)
            self.save_folders()
            return True
        return False
    
    @pyqtSlot(int)
    def remove_folder(self, folder_id):
        """Remove folder by ID"""
        self.folders = [f for f in self.folders if f.get('id') != folder_id]
        # Reassign IDs
        for i, folder in enumerate(self.folders):
            folder['id'] = i
        self.save_folders()
    
    @pyqtSlot(str)
    def open_folder(self, folder_path):
        """Open folder in file explorer"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(folder_path)
            elif os.name == 'posix':  # macOS and Linux
                os.system(f'open "{folder_path}"' if sys.platform == 'darwin' else f'xdg-open "{folder_path}"')
        except Exception as e:
            print(f"Error opening folder: {e}")
    
    @pyqtSlot()
    def close_window(self):
        self.html_window.close()

class FolderWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Folder Manager")
        
        # Center the window on screen - make it more compact
        self.resize(720, 520)
        self.center_window()
        
        # Remove window frame and title bar for clean look
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # Variables for window dragging
        self.dragging = False
        self.drag_position = QPoint()
        
        # Setup the UI
        self.setup_ui()
    
    def center_window(self):
        """Center the window on the screen"""
        screen = QApplication.desktop().screenGeometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)
    
    def mousePressEvent(self, event):
        """Handle mouse press for window dragging"""
        if event.button() == Qt.LeftButton:
            # Check if the click is on the drag handle
            drag_handle_rect = self.drag_handle.geometry()
            if drag_handle_rect.contains(event.pos()):
                self.dragging = True
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()
                return
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging"""
        if event.buttons() == Qt.LeftButton and self.dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release to stop dragging"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
        super().mouseReleaseEvent(event)
    
    def setup_ui(self):
        """Setup the web view and HTML content"""
        # Create main widget and layout
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create drag handle
        self.drag_handle = QLabel("⋮⋮⋮ Drag to move ⋮⋮⋮")
        self.drag_handle.setFixedHeight(30)
        self.drag_handle.setAlignment(Qt.AlignCenter)
        self.drag_handle.setStyleSheet("""
            QLabel {
                background: rgba(102, 126, 234, 0.3);
                color: white;
                font-size: 12px;
                border: none;
            }
            QLabel:hover {
                background: rgba(102, 126, 234, 0.5);
            }
        """)
        self.drag_handle.setCursor(Qt.SizeAllCursor)
        
        # Create web view and channel
        self.web_view = QWebEngineView()
        self.channel = QWebChannel()
        self.manager = FolderManager(self)
        
        # Register the manager object with the web channel
        self.channel.registerObject('manager', self.manager)
        self.web_view.page().setWebChannel(self.channel)
        
        # Add widgets to layout
        layout.addWidget(self.drag_handle)
        layout.addWidget(self.web_view)
        
        # Set main widget
        self.setCentralWidget(main_widget)
        
        # Load HTML content
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            <style>
                body {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    margin: 0;
                    padding: 0;
                    height: 100vh;
                    overflow: hidden;
                }
                .content-area {
                    padding: 15px;
                    height: calc(100vh - 30px);
                    overflow: hidden;
                }
                .container {
                    display: flex;
                    flex-direction: column;
                    height: 100%;
                }
                .header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 15px;
                    user-select: none;
                    padding: 10px;
                    border-radius: 10px;
                }
                .header-buttons {
                    display: flex;
                    gap: 10px;
                    align-items: center;
                }
                .search-bar {
                    flex: 1;
                    background: rgba(255,255,255,0.1);
                    border: 2px solid rgba(255,255,255,0.2);
                    border-radius: 20px;
                    padding: 8px 15px;
                    color: white;
                    font-size: 14px;
                    outline: none;
                    transition: all 0.2s ease;
                }
                .search-bar::placeholder {
                    color: rgba(255,255,255,0.6);
                }
                .search-bar:focus {
                    border-color: rgba(255,255,255,0.5);
                    background: rgba(255,255,255,0.15);
                }
                .header-btn {
                    background: rgba(255,255,255,0.2);
                    border: none;
                    color: white;
                    font-size: 18px;
                    cursor: pointer;
                    padding: 8px 12px;
                    border-radius: 50%;
                    transition: all 0.2s ease;
                    user-select: none;
                    z-index: 1000;
                    width: 36px;
                    height: 36px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .add-btn:hover {
                    background: rgba(0,255,0,0.6);
                    transform: scale(1.1);
                }
                .close-btn:hover {
                    background: rgba(255,0,0,0.6);
                    transform: scale(1.1);
                }

                .folders-container {
                    flex: 1;
                    background: rgba(255,255,255,0.1);
                    border-radius: 15px;
                    padding: 15px;
                    backdrop-filter: blur(10px);
                    overflow-y: auto;
                }
                .folder-item {
                    background: rgba(255,255,255,0.1);
                    border-radius: 8px;
                    padding: 12px;
                    margin-bottom: 8px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    border: 2px solid transparent;
                }
                .folder-item:hover {
                    background: rgba(255,255,255,0.2);
                    border-color: rgba(255,255,255,0.3);
                    transform: translateX(5px);
                }
                .folder-info {
                    flex: 1;
                }
                .folder-display {
                    font-size: 1.05em;
                    font-weight: bold;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    flex-wrap: wrap;
                }
                .folder-name {
                    color: white;
                }
                .folder-path {
                    font-size: 0.9em;
                    opacity: 0.7;
                    font-weight: normal;
                    word-break: break-all;
                }
                .path-separator {
                    opacity: 0.5;
                    font-weight: normal;
                }
                .folder-actions {
                    display: flex;
                    gap: 10px;
                }
                .action-btn {
                    background: rgba(255,255,255,0.2);
                    border: none;
                    color: white;
                    padding: 8px 12px;
                    border-radius: 5px;
                    cursor: pointer;
                    transition: background 0.2s ease;
                    font-size: 12px;
                }
                .action-btn:hover {
                    background: rgba(255,255,255,0.3);
                }
                .delete-btn:hover {
                    background: rgba(255,0,0,0.6);
                }
                .empty-state {
                    text-align: center;
                    padding: 40px;
                    opacity: 0.7;
                }
                .loading {
                    text-align: center;
                    padding: 20px;
                }
                
                /* Custom Scrollbar Styling */
                .folders-container::-webkit-scrollbar {
                    width: 8px;
                }
                .folders-container::-webkit-scrollbar-track {
                    background: transparent;
                }
                .folders-container::-webkit-scrollbar-thumb {
                    background: rgba(255, 0, 0, 0.7);
                    border-radius: 4px;
                    transition: background 0.2s ease;
                }
                .folders-container::-webkit-scrollbar-thumb:hover {
                    background: rgba(255, 0, 0, 0.9);
                }
                .folders-container::-webkit-scrollbar-corner {
                    background: transparent;
                }
            </style>
        </head>
        <body>
            <div class="content-area">
                <div class="container">
                    <div class="header">
                        <input type="text" class="search-bar" placeholder="🔍 Search folders..." oninput="filterFolders(this.value)">
                        <div class="header-buttons">
                            <button class="header-btn add-btn" onclick="addFolder()" title="Add Folder">+</button>
                            <button class="header-btn close-btn" onclick="closeWindow()" title="Close">×</button>
                        </div>
                    </div>
                
                <div class="folders-container">
                    <div id="folders-list" class="loading">Loading folders...</div>
                </div>
            </div>
            
            <script>
                let manager;
                
                new QWebChannel(qt.webChannelTransport, function(channel) {
                    manager = channel.objects.manager;
                    loadFolders();
                });
                
                function loadFolders() {
                    if (manager) {
                        manager.get_folders(function(result) {
                            allFolders = JSON.parse(result);
                            displayFolders(allFolders);
                        });
                    }
                }
                
                function displayFolders(folders) {
                    const listElement = document.getElementById('folders-list');
                    
                    if (folders.length === 0) {
                        const searchValue = document.querySelector('.search-bar').value;
                        if (searchValue) {
                            listElement.innerHTML = `
                                <div class="empty-state">
                                    <h3>No folders found</h3>
                                    <p>No folders match your search criteria</p>
                                </div>
                            `;
                        } else {
                            listElement.innerHTML = `
                                <div class="empty-state">
                                    <h3>No folders added yet</h3>
                                    <p>Click the "+" button to get started!</p>
                                </div>
                            `;
                        }
                        return;
                    }
                    
                    listElement.innerHTML = '';
                    
                    folders.forEach(folder => {
                        const item = document.createElement('div');
                        item.className = 'folder-item';
                        item.innerHTML = `
                            <div class="folder-info" onclick="openFolder('${folder.path}')">
                                <div class="folder-display">
                                    <span class="folder-name">📁 ${folder.name}</span>
                                    <span class="folder-path">&nbsp;&nbsp;${folder.path}</span>
                                </div>
                            </div>
                            <div class="folder-actions">
                                <button class="action-btn delete-btn" onclick="removeFolder(${folder.id})">Delete</button>
                            </div>
                        `;
                        listElement.appendChild(item);
                    });
                }
                
                function addFolder() {
                    if (manager) {
                        manager.add_folder();
                        // Reload folders after a short delay
                        setTimeout(loadFolders, 500);
                    }
                }
                
                function removeFolder(folderId) {
                    if (manager && confirm('Are you sure you want to remove this folder?')) {
                        manager.remove_folder(folderId);
                        loadFolders();
                    }
                }
                
                function openFolder(folderPath) {
                    if (manager) {
                        manager.open_folder(folderPath);
                    }
                }
                
                function closeWindow() {
                    if (manager) {
                        manager.close_window();
                    }
                }
                
                let allFolders = [];
                
                function filterFolders(searchTerm) {
                    const filteredFolders = allFolders.filter(folder => 
                        folder.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                        folder.path.toLowerCase().includes(searchTerm.toLowerCase())
                    );
                    displayFolders(filteredFolders);
                }
            </script>
        </body>
        </html>
        """
        
        self.web_view.setHtml(html_content)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Directly show the folder manager window
    folder_window = FolderWindow()
    folder_window.show()
    
    sys.exit(app.exec_())