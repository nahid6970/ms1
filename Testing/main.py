import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt

class HTMLWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HTML Display")
        self.setGeometry(300, 300, 800, 600)
        
        # Remove window frame and title bar for clean look
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # Create web view
        self.web_view = QWebEngineView()
        
        # Load HTML content
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    margin: 0;
                    padding: 20px;
                    height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    flex-direction: column;
                }
                h1 {
                    font-size: 3em;
                    margin-bottom: 20px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }
                .card {
                    background: rgba(255,255,255,0.1);
                    padding: 30px;
                    border-radius: 15px;
                    backdrop-filter: blur(10px);
                    text-align: center;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                }
                .close-btn {
                    position: absolute;
                    top: 10px;
                    right: 15px;
                    background: rgba(255,255,255,0.2);
                    border: none;
                    color: white;
                    font-size: 20px;
                    cursor: pointer;
                    padding: 5px 10px;
                    border-radius: 50%;
                }
            </style>
        </head>
        <body>
            <button class="close-btn" onclick="window.close()">×</button>
            <div class="card">
                <h1>HTML Window</h1>
                <p>This is an HTML window displayed without browser bars!</p>
                <p>Built with Qt WebEngine - just like YASB Reborn</p>
            </div>
        </body>
        </html>
        """
        
        self.web_view.setHtml(html_content)
        self.setCentralWidget(self.web_view)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Directly show the HTML window
    html_window = HTMLWindow()
    html_window.show()
    
    sys.exit(app.exec_())