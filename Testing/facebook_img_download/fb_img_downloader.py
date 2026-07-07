import sys
import os
import re
import time
import requests
import json
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                             QGroupBox, QFormLayout, QPlainTextEdit, QFileDialog, 
                             QProgressBar, QSpinBox, QCheckBox, QDialog, QMessageBox, QInputDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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

    def _get_current_image(self, driver):
        """Extract the highest-quality scontent/fbcdn image URL from the current view."""
        selectors = [
            "//div[@role='dialog']//img[@data-visualcompletion='media-vc-image']",
            "//img[@data-visualcompletion='media-vc-image']",
            "//div[@role='dialog']//img[contains(@src,'scontent') or contains(@src,'fbcdn')]",
            "//div[@role='main']//img[contains(@src,'scontent') or contains(@src,'fbcdn')]",
            "//img[contains(@src,'scontent') or contains(@src,'fbcdn')]",
        ]
        
        for selector in selectors:
            elements = driver.find_elements(By.XPATH, selector)
            for img in elements:
                try:
                    # Ignore tiny images (icons, profile thumbnails, trackers)
                    w_val = img.get_attribute("width")
                    h_val = img.get_attribute("height")
                    if w_val and h_val:
                        try:
                            if int(w_val) < 200 or int(h_val) < 200:
                                continue
                        except ValueError:
                            pass

                    # Try srcset first as it contains all available resolutions
                    srcset = img.get_attribute("srcset")
                    if srcset:
                        # srcset format: "url1 w1, url2 w2, ..."
                        parts = srcset.split(",")
                        best_url = None
                        max_w = 0
                        for part in parts:
                            m = re.search(r'(https://\S+)\s+(\d+)w', part)
                            if m:
                                url, w = m.group(1), int(m.group(2))
                                if w > max_w:
                                    max_w = w
                                    best_url = url
                        if best_url:
                            return best_url

                    # Fallback to src
                    src = img.get_attribute("src")
                    if src and ("scontent" in src or "fbcdn" in src):
                        if any(x in src for x in ["/rsrc.php", "emoji", "/cp/", "rsrc="]):
                            continue
                        return src
                except:
                    continue
        return None

    def _upgrade_url_quality(self, url):
        """Attempt to upgrade URL to full size if not already, while keeping auth params."""
        if not url: return url
        # If it's already a high-res _n.jpg or similar, just return it
        if "_n." in url or "_o." in url:
            return url
            
        # Try to replace size suffixes like _s.jpg, _t.jpg with _n.jpg
        upgraded = re.sub(r'_(s|b|t|q|p|o)\.(jpg|jpeg|png|webp)', r'_n.\2', url, flags=re.IGNORECASE)
        
        # DO NOT strip query parameters like oh and oe, they are signatures!
        return upgraded

    def _download_with_cookies(self, url, driver, filepath):
        """Download using the browser's session cookies to bypass 403."""
        session = requests.Session()
        for cookie in driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain', ''))
        headers = {
            "User-Agent": driver.execute_script("return navigator.userAgent;"),
            "Referer": "https://www.facebook.com/",
        }
        resp = session.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
        with open(filepath, 'wb') as f:
            f.write(resp.content)
        return resp.headers.get("content-type", "image/jpeg")

    def run(self):
        count = 0
        try:
            options = Options()
            if self.headless:
                options.add_argument("--headless=new")
                options.add_argument("--disable-gpu")
                options.add_argument("--disable-software-rasterizer")
                options.add_argument("--window-position=-2400,-2400")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

            # Force using Google Chrome by specifying binary location if found in standard paths
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ]
            local_app_data = os.environ.get("LOCALAPPDATA")
            if local_app_data:
                chrome_paths.append(os.path.join(local_app_data, r"Google\Chrome\Application\chrome.exe"))
            user_profile = os.environ.get("USERPROFILE")
            if user_profile:
                chrome_paths.append(os.path.join(user_profile, r"AppData\Local\Google\Chrome\Application\chrome.exe"))

            chrome_binary = None
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_binary = path
                    break

            self.log_signal.emit("Initializing WebDriver...")
            if chrome_binary:
                options.binary_location = chrome_binary
                self.log_signal.emit(f"Using Google Chrome binary at: {chrome_binary}")
            else:
                self.log_signal.emit("Google Chrome binary not found in standard paths, falling back to default Selenium search.")

            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

            self.log_signal.emit(f"Opening URL: {self.url}")
            driver.get(self.url)
            time.sleep(5)

            # Dismiss any login/cookie popups
            for label in ["Dismiss", "Not now", "Decline optional cookies"]:
                for el in driver.find_elements(By.XPATH, f"//div[@aria-label='{label}'] | //button[@aria-label='{label}']"):
                    try:
                        if el.is_displayed():
                            driver.execute_script("arguments[0].click();", el)
                            time.sleep(0.5)
                    except:
                        pass

            # Enter gallery mode if we're on a post page
            if "/photo" not in driver.current_url:
                self.log_signal.emit("Post detected. Entering gallery mode...")
                try:
                    photo_links = driver.find_elements(By.XPATH, "//a[img][(contains(@href, '/photo') or contains(@href, 'fbid=') or contains(@href, '/photos/')) and not(contains(@href, 'login'))]")
                    if not photo_links:
                        photo_links = driver.find_elements(By.XPATH, "//a[img[contains(@src,'scontent') or contains(@src,'fbcdn')] and not(contains(@href, 'login'))]")
                    
                    if photo_links:
                        self.log_signal.emit("Found photo link. Clicking to enter theater/gallery mode...")
                        driver.execute_script("arguments[0].click();", photo_links[0])
                        time.sleep(5)
                    else:
                        self.log_signal.emit("No photo links found by XPath. Trying keyboard (TABx5 + ENTER) fallback...")
                        from selenium.webdriver.common.action_chains import ActionChains
                        for _ in range(5):
                            ActionChains(driver).send_keys(Keys.TAB).perform()
                            time.sleep(0.3)
                        ActionChains(driver).send_keys(Keys.ENTER).perform()
                        time.sleep(0.5)
                        ActionChains(driver).send_keys(Keys.ENTER).perform()
                        time.sleep(5)
                except Exception as e:
                    self.log_signal.emit(f"Gallery entry error: {e}")

            downloaded_urls = set()
            no_new_streak = 0  # consecutive cycles with no new image

            while count < self.max_images and self.is_running:
                try:
                    src = self._get_current_image(driver)

                    if src and src not in downloaded_urls:
                        full_url = self._upgrade_url_quality(src)
                        downloaded_urls.add(src)
                        no_new_streak = 0
                        count += 1
                        self.log_signal.emit(f"[{count}] Downloading full-quality image...")

                        try:
                            filename = f"fb_image_{count:03d}_{int(time.time())}.jpg"
                            filepath = os.path.join(self.output_dir, filename)
                            ct = self._download_with_cookies(full_url, driver, filepath)
                            # Rename with correct extension if needed
                            if "png" in ct:
                                os.rename(filepath, filepath.replace(".jpg", ".png"))
                            elif "webp" in ct:
                                os.rename(filepath, filepath.replace(".jpg", ".webp"))
                            self.progress_signal.emit(int((count / self.max_images) * 100))
                        except Exception as e:
                            self.log_signal.emit(f"Download error: {e}")
                    else:
                        no_new_streak += 1
                        if no_new_streak > 8:
                            self.log_signal.emit("No new images after multiple attempts. End of gallery.")
                            break

                    # Navigate to next image — prefer keyboard Right arrow (most reliable)
                    navigated = False

                    # 1. Try clicking the Next button
                    for label in ["Next photo", "Next Photo", "Next"]:
                        btns = driver.find_elements(By.XPATH,
                            f"//div[@aria-label='{label}'] | //a[@aria-label='{label}'] | //button[@aria-label='{label}']")
                        for btn in btns:
                            try:
                                if btn.is_displayed():
                                    driver.execute_script("arguments[0].click();", btn)
                                    navigated = True
                                    break
                            except:
                                continue
                        if navigated:
                            break

                    # 2. Fallback: send Right arrow key globally via ActionChains
                    if not navigated:
                        try:
                            from selenium.webdriver.common.action_chains import ActionChains
                            ActionChains(driver).send_keys(Keys.ARROW_RIGHT).perform()
                            navigated = True
                        except:
                            pass

                    if not navigated:
                        self.log_signal.emit("Cannot navigate further. End of gallery.")
                        break

                    time.sleep(1.8)  # wait for image transition

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
        
        self.settings_file = os.path.join(os.path.dirname(__file__), 'settings.json')
        self.load_settings()

        self.apply_styles()
        self.init_ui()

    def load_settings(self):
        """Load settings from JSON or set defaults."""
        defaults = {
            "target_url": "https://www.facebook.com/share/p/1QoccunqqZ/",
            "output_dir": os.path.join(os.getcwd(), "downloads"),
            "max_images": 100,
            "headless": False
        }
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
            else:
                self.settings = defaults
        except:
            self.settings = defaults
        
        # Ensure output dir exists
        self.output_dir = self.settings.get("output_dir", defaults["output_dir"])
        if not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir)
            except:
                self.output_dir = defaults["output_dir"]

    def save_settings(self):
        """Collect current UI values and save to JSON."""
        try:
            self.settings["target_url"] = self.url_input.text().strip()
            self.settings["output_dir"] = self.output_dir
            self.settings["max_images"] = self.max_images_spin.value()
            self.settings["headless"] = self.headless_cb.isChecked()
            
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def apply_styles(self):
        self.setStyleSheet(f"""
            QMainWindow, QDialog {{
                background-color: {CP_BG};
            }}
            QLabel, QCheckBox, QGroupBox, QLineEdit, QSpinBox, QPushButton, QPlainTextEdit, QProgressBar, QDialog {{
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
        self.url_input.setText(self.settings.get("target_url", ""))
        self.url_input.textChanged.connect(self.save_settings)
        
        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit(self.output_dir)
        self.dir_input.textChanged.connect(self.on_dir_changed)
        self.browse_btn = QPushButton("BROWSE")
        self.browse_btn.clicked.connect(self.browse_folder)
        self.open_btn = QPushButton("OPEN")
        self.open_btn.clicked.connect(self.open_folder)
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(self.browse_btn)
        dir_layout.addWidget(self.open_btn)

        self.max_images_spin = QSpinBox()
        self.max_images_spin.setRange(1, 5000)
        self.max_images_spin.setValue(self.settings.get("max_images", 100))
        self.max_images_spin.valueChanged.connect(self.save_settings)
        
        self.headless_cb = QCheckBox("Headless Mode (Background)")
        self.headless_cb.setChecked(self.settings.get("headless", False))
        self.headless_cb.toggled.connect(self.save_settings)

        input_layout.addRow("TARGET URL:", self.url_input)
        input_layout.addRow("OUTPUT DIR:", dir_layout)
        input_layout.addRow("MAX IMAGES:", self.max_images_spin)
        input_layout.addRow("EXECUTION:", self.headless_cb)
        input_grp.setLayout(input_layout)
        main_layout.addWidget(input_grp)

        # Controls
        ctrl_layout = QHBoxLayout()
        self.action_btn = QPushButton("▶ START DOWNLOAD")
        self.action_btn.setStyleSheet(f"background-color: {CP_CYAN}; color: black; font-size: 11pt;")
        self.action_btn.clicked.connect(self.toggle_action)
        
        self.restart_btn = QPushButton("↺ RESTART")
        self.restart_btn.clicked.connect(self.restart_app)
        
        self.settings_btn = QPushButton("⚙ SETTINGS")
        self.settings_btn.clicked.connect(self.show_settings)

        ctrl_layout.addWidget(self.action_btn, 3)
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

    def on_dir_changed(self, text):
        self.output_dir = text
        self.save_settings()

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Directory", self.output_dir)
        if folder:
            self.output_dir = folder
            self.dir_input.setText(folder)
            self.save_settings()

    def open_folder(self):
        if os.path.exists(self.output_dir):
            os.startfile(self.output_dir)
        else:
            self.log(f"Directory does not exist: {self.output_dir}")

    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_output.appendPlainText(f"[{timestamp}] {message}")
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())

    def toggle_action(self):
        if hasattr(self, 'dl_thread') and self.dl_thread.isRunning():
            self.log("Stopping extraction process...")
            self.dl_thread.stop()
            self.action_btn.setEnabled(False)
            self.action_btn.setText("⏳ STOPPING...")
        else:
            self.start_download()

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.critical(self, "Error", "Target URL is required.")
            return

        # Prompt for Max Images
        val, ok = QInputDialog.getInt(self, "DOWNLOAD LIMIT", "Enter max images to download:", 
                                     value=self.max_images_spin.value(), min=1, max=5000)
        if not ok:
            return
        
        self.max_images_spin.setValue(val)
        self.save_settings()

        if not os.path.exists(self.output_dir):
            try:
                os.makedirs(self.output_dir)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not create directory: {e}")
                return

        self.action_btn.setText("■ STOP DOWNLOAD")
        self.action_btn.setStyleSheet(f"background-color: {CP_RED}; color: white; font-size: 11pt;")
        self.progress_bar.setValue(0)
        self.log("Initializing extraction process...")

        self.dl_thread = DownloaderThread(
            url, 
            self.output_dir, 
            self.max_images_spin.value(),
            self.headless_cb.isChecked()
        )
        self.dl_thread.log_signal.connect(self.log)
        self.dl_thread.progress_signal.connect(self.progress_bar.setValue)
        self.dl_thread.finished_signal.connect(self.download_finished)
        self.dl_thread.start()

    def download_finished(self, count):
        self.action_btn.setEnabled(True)
        self.action_btn.setText("▶ START DOWNLOAD")
        self.action_btn.setStyleSheet(f"background-color: {CP_CYAN}; color: black; font-size: 11pt;")
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
