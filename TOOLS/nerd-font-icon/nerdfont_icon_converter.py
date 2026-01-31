import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QGroupBox, QFormLayout,
                             QComboBox, QSpinBox, QTextEdit, QFileDialog, QMessageBox,
                             QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QIcon
from PIL import Image, ImageDraw, ImageFont
import json
import matplotlib.font_manager as fm

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

class NerdFontConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NERDFONT ICON CONVERTER")
        self.resize(900, 700)
        
        # Default settings
        self.config = {
            "dimensions": [16, 24, 32, 40, 48, 64, 128, 256],
            "output_format": "png",
            "icon_color": "#FFFFFF",
            "bg_color": "transparent",
            "font_path": "",
            "font_name": "JetBrainsMono Nerd Font"
        }
        
        self.system_fonts = self.get_system_fonts()
        self.load_config()
        self.init_ui()
        self.apply_theme()
        
    def apply_theme(self):
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QListWidget {{
                background-color: {CP_PANEL}; 
                color: {CP_CYAN}; 
                border: 1px solid {CP_DIM}; 
                padding: 4px;
                selection-background-color: {CP_CYAN};
                selection-color: #000000;
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
                border: 1px solid {CP_CYAN};
            }}
            
            QPushButton {{
                background-color: {CP_DIM}; 
                border: 1px solid {CP_DIM}; 
                color: white; 
                padding: 8px 16px; 
                font-weight: bold;
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
                margin-top: 10px; 
                padding-top: 10px; 
                font-weight: bold; 
                color: {CP_YELLOW};
            }}
            QGroupBox::title {{ 
                subcontrol-origin: margin; 
                subcontrol-position: top left; 
                padding: 0 5px; 
            }}
            
            QLabel {{
                color: {CP_TEXT};
            }}
            
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 0px;
                border: none;
            }}
        """)
    
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # Title
        title = QLabel("⚡ NERDFONT ICON CONVERTER ⚡")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"font-size: 16pt; font-weight: bold; color: {CP_YELLOW}; padding: 10px;")
        main_layout.addWidget(title)
        
        # Input Group
        input_group = QGroupBox("ICON INPUT")
        input_layout = QFormLayout()
        
        self.icon_input = QLineEdit()
        self.icon_input.setPlaceholderText("Enter Nerd Font character (e.g., ) or Unicode (U+F015)")
        input_layout.addRow("Icon Character:", self.icon_input)
        
        # Font selection (system fonts dropdown)
        self.font_combo = QComboBox()
        self.font_combo.setEditable(True)
        nerd_fonts = [f for f in self.system_fonts.keys() if 'nerd' in f.lower() or 'nf' in f.lower()]
        all_fonts = list(self.system_fonts.keys())
        
        # Add Nerd Fonts first, then all fonts
        for font in nerd_fonts:
            self.font_combo.addItem(font)
        self.font_combo.insertSeparator(len(nerd_fonts))
        for font in all_fonts:
            if font not in nerd_fonts:
                self.font_combo.addItem(font)
        
        # Set saved font or default
        saved_font = self.config.get("font_name", "JetBrainsMono Nerd Font")
        index = self.font_combo.findText(saved_font)
        if index >= 0:
            self.font_combo.setCurrentIndex(index)
        
        input_layout.addRow("Font Name:", self.font_combo)
        
        # Optional: Custom font file path
        self.font_path_input = QLineEdit(self.config.get("font_path", ""))
        self.font_path_input.setPlaceholderText("Or specify custom .ttf file path (optional)")
        font_browse_btn = QPushButton("BROWSE")
        font_browse_btn.clicked.connect(self.browse_font)
        font_layout = QHBoxLayout()
        font_layout.addWidget(self.font_path_input)
        font_layout.addWidget(font_browse_btn)
        input_layout.addRow("Custom Font:", font_layout)
        
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)
        
        # Settings Group
        settings_group = QGroupBox("CONVERSION SETTINGS")
        settings_layout = QFormLayout()
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["png", "ico", "bmp", "jpg"])
        self.format_combo.setCurrentText(self.config["output_format"])
        settings_layout.addRow("Output Format:", self.format_combo)
        
        self.icon_color_input = QLineEdit(self.config["icon_color"])
        self.icon_color_input.setPlaceholderText("#FFFFFF or transparent")
        settings_layout.addRow("Icon Color:", self.icon_color_input)
        
        self.bg_color_input = QLineEdit(self.config["bg_color"])
        self.bg_color_input.setPlaceholderText("transparent or #000000")
        settings_layout.addRow("Background:", self.bg_color_input)
        
        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)
        
        # Dimensions Group
        dim_group = QGroupBox("OUTPUT DIMENSIONS")
        dim_layout = QVBoxLayout()
        
        dim_info = QLabel("Modify dimensions (one per line, e.g., 16, 32, 64):")
        dim_info.setStyleSheet(f"color: {CP_SUBTEXT}; font-size: 9pt;")
        dim_layout.addWidget(dim_info)
        
        self.dimensions_text = QTextEdit()
        self.dimensions_text.setPlainText("\n".join(map(str, self.config["dimensions"])))
        self.dimensions_text.setMaximumHeight(120)
        dim_layout.addWidget(self.dimensions_text)
        
        dim_group.setLayout(dim_layout)
        main_layout.addWidget(dim_group)
        
        # Output Group
        output_group = QGroupBox("OUTPUT DIRECTORY")
        output_layout = QHBoxLayout()
        
        self.output_path_input = QLineEdit("img")
        self.output_path_input.setPlaceholderText("Output directory path")
        output_browse_btn = QPushButton("BROWSE")
        output_browse_btn.clicked.connect(self.browse_output)
        
        output_layout.addWidget(self.output_path_input)
        output_layout.addWidget(output_browse_btn)
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        
        self.convert_btn = QPushButton("⚡ CONVERT ICON ⚡")
        self.convert_btn.clicked.connect(self.convert_icon)
        self.convert_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CP_GREEN};
                color: black;
                font-size: 12pt;
                padding: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {CP_YELLOW};
            }}
        """)
        
        save_config_btn = QPushButton("SAVE CONFIG")
        save_config_btn.clicked.connect(self.save_config)
        
        btn_layout.addWidget(save_config_btn)
        btn_layout.addWidget(self.convert_btn)
        main_layout.addLayout(btn_layout)
        
        # Status Log
        log_group = QGroupBox("STATUS LOG")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        self.log_text.setStyleSheet(f"color: {CP_GREEN};")
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        self.log("System ready. Load a Nerd Font and enter an icon character.")
    
    def log(self, message):
        self.log_text.append(f">> {message}")
    
    def get_system_fonts(self):
        """Get all system fonts with their paths"""
        fonts = {}
        try:
            for font in fm.fontManager.ttflist:
                font_name = font.name
                if font_name not in fonts:
                    fonts[font_name] = font.fname
        except:
            pass
        return fonts
    
    def browse_font(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Nerd Font File", "", "Font Files (*.ttf *.otf)"
        )
        if file_path:
            self.font_path_input.setText(file_path)
            self.log(f"Font loaded: {Path(file_path).name}")
    
    def browse_output(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_path_input.setText(dir_path)
    
    def parse_dimensions(self):
        text = self.dimensions_text.toPlainText()
        dimensions = []
        for line in text.split('\n'):
            line = line.strip()
            if line.isdigit():
                dimensions.append(int(line))
        return dimensions if dimensions else [64]
    
    def convert_icon(self):
        # Validate inputs
        icon_char = self.icon_input.text().strip()
        
        if not icon_char:
            QMessageBox.warning(self, "Input Error", "Please enter an icon character!")
            return
        
        # Get font path (custom file or system font)
        font_path = self.font_path_input.text().strip()
        if not font_path:
            # Use selected system font
            font_name = self.font_combo.currentText()
            if font_name in self.system_fonts:
                font_path = self.system_fonts[font_name]
            else:
                QMessageBox.warning(self, "Font Error", "Please select a valid font!")
                return
        
        if not Path(font_path).exists():
            QMessageBox.warning(self, "Font Error", f"Font file not found: {font_path}")
            return
        
        # Parse Unicode if needed
        if icon_char.startswith("U+") or icon_char.startswith("u+"):
            try:
                icon_char = chr(int(icon_char[2:], 16))
            except:
                QMessageBox.warning(self, "Unicode Error", "Invalid Unicode format!")
                return
        
        # Get settings
        dimensions = self.parse_dimensions()
        output_format = self.format_combo.currentText()
        icon_color = self.icon_color_input.text().strip()
        bg_color = self.bg_color_input.text().strip()
        output_dir = Path(self.output_path_input.text().strip())
        
        # Create directories
        output_dir.mkdir(parents=True, exist_ok=True)
        batch_dir = output_dir / "all_sizes"
        batch_dir.mkdir(exist_ok=True)
        
        self.log(f"Starting conversion for '{icon_char}'...")
        self.log(f"Dimensions: {dimensions}")
        
        success_count = 0
        
        for size in dimensions:
            try:
                # Create image
                img = Image.new('RGBA', (size, size), (0, 0, 0, 0) if bg_color == "transparent" else bg_color)
                draw = ImageDraw.Draw(img)
                
                # Load font
                font = ImageFont.truetype(font_path, int(size * 0.8))
                
                # Get text bounding box
                bbox = draw.textbbox((0, 0), icon_char, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Center the icon
                x = (size - text_width) // 2 - bbox[0]
                y = (size - text_height) // 2 - bbox[1]
                
                # Draw icon
                fill_color = icon_color if icon_color != "transparent" else "#FFFFFF"
                draw.text((x, y), icon_char, font=font, fill=fill_color)
                
                # Save to both locations
                filename = f"icon_{size}x{size}.{output_format}"
                
                # Root directory
                root_path = output_dir / filename
                img.save(root_path, format=output_format.upper())
                
                # Batch directory
                batch_path = batch_dir / filename
                img.save(batch_path, format=output_format.upper())
                
                success_count += 1
                self.log(f"✓ Generated {size}x{size} → {filename}")
                
            except Exception as e:
                self.log(f"✗ Error at {size}x{size}: {str(e)}")
        
        self.log(f"Conversion complete! {success_count}/{len(dimensions)} icons generated.")
        self.log(f"Output: {output_dir.absolute()}")
        QMessageBox.information(self, "Success", f"Generated {success_count} icons in:\n{output_dir.absolute()}")
    
    def load_config(self):
        config_file = Path("nerdfont_converter_config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    loaded = json.load(f)
                    self.config.update(loaded)
            except:
                pass
    
    def save_config(self):
        self.config["dimensions"] = self.parse_dimensions()
        self.config["output_format"] = self.format_combo.currentText()
        self.config["icon_color"] = self.icon_color_input.text().strip()
        self.config["bg_color"] = self.bg_color_input.text().strip()
        self.config["font_path"] = self.font_path_input.text().strip()
        self.config["font_name"] = self.font_combo.currentText()
        
        with open("nerdfont_converter_config.json", 'w') as f:
            json.dump(self.config, f, indent=2)
        
        self.log("Configuration saved!")
        QMessageBox.information(self, "Saved", "Configuration saved successfully!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NerdFontConverter()
    window.show()
    sys.exit(app.exec())
