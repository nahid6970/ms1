import sys
import os
import re
import time
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
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

    def _upgrade_url_quality(self, url):
        """Strip FB size-limiting params and request the highest quality version."""
        # FB full-res URLs use _n.jpg or no suffix; compressed use _s, _b, _t, etc.
        # Replace size suffix before extension
        url = re.sub(r'_(s|b|t|q|p|o|n)\.(jpg|jpeg|png|webp)', r'_n.\2', url, flags=re.IGNORECASE)
        # Remove width/height query params that cap resolution
        parsed = urlparse(url)
        params = parse_qs(parsed.query, keep_blank_values=True)
        for key in ['_nc_cat', 'ccb', 'efg', '_nc_sid', '_nc_ohc', '_nc_oc',
                    '_nc_zt', '_nc_ht', 'oh', 'oe', '_nc_fb', 'tp']:
            params.pop(key, None)
        new_query = urlencode({k: v[0] for k, v in params.items()})
        return urlunparse(parsed._replace(query=new_query))

    def _get_current_image(self, driver):
        """Extract the highest-quality scontent image URL from the current view."""
        selectors = [
            "//div[@role='dialog']//img[@data-visualcompletion='media-vc-image']",
            "//img[@data-visualcompletion='media-vc-image']",
            "//div[@role='dialog']//img[contains(@src,'scontent')]",
            "//div[@role='main']//img[contains(@src,'scontent')]",
        ]
        best = (0, None)
        for selector in selectors:
            for img in driver.find_elements(By.XPATH, selector):
                try:
                    src = img.get_attribute("src") or ""
                    if "scontent" not in src:
                        continue
                    w = int(img.get_attribute("naturalWidth") or 0)
                    if w > best[0]:
                        best = (w, src)
                except:
                    continue
        return best[1]

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
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

            self.log_signal.emit("Initializing WebDriver...")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

            self.log_signal.emit(f"Opening URL: {self.url}")
            driver.get(self.url)
            time.sleep(5)

            # Dismiss any login/cookie popups
            for label in ["Close", "close", "Dismiss", "Not now", "Decline optional cookies"]:
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
                    photo_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/photo')]")
                    if photo_links:
                        driver.execute_script("arguments[0].click();", photo_links[0])
                        time.sleep(4)
                    else:
                        self.log_signal.emit("No photo links found.")
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

                    # 2. Fallback: send Right arrow key to the active element / body
                    if not navigated:
                        try:
                            active = driver.switch_to.active_element
                            active.send_keys(Keys.ARROW_RIGHT)
                            navigated = True
                        except:
                            try:
                                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_RIGHT)
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
