import sys
import json
import psutil
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, QObject
from PyQt5.QtWebChannel import QWebChannel

class SystemMonitor(QObject):
    def __init__(self, html_window):
        super().__init__()
        self.html_window = html_window
    
    @pyqtSlot(result=str)
    def get_system_stats(self):
        cpu_percent = psutil.cpu_percent(interval=0.1)  # Reduced interval for responsiveness
        memory = psutil.virtual_memory()
        ram_percent = memory.percent
        
        return json.dumps({
            'cpu': round(cpu_percent, 1),
            'ram': round(ram_percent, 1)
        })
    
    @pyqtSlot()
    def close_window(self):
        self.html_window.close()
    
    @pyqtSlot(result=str)
    def get_top_cpu_processes(self):
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                proc_info = proc.info
                if proc_info['cpu_percent'] > 0:
                    processes.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage and get top 10
        top_processes = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:10]
        return json.dumps(top_processes)
    
    @pyqtSlot(result=str)
    def get_top_ram_processes(self):
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                proc_info = proc.info
                if proc_info['memory_percent'] > 0:
                    processes.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by RAM usage and get top 10
        top_processes = sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:10]
        return json.dumps(top_processes)

class HTMLWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Monitor")
        self.setGeometry(300, 300, 900, 700)
        
        # Remove window frame and title bar for clean look
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # Create web view and channel
        self.web_view = QWebEngineView()
        self.channel = QWebChannel()
        self.monitor = SystemMonitor(self)
        
        # Register the monitor object with the web channel
        self.channel.registerObject('monitor', self.monitor)
        self.web_view.page().setWebChannel(self.channel)
        
        # Load HTML content
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            <style>
                body {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    color: white;
                    margin: 0;
                    padding: 20px;
                    height: 100vh;
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
                    margin-bottom: 20px;
                }
                .title {
                    font-size: 2em;
                    font-weight: bold;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }
                .close-btn {
                    background: rgba(255,255,255,0.2);
                    border: none;
                    color: white;
                    font-size: 20px;
                    cursor: pointer;
                    padding: 8px 12px;
                    border-radius: 50%;
                    transition: background 0.2s ease;
                    user-select: none;
                    z-index: 1000;
                }
                .close-btn:hover {
                    background: rgba(255,0,0,0.6);
                    transform: scale(1.1);
                }
                .close-btn:active {
                    transform: scale(0.95);
                }
                .stats-container {
                    display: flex;
                    gap: 20px;
                    margin-bottom: 20px;
                }
                .stat-card {
                    flex: 1;
                    background: rgba(255,255,255,0.1);
                    padding: 20px;
                    border-radius: 15px;
                    backdrop-filter: blur(10px);
                    text-align: center;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    border: 2px solid transparent;
                    user-select: none;
                    position: relative;
                }
                .stat-card:hover {
                    background: rgba(255,255,255,0.25);
                    border-color: rgba(255,255,255,0.4);
                    transform: translateY(-3px);
                    box-shadow: 0 8px 25px rgba(0,0,0,0.2);
                }
                .stat-card:active {
                    transform: translateY(-1px);
                }
                .stat-label {
                    font-size: 1.2em;
                    margin-bottom: 10px;
                    opacity: 0.8;
                }
                .stat-value {
                    font-size: 2.5em;
                    font-weight: bold;
                    margin-bottom: 5px;
                }
                .processes-container {
                    flex: 1;
                    background: rgba(255,255,255,0.1);
                    border-radius: 15px;
                    padding: 20px;
                    backdrop-filter: blur(10px);
                    overflow: hidden;
                }
                .processes-title {
                    font-size: 1.5em;
                    margin-bottom: 15px;
                    text-align: center;
                }
                .process-list {
                    max-height: 400px;
                    overflow-y: auto;
                }
                .process-item {
                    display: flex;
                    justify-content: space-between;
                    padding: 8px 0;
                    border-bottom: 1px solid rgba(255,255,255,0.1);
                }
                .process-name {
                    flex: 1;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                }
                .process-usage {
                    font-weight: bold;
                    min-width: 60px;
                    text-align: right;
                }
                .hidden {
                    display: none;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="title">System Monitor</div>
                    <button class="close-btn" onclick="closeWindow()">×</button>
                </div>
                
                <div class="stats-container">
                    <div class="stat-card" onclick="showCpuProcesses()">
                        <div class="stat-label">CPU Usage</div>
                        <div class="stat-value" id="cpu-value">0%</div>
                        <div>Click for details</div>
                    </div>
                    <div class="stat-card" onclick="showRamProcesses()">
                        <div class="stat-label">RAM Usage</div>
                        <div class="stat-value" id="ram-value">0%</div>
                        <div>Click for details</div>
                    </div>
                </div>
                
                <div class="processes-container">
                    <div class="processes-title" id="processes-title">Click CPU or RAM to see top processes</div>
                    <div class="process-list" id="process-list"></div>
                </div>
            </div>
            
            <script>
                let monitor;
                
                new QWebChannel(qt.webChannelTransport, function(channel) {
                    monitor = channel.objects.monitor;
                    updateStats();
                    setInterval(updateStats, 2000); // Update every 2 seconds
                });
                
                function updateStats() {
                    if (monitor) {
                        monitor.get_system_stats(function(result) {
                            const stats = JSON.parse(result);
                            document.getElementById('cpu-value').textContent = stats.cpu + '%';
                            document.getElementById('ram-value').textContent = stats.ram + '%';
                        });
                    }
                }
                
                function closeWindow() {
                    if (monitor) {
                        monitor.close_window();
                    }
                }
                
                function showCpuProcesses() {
                    if (monitor) {
                        monitor.get_top_cpu_processes(function(result) {
                            const processes = JSON.parse(result);
                            displayProcesses(processes, 'Top 10 CPU Usage', 'cpu_percent', '%');
                        });
                    }
                }
                
                function showRamProcesses() {
                    if (monitor) {
                        monitor.get_top_ram_processes(function(result) {
                            const processes = JSON.parse(result);
                            displayProcesses(processes, 'Top 10 RAM Usage', 'memory_percent', '%');
                        });
                    }
                }
                
                function displayProcesses(processes, title, usageKey, unit) {
                    document.getElementById('processes-title').textContent = title;
                    const listElement = document.getElementById('process-list');
                    listElement.innerHTML = '';
                    
                    processes.forEach(proc => {
                        const item = document.createElement('div');
                        item.className = 'process-item';
                        item.innerHTML = `
                            <div class="process-name">${proc.name}</div>
                            <div class="process-usage">${proc[usageKey].toFixed(1)}${unit}</div>
                        `;
                        listElement.appendChild(item);
                    });
                }
            </script>
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