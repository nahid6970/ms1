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
    
    @pyqtSlot(int, bool)
    def move_folder(self, folder_id, move_up):
        """Move folder up or down in the list"""
        if folder_id < 0 or folder_id >= len(self.folders):
            return
        
        if move_up and folder_id > 0:
            # Move up (swap with previous)
            self.folders[folder_id], self.folders[folder_id - 1] = self.folders[folder_id - 1], self.folders[folder_id]
        elif not move_up and folder_id < len(self.folders) - 1:
            # Move down (swap with next)
            self.folders[folder_id], self.folders[folder_id + 1] = self.folders[folder_id + 1], self.folders[folder_id]
        
        # Reassign IDs after reordering
        for i, folder in enumerate(self.folders):
            folder['id'] = i
        
        self.save_folders()
    
    @pyqtSlot(int, str, str)
    def edit_folder(self, folder_id, new_name, new_path):
        """Edit folder name and path"""
        if folder_id < 0 or folder_id >= len(self.folders):
            return
        
        if new_name.strip() and new_path.strip():
            self.folders[folder_id]['name'] = new_name.strip()
            self.folders[folder_id]['path'] = new_path.strip()
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
        self.drag_handle.setFixedHeight(15)
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
                    height: calc(100vh - 15px);
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
                .move-btn {
                    background: rgba(255,255,255,0.2);
                    border: none;
                    color: white;
                    padding: 6px 8px;
                    border-radius: 5px;
                    cursor: pointer;
                    transition: background 0.2s ease;
                    font-size: 14px;
                    user-select: none;
                }
                .move-btn:hover {
                    background: rgba(0,150,255,0.6);
                }
                .edit-btn {
                    background: rgba(255,255,255,0.2);
                    border: none;
                    color: white;
                    padding: 6px 8px;
                    border-radius: 5px;
                    cursor: pointer;
                    transition: background 0.2s ease;
                    font-size: 12px;
                    user-select: none;
                }
                .edit-btn:hover {
                    background: rgba(255,165,0,0.6);
                }
                .folder-actions {
                    display: flex;
                    gap: 5px;
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
                
                /* Custom Dialogs */
                .dialog-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.5);
                    display: none;
                    justify-content: center;
                    align-items: center;
                    z-index: 9999;
                }
                .confirm-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.5);
                    display: none;
                    justify-content: center;
                    align-items: center;
                    z-index: 9999;
                }
                .confirm-dialog {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border: 2px solid rgba(255, 255, 255, 0.3);
                    border-radius: 15px;
                    padding: 25px;
                    text-align: center;
                    min-width: 300px;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                }
                .confirm-title {
                    font-size: 1.3em;
                    font-weight: bold;
                    margin-bottom: 15px;
                    color: white;
                }
                .confirm-message {
                    margin-bottom: 20px;
                    color: rgba(255, 255, 255, 0.9);
                    line-height: 1.4;
                }
                .confirm-buttons {
                    display: flex;
                    gap: 10px;
                    justify-content: center;
                }
                .confirm-btn {
                    padding: 8px 20px;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: bold;
                    transition: all 0.2s ease;
                }
                .confirm-yes {
                    background: rgba(255, 0, 0, 0.8);
                    color: white;
                }
                .confirm-yes:hover {
                    background: rgba(255, 0, 0, 1);
                    transform: scale(1.05);
                }
                .confirm-no {
                    background: rgba(255, 255, 255, 0.2);
                    color: white;
                }
                .confirm-no:hover {
                    background: rgba(255, 255, 255, 0.3);
                    transform: scale(1.05);
                }
                
                /* Edit Dialog */
                .edit-dialog {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border: 2px solid rgba(255, 255, 255, 0.3);
                    border-radius: 15px;
                    padding: 25px;
                    min-width: 400px;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                }
                .edit-title {
                    font-size: 1.3em;
                    font-weight: bold;
                    margin-bottom: 20px;
                    color: white;
                    text-align: center;
                }
                .edit-field {
                    margin-bottom: 15px;
                }
                .edit-label {
                    display: block;
                    margin-bottom: 5px;
                    color: white;
                    font-weight: bold;
                }
                .edit-input {
                    width: 100%;
                    padding: 8px 12px;
                    border: 2px solid rgba(255, 255, 255, 0.3);
                    border-radius: 8px;
                    background: rgba(255, 255, 255, 0.1);
                    color: white;
                    font-size: 14px;
                    outline: none;
                    box-sizing: border-box;
                }
                .edit-input:focus {
                    border-color: rgba(255, 255, 255, 0.6);
                    background: rgba(255, 255, 255, 0.15);
                }
                .edit-input::placeholder {
                    color: rgba(255, 255, 255, 0.5);
                }
                .edit-buttons {
                    display: flex;
                    gap: 10px;
                    justify-content: center;
                    margin-top: 20px;
                }
                .edit-save {
                    background: rgba(0, 255, 0, 0.8);
                    color: white;
                }
                .edit-save:hover {
                    background: rgba(0, 255, 0, 1);
                    transform: scale(1.05);
                }
                .edit-cancel {
                    background: rgba(255, 255, 255, 0.2);
                    color: white;
                }
                .edit-cancel:hover {
                    background: rgba(255, 255, 255, 0.3);
                    transform: scale(1.05);
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
            
            <!-- Custom Confirmation Dialog -->
            <div id="confirm-overlay" class="confirm-overlay">
                <div class="confirm-dialog">
                    <div class="confirm-title">🗑️ Delete Folder</div>
                    <div class="confirm-message" id="confirm-message">Are you sure you want to remove this folder from the list?</div>
                    <div class="confirm-buttons">
                        <button class="confirm-btn confirm-yes" onclick="confirmDelete(true)">Delete</button>
                        <button class="confirm-btn confirm-no" onclick="confirmDelete(false)">Cancel</button>
                    </div>
                </div>
            </div>
            
            <!-- Edit Dialog -->
            <div id="edit-overlay" class="dialog-overlay">
                <div class="edit-dialog">
                    <div class="edit-title">✏️ Edit Folder</div>
                    <div class="edit-field">
                        <label class="edit-label">Folder Name:</label>
                        <input type="text" id="edit-name" class="edit-input" placeholder="Enter folder name">
                    </div>
                    <div class="edit-field">
                        <label class="edit-label">Folder Path:</label>
                        <input type="text" id="edit-path" class="edit-input" placeholder="Enter folder path">
                    </div>
                    <div class="edit-buttons">
                        <button class="confirm-btn edit-save" onclick="saveEdit()">Save</button>
                        <button class="confirm-btn edit-cancel" onclick="cancelEdit()">Cancel</button>
                    </div>
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
                                <button class="edit-btn" onclick="editFolder(${folder.id})" title="Edit folder name and path">✏️</button>
                                <button class="move-btn" 
                                        onmousedown="handleMoveClick(event, ${folder.id})" 
                                        oncontextmenu="return false"
                                        title="Left click: Move Up | Right click: Move Down">↕</button>
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
                
                let pendingDeleteId = null;
                
                function removeFolder(folderId) {
                    pendingDeleteId = folderId;
                    document.getElementById('confirm-overlay').style.display = 'flex';
                }
                
                function confirmDelete(confirmed) {
                    document.getElementById('confirm-overlay').style.display = 'none';
                    
                    if (confirmed && pendingDeleteId !== null && manager) {
                        manager.remove_folder(pendingDeleteId);
                        loadFolders();
                    }
                    
                    pendingDeleteId = null;
                }
                
                function handleMoveClick(event, folderId) {
                    event.preventDefault();
                    
                    if (manager) {
                        if (event.button === 0) {
                            // Left click - move up
                            manager.move_folder(folderId, true);
                        } else if (event.button === 2) {
                            // Right click - move down
                            manager.move_folder(folderId, false);
                        }
                        
                        // Reload folders to show new order
                        setTimeout(loadFolders, 100);
                    }
                }
                
                let editingFolderId = null;
                
                function editFolder(folderId) {
                    const folder = allFolders.find(f => f.id === folderId);
                    if (!folder) return;
                    
                    editingFolderId = folderId;
                    document.getElementById('edit-name').value = folder.name;
                    document.getElementById('edit-path').value = folder.path;
                    document.getElementById('edit-overlay').style.display = 'flex';
                }
                
                function saveEdit() {
                    const newName = document.getElementById('edit-name').value.trim();
                    const newPath = document.getElementById('edit-path').value.trim();
                    
                    if (newName && newPath && editingFolderId !== null && manager) {
                        manager.edit_folder(editingFolderId, newName, newPath);
                        setTimeout(loadFolders, 100);
                    }
                    
                    cancelEdit();
                }
                
                function cancelEdit() {
                    document.getElementById('edit-overlay').style.display = 'none';
                    editingFolderId = null;
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