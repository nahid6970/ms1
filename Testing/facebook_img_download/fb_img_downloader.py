import sys
import os
import time
import requests
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                             QGroupBox, QFormLayout, QPlainTextEdit, QFileDialog, 
                             QProgressBar, QSpinBox, QCheckBox, QDialog, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# CYBERPUNK THEME PALETTE
CP_BG = "#050505"
CP_PANEL = "#111111"
CP_YELLOW = "#FCEE0A"
CP_CYAN = "#00F0FF"
CP_RED = "#FF003C"
CP_GREEN = "#00ff21"
CP_ORANGE = "#ff934b"
CP_DIM = "#3a3a3a"
CP_TEXT = "#E0E0E0"
CP_SUBTEXT = "#808080"

class DownloaderThread(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(int)

    def __init__(self, url, output_dir, max_images, headless):
        super().__init__()
        self.url = url
        self.output_dir = output_dir
        self.max_images = max_images
        self.headless = headless
        self.is_running = True

    def run(self):
        count = 0
        try:
            options = Options()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            self.log_signal.emit("Initializing WebDriver...")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            
            self.log_signal.emit(f"Opening URL: {self.url}")
            driver.get(self.url)
            
            # If it's a share link, it might redirect to a post. 
            # If it's a post link, we might need to click on an image to start the gallery.
            time.sleep(5)
            
            # Check if we are on a photo page or a post page
            if "/photo" not in driver.current_url:
                self.log_signal.emit("Post detected. Attempting to enter gallery mode...")
                # Try to find the first image to click
                try:
                    # Look for links that contain /photo/
                    # We look for the one that likely leads to the main gallery
                    photo_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/photo')]")
                    if photo_links:
                        self.log_signal.emit("Found photo link. Entering...")
                        driver.execute_script("arguments[0].click();", photo_links[0])
                        time.sleep(5) # Wait longer for gallery to load
                    else:
                        self.log_signal.emit("Could not find photo links in the post. Falling back to scroll mode.")
                except Exception as e:
                    self.log_signal.emit(f"Error entering gallery: {e}")

            downloaded_urls = set()
            retry_count = 0
            
            while count < self.max_images and self.is_running:
                try:
                    # Check for login/signup popups and close them
                    try:
                        # FB often uses a close button with aria-label "Close" or "Dismiss"
                        popups = driver.find_elements(By.XPATH, "//div[@aria-label='Close' or @aria-label='close' or @aria-label='Dismiss']")
                        for p in popups:
                            if p.is_displayed():
                                driver.execute_script("arguments[0].click();", p)
                                self.log_signal.emit("Closed a blocking popup.")
                                time.sleep(1)
                    except:
                        pass

                    # Try to find the main image in theater mode
                    # Theatre mode images often have data-visualcompletion="media-vc-image"
                    # Or are the only large image in a role="dialog"
                    selectors = [
                        "//div[@role='dialog']//img[@data-visualcompletion='media-vc-image']",
                        "//img[@data-visualcompletion='media-vc-image']",
                        "//div[@role='dialog']//img",
                        "//div[@role='main']//img",
                        "//img[contains(@class, 'xz74otr')]", 
                    ]
                    
                    current_img_src = None
                    found_any_src = False
                    for selector in selectors:
                        img_elements = driver.find_elements(By.XPATH, selector)
                        for img in img_elements:
                            try:
                                src = img.get_attribute("src")
                                if src and "scontent" in src:
                                    found_any_src = True
                                    if src not in downloaded_urls:
                                        current_img_src = src
                                        break
                            except:
                                continue
                        if current_img_src:
                            break
                    
                    if current_img_src:
                        count += 1
                        downloaded_urls.add(current_img_src)
                        retry_count = 0 # Reset retry on success
                        self.log_signal.emit(f"[{count}] Found image: {current_img_src[:60]}...")
                        
                        # Download image
                        try:
                            filename = f"fb_image_{count:03d}_{int(time.time())}.jpg"
                            filepath = os.path.join(self.output_dir, filename)
                            
                            img_data = requests.get(current_img_src, timeout=15).content
                            with open(filepath, 'wb') as f:
                                f.write(img_data)
                            
                            self.progress_signal.emit(int((count / self.max_images) * 100))
                        except Exception as e:
                            self.log_signal.emit(f"Download failed for image {count}: {e}")
                    else:
                        if found_any_src:
                            self.log_signal.emit("Image already downloaded. Navigating next...")
                        else:
                            self.log_signal.emit("Waiting for image content...")
                            time.sleep(2)
                            retry_count += 1
                            if retry_count > 5:
                                self.log_signal.emit("Stuck? Attempting forced navigation...")

                    # Find "Next" button - prioritize gallery navigation
                    next_found = False
                    next_selectors = [
                        "//div[@aria-label='Next photo']",
                        "//div[@aria-label='Next Photo']",
                        "//div[@aria-label='Next photo']//i", # Sometimes the icon inside
                        "//a[@aria-label='Next photo']",
                        "//div[contains(@aria-label, 'Next')]",
                        "//div[@role='button' and contains(@style, 'right')]",
                        "//div[contains(@class, 'next')]",
                    ]
                    
                    for selector in next_selectors:
                        next_btns = driver.find_elements(By.XPATH, selector)
                        for btn in next_btns:
                            try:
                                if btn.is_displayed():
                                    # Click using JS to bypass potential overlays
                                    driver.execute_script("arguments[0].click();", btn)
                                    next_found = True
                                    # self.log_signal.emit("Navigating to next image...")
                                    time.sleep(2) # Wait for transition
                                    break
                            except:
                                continue
                        if next_found:
                            break
                    
                    if not next_found:
                        if "/photo" in driver.current_url:
                            self.log_signal.emit("End of gallery detected.")
                            break
                        else:
                            # If we are NOT in gallery mode, scroll the feed
                            self.log_signal.emit("Scrolling feed...")
                            driver.execute_script("window.scrollBy(0, 1000);")
                            time.sleep(2)
                            if retry_count > 3:
                                self.log_signal.emit("No more images in feed.")
                                break

                except Exception as e:
                    self.log_signal.emit(f"Navigation error: {e}")
                    break
            
            driver.quit()
            self.log_signal.emit(f"Task completed. Total images downloaded: {count}")
            
        except Exception as e:
            self.log_signal.emit(f"CRITICAL ERROR: {e}")
        
        self.finished_signal.emit(count)

    def stop(self):
        self.is_running = False

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙ SETTINGS")
        self.resize(400, 200)
        self.setStyleSheet(f"background-color: {CP_BG}; color: {CP_TEXT}; font-family: 'Consolas';")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Settings module extensible..."))
        close_btn = QPushButton("CLOSE")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

class FacebookDownloaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CYBER_FB_EXTRACTOR v1.0")
        self.resize(900, 700)
        self.output_dir = os.path.join(os.getcwd(), "downloads")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.apply_styles()
        self.init_ui()

    def apply_styles(self):
        self.setStyleSheet(f"""
            QMainWindow, QDialog {{
                background-color: {CP_BG};
            }}
            QWidget {{
                color: {CP_TEXT};
                font-family: 'Consolas';
                font-size: 10pt;
            }}
            QLineEdit, QSpinBox, QComboBox, QPlainTextEdit {{
                background-color: {CP_PANEL};
                color: {CP_CYAN};
                border: 1px solid {CP_DIM};
                padding: 6px;
                selection-background-color: {CP_CYAN};
                selection-color: #000000;
            }}
            QLineEdit:focus, QPlainTextEdit:focus, QSpinBox:focus {{
                border: 1px solid {CP_CYAN};
            }}
            QPushButton {{
                background-color: {CP_DIM};
                border: 1px solid {CP_DIM};
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 0px;
            }}
            QPushButton:hover {{
                background-color: #2a2a2a;
                border: 1px solid {CP_YELLOW};
                color: {CP_YELLOW};
            }}
            QPushButton:pressed {{
                background-color: {CP_YELLOW};
                color: black;
            }}
            QGroupBox {{
                border: 1px solid {CP_DIM};
                margin-top: 15px;
                padding-top: 15px;
                font-weight: bold;
                color: {CP_YELLOW};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }}
            QProgressBar {{
                border: 1px solid {CP_DIM};
                text-align: center;
                background-color: {CP_PANEL};
                color: {CP_TEXT};
            }}
            QProgressBar::chunk {{
                background-color: {CP_CYAN};
            }}
            QScrollBar:vertical {{
                background: {CP_BG};
                width: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {CP_CYAN};
                min-height: 20px;
                border-radius: 5px;
            }}
            QCheckBox {{
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {CP_DIM};
                background: {CP_PANEL};
            }}
            QCheckBox::indicator:checked {{
                background: {CP_YELLOW};
                border-color: {CP_YELLOW};
            }}
        """)

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Header
        header = QLabel("SYSTEM :: FACEBOOK_IMAGE_DOWNLOADER")
        header.setStyleSheet(f"color: {CP_CYAN}; font-size: 14pt; font-weight: bold; border-bottom: 2px solid {CP_CYAN}; padding-bottom: 5px;")
        main_layout.addWidget(header)

        # Input Group
        input_grp = QGroupBox("CORE PARAMETERS")
        input_layout = QFormLayout()
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.facebook.com/share/p/...")
        self.url_input.setText("https://www.facebook.com/share/p/1QoccunqqZ/")
        
        dir_layout = QHBoxLayout()
        self.dir_label = QLineEdit(self.output_dir)
        self.dir_label.setReadOnly(True)
        self.browse_btn = QPushButton("BROWSE")
        self.browse_btn.clicked.connect(self.browse_folder)
        dir_layout.addWidget(self.dir_label)
        dir_layout.addWidget(self.browse_btn)

        self.max_images_spin = QSpinBox()
        self.max_images_spin.setRange(1, 1000)
        self.max_images_spin.setValue(100)
        
        self.headless_cb = QCheckBox("Headless Mode (Background)")
        self.headless_cb.setChecked(False)

        input_layout.addRow("TARGET URL:", self.url_input)
        input_layout.addRow("OUTPUT DIR:", dir_layout)
        input_layout.addRow("MAX IMAGES:", self.max_images_spin)
        input_layout.addRow("EXECUTION:", self.headless_cb)
        input_grp.setLayout(input_layout)
        main_layout.addWidget(input_grp)

        # Controls
        ctrl_layout = QHBoxLayout()
        self.start_btn = QPushButton("▶ START DOWNLOAD")
        self.start_btn.setStyleSheet(f"background-color: {CP_CYAN}; color: black; font-size: 11pt;")
        self.start_btn.clicked.connect(self.start_download)
        
        self.stop_btn = QPushButton("■ STOP")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet(f"background-color: {CP_RED}; color: white;")
        self.stop_btn.clicked.connect(self.stop_download)
        
        self.restart_btn = QPushButton("↺ RESTART")
        self.restart_btn.clicked.connect(self.restart_app)
        
        self.settings_btn = QPushButton("⚙ SETTINGS")
        self.settings_btn.clicked.connect(self.show_settings)

        ctrl_layout.addWidget(self.start_btn, 2)
        ctrl_layout.addWidget(self.stop_btn, 1)
        ctrl_layout.addWidget(self.restart_btn, 1)
        ctrl_layout.addWidget(self.settings_btn, 1)
        main_layout.addLayout(ctrl_layout)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        # Logs
        log_grp = QGroupBox("SYSTEM LOG")
        log_layout = QVBoxLayout()
        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet(f"background-color: #000000; color: {CP_GREEN}; border: 1px solid {CP_DIM};")
        log_layout.addWidget(self.log_output)
        log_grp.setLayout(log_layout)
        main_layout.addWidget(log_grp)

        # Footer
        footer = QLabel("READY TO INITIALIZE...")
        footer.setStyleSheet(f"color: {CP_SUBTEXT}; font-style: italic;")
        self.footer = footer
        main_layout.addWidget(footer)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Directory", self.output_dir)
        if folder:
            self.output_dir = folder
            self.dir_label.setText(folder)

    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_output.appendPlainText(f"[{timestamp}] {message}")
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.critical(self, "Error", "Target URL is required.")
            return

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.start_btn.setText("⏳ RUNNING...")
        self.progress_bar.setValue(0)
        self.log("Initializing extraction process...")

        self.thread = DownloaderThread(
            url, 
            self.output_dir, 
            self.max_images_spin.value(),
            self.headless_cb.isChecked()
        )
        self.thread.log_signal.connect(self.log)
        self.thread.progress_signal.connect(self.progress_bar.setValue)
        self.thread.finished_signal.connect(self.download_finished)
        self.thread.start()

    def stop_download(self):
        if hasattr(self, 'thread') and self.thread.isRunning():
            self.log("Stopping extraction process...")
            self.thread.stop()
            self.stop_btn.setEnabled(False)

    def download_finished(self, count):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.start_btn.setText("▶ START DOWNLOAD")
        self.log(f"Process ended. {count} images saved to {self.output_dir}")
        QMessageBox.information(self, "Finished", f"Successfully downloaded {count} images.")

    def restart_app(self):
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def show_settings(self):
        diag = SettingsDialog(self)
        diag.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FacebookDownloaderApp()
    window.show()
    sys.exit(app.exec())
