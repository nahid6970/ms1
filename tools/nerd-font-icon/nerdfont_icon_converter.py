import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QGroupBox, QFormLayout,
                             QComboBox, QSpinBox, QTextEdit, QFileDialog, QMessageBox,
                             QListWidget, QListWidgetItem, QColorDialog, QCheckBox)
from PyQt6.QtCore import Qt, QSize, QTimer
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
        self.resize(1400, 500)
        
        # Config file path
        self.config_dir = Path(r"C:\@delta\output\nerd-icon")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "nerdfont_converter_config.json"
        
        # Default settings
        self.config = {
            "dimensions": [16, 24, 32, 40, 48, 64, 128, 256],
            "output_format": "png",
            "icon_color": "#FFFFFF",
            "bg_color": "transparent",
            "font_path": "",
            "font_name": "JetBrainsMono Nerd Font",
            "output_path": "img",
            "border_enabled": False,
            "border_color": "#000000",
            "border_thickness": 2,
            "border_radius": 0,
            "last_icon": "",
            "icon_size_ratio": 75,
            "filename_pattern": "icon_{size}x{size}"
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
        
        # Two-column layout
        columns_layout = QHBoxLayout()
        
        # LEFT COLUMN
        left_column = QVBoxLayout()
        
        # Input Group
        input_group = QGroupBox("ICON INPUT")
        input_layout = QFormLayout()
        
        self.icon_input = QLineEdit()
        self.icon_input.setPlaceholderText("Enter Nerd Font character (e.g., ) or Unicode (U+F015)")
        self.icon_input.setText(self.config.get("last_icon", ""))
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
        left_column.addWidget(input_group)
        
        # Settings Group
        settings_group = QGroupBox("CONVERSION SETTINGS")
        settings_layout = QFormLayout()
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["png", "svg", "ico", "bmp", "jpg"])
        self.format_combo.setCurrentText(self.config["output_format"])
        settings_layout.addRow("Output Format:", self.format_combo)
        
        # Icon color with color picker
        icon_color_layout = QHBoxLayout()
        self.icon_color_input = QLineEdit(self.config["icon_color"])
        self.icon_color_input.setPlaceholderText("#FFFFFF or transparent")
        self.icon_color_input.textChanged.connect(lambda: self.update_color_preview(self.icon_color_input, self.icon_color_preview))
        self.icon_color_preview = QLabel("   ")
        self.icon_color_preview.setFixedSize(30, 30)
        self.icon_color_preview.setStyleSheet(f"background-color: {self.config['icon_color']}; border: 1px solid {CP_DIM};")
        icon_color_btn = QPushButton("PICK COLOR")
        icon_color_btn.clicked.connect(lambda: self.pick_color(self.icon_color_input, self.icon_color_preview))
        icon_color_layout.addWidget(self.icon_color_input)
        icon_color_layout.addWidget(self.icon_color_preview)
        icon_color_layout.addWidget(icon_color_btn)
        settings_layout.addRow("Icon Color:", icon_color_layout)
        
        # Background color with color picker
        bg_color_layout = QHBoxLayout()
        self.bg_color_input = QLineEdit(self.config["bg_color"])
        self.bg_color_input.setPlaceholderText("transparent or #000000")
        self.bg_color_input.textChanged.connect(lambda: self.update_color_preview(self.bg_color_input, self.bg_color_preview))
        self.bg_color_preview = QLabel("   ")
        self.bg_color_preview.setFixedSize(30, 30)
        bg_preview_color = self.config["bg_color"] if self.config["bg_color"] != "transparent" else "#00000000"
        self.bg_color_preview.setStyleSheet(f"background-color: {bg_preview_color}; border: 1px solid {CP_DIM};")
        bg_color_btn = QPushButton("PICK COLOR")
        bg_color_btn.clicked.connect(lambda: self.pick_color(self.bg_color_input, self.bg_color_preview))
        bg_color_layout.addWidget(self.bg_color_input)
        bg_color_layout.addWidget(self.bg_color_preview)
        bg_color_layout.addWidget(bg_color_btn)
        settings_layout.addRow("Background:", bg_color_layout)
        
        # Icon size ratio
        self.icon_size_ratio = QSpinBox()
        self.icon_size_ratio.setRange(10, 200)
        self.icon_size_ratio.setValue(self.config.get("icon_size_ratio", 75))
        self.icon_size_ratio.setSuffix("%")
        settings_layout.addRow("Icon Size Ratio:", self.icon_size_ratio)
        
        settings_group.setLayout(settings_layout)
        left_column.addWidget(settings_group)
        
        # Dimensions Group
        dim_group = QGroupBox("OUTPUT DIMENSIONS")
        dim_layout = QVBoxLayout()
        
        self.dimensions_text = QLineEdit()
        self.dimensions_text.setText(", ".join(map(str, self.config["dimensions"])))
        self.dimensions_text.setPlaceholderText("e.g., 16, 32, 64, 128")
        dim_layout.addWidget(self.dimensions_text)
        
        dim_group.setLayout(dim_layout)
        left_column.addWidget(dim_group)
        left_column.addStretch()
        
        # RIGHT COLUMN
        right_column = QVBoxLayout()
        
        # Border Settings Group
        border_group = QGroupBox("BORDER SETTINGS")
        border_layout = QFormLayout()
        
        self.border_enabled = QCheckBox("Enable Border")
        self.border_enabled.setChecked(self.config.get("border_enabled", False))
        border_layout.addRow("", self.border_enabled)
        
        # Border color with picker
        border_color_layout = QHBoxLayout()
        self.border_color_input = QLineEdit(self.config.get("border_color", "#000000"))
        self.border_color_input.setPlaceholderText("#000000")
        self.border_color_input.textChanged.connect(lambda: self.update_color_preview(self.border_color_input, self.border_color_preview))
        self.border_color_preview = QLabel("   ")
        self.border_color_preview.setFixedSize(30, 30)
        self.border_color_preview.setStyleSheet(f"background-color: {self.config.get('border_color', '#000000')}; border: 1px solid {CP_DIM};")
        border_color_btn = QPushButton("PICK COLOR")
        border_color_btn.clicked.connect(lambda: self.pick_color(self.border_color_input, self.border_color_preview))
        border_color_layout.addWidget(self.border_color_input)
        border_color_layout.addWidget(self.border_color_preview)
        border_color_layout.addWidget(border_color_btn)
        border_layout.addRow("Border Color:", border_color_layout)
        
        self.border_thickness = QSpinBox()
        self.border_thickness.setRange(1, 50)
        self.border_thickness.setValue(self.config.get("border_thickness", 2))
        border_layout.addRow("Border Thickness:", self.border_thickness)
        
        self.border_radius = QSpinBox()
        self.border_radius.setRange(0, 500)
        self.border_radius.setValue(self.config.get("border_radius", 0))
        border_layout.addRow("Border Radius:", self.border_radius)
        
        border_group.setLayout(border_layout)
        right_column.addWidget(border_group)
        
        # Output Group
        output_group = QGroupBox("OUTPUT SETTINGS")
        output_layout = QFormLayout()
        
        # Output directory
        output_dir_layout = QHBoxLayout()
        self.output_path_input = QLineEdit(self.config.get("output_path", "img"))
        self.output_path_input.setPlaceholderText("Output directory path")
        output_browse_btn = QPushButton("BROWSE")
        output_browse_btn.clicked.connect(self.browse_output)
        output_dir_layout.addWidget(self.output_path_input)
        output_dir_layout.addWidget(output_browse_btn)
        output_layout.addRow("Output Directory:", output_dir_layout)
        
        # Filename pattern
        self.filename_pattern = QLineEdit(self.config.get("filename_pattern", "icon_{size}x{size}"))
        self.filename_pattern.setPlaceholderText("Use {size} for dimension")
        output_layout.addRow("Filename Pattern:", self.filename_pattern)
        
        output_group.setLayout(output_layout)
        right_column.addWidget(output_group)
        right_column.addStretch()
        
        # Add columns to layout
        columns_layout.addLayout(left_column)
        columns_layout.addLayout(right_column)
        main_layout.addLayout(columns_layout)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        
        save_config_btn = QPushButton("SAVE CONFIG")
        save_config_btn.clicked.connect(self.save_config)
        
        self.convert_btn = QPushButton("⚡ CONVERT ICON")
        self.convert_btn.clicked.connect(self.convert_icon)
        
        btn_layout.addWidget(save_config_btn)
        btn_layout.addWidget(self.convert_btn)
        main_layout.addLayout(btn_layout)
        

    
    def log(self, message):
        pass
    
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
    
    def save_as_svg(self, output_path, icon_char, size, fill_color, bg_color, font_path,
                   border_enabled=False, border_color="#000000", border_thickness=2, border_radius=0, icon_size_ratio=75):
        """Generate SVG file with embedded font"""
        font_size = int(size * (icon_size_ratio / 100))
        
        # Calculate approximate text position (centered)
        x = size // 2
        y = size // 2 + font_size // 3
        
        # Convert font to base64 for embedding
        import base64
        try:
            with open(font_path, 'rb') as f:
                font_data = base64.b64encode(f.read()).decode('utf-8')
            font_family = Path(font_path).stem
            
            # Embedded font style
            font_style = f'''<defs>
    <style type="text/css">
        @font-face {{
            font-family: '{font_family}';
            src: url(data:font/truetype;charset=utf-8;base64,{font_data}) format('truetype');
        }}
    </style>
</defs>'''
        except:
            # Fallback without embedded font
            font_family = "monospace"
            font_style = ""
        
        # Background
        bg_rect = ""
        if bg_color != "transparent":
            if border_radius > 0:
                bg_rect = f'<rect width="{size}" height="{size}" rx="{border_radius}" ry="{border_radius}" fill="{bg_color}"/>'
            else:
                bg_rect = f'<rect width="{size}" height="{size}" fill="{bg_color}"/>'
        
        # Border
        border_rect = ""
        if border_enabled:
            if border_radius > 0:
                border_rect = f'<rect x="{border_thickness/2}" y="{border_thickness/2}" width="{size-border_thickness}" height="{size-border_thickness}" rx="{border_radius}" ry="{border_radius}" fill="none" stroke="{border_color}" stroke-width="{border_thickness}"/>'
            else:
                border_rect = f'<rect x="{border_thickness/2}" y="{border_thickness/2}" width="{size-border_thickness}" height="{size-border_thickness}" fill="none" stroke="{border_color}" stroke-width="{border_thickness}"/>'
        
        # SVG content
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
{font_style}
{bg_rect}
{border_rect}
<text x="{x}" y="{y}" font-family="{font_family}" font-size="{font_size}" fill="{fill_color}" text-anchor="middle" dominant-baseline="middle">{icon_char}</text>
</svg>'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
    
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
    
    def pick_color(self, line_edit, preview_label):
        """Open color picker dialog"""
        current_color = line_edit.text().strip()
        
        # Parse current color if valid
        initial_color = QColor("#FFFFFF")
        if current_color and current_color != "transparent":
            try:
                initial_color = QColor(current_color)
            except:
                pass
        
        color = QColorDialog.getColor(initial_color, self, "Pick Color")
        
        if color.isValid():
            line_edit.setText(color.name())
            preview_label.setStyleSheet(f"background-color: {color.name()}; border: 1px solid {CP_DIM};")
    
    def update_color_preview(self, line_edit, preview_label):
        """Update color preview when text changes"""
        color_text = line_edit.text().strip()
        if color_text == "transparent":
            preview_label.setStyleSheet(f"background-color: #00000000; border: 1px solid {CP_DIM};")
        elif color_text.startswith("#") and len(color_text) in [4, 7, 9]:
            try:
                QColor(color_text)  # Validate color
                preview_label.setStyleSheet(f"background-color: {color_text}; border: 1px solid {CP_DIM};")
            except:
                pass
    
    def parse_dimensions(self):
        text = self.dimensions_text.text()
        dimensions = []
        for item in text.split(','):
            item = item.strip()
            if item.isdigit():
                dimensions.append(int(item))
        return dimensions if dimensions else [64]
    
    def convert_icon(self):
        self.convert_btn.setEnabled(False)
        self.convert_btn.setText("CONVERTING...")
        QApplication.processEvents()
        
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
        bg_color = self.bg_color_input.text().strip() or "transparent"
        output_dir = Path(self.output_path_input.text().strip())
        
        # Border settings
        border_enabled = self.border_enabled.isChecked()
        border_color = self.border_color_input.text().strip()
        border_thickness = self.border_thickness.value()
        border_radius = self.border_radius.value()
        
        # Icon size ratio
        icon_size_ratio = self.icon_size_ratio.value()
        
        # Filename pattern
        filename_pattern = self.filename_pattern.text().strip()
        if not filename_pattern:
            filename_pattern = "icon_{size}x{size}"
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        self.log(f"Starting conversion for '{icon_char}'...")
        self.log(f"Dimensions: {dimensions}")
        
        success_count = 0
        
        for size in dimensions:
            try:
                # Create image with transparent background always (bg will be added later if needed)
                img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                
                # Draw background if no border or square border
                if not border_enabled or (border_enabled and border_radius == 0):
                    if bg_color != "transparent":
                        draw.rectangle([(0, 0), (size-1, size-1)], fill=bg_color)
                
                # Load font with custom size ratio
                font_size = int(size * (icon_size_ratio / 100))
                font = ImageFont.truetype(font_path, font_size)
                
                # Draw icon centered using anchor
                fill_color = icon_color if icon_color != "transparent" else "#FFFFFF"
                draw.text((size // 2, size // 2), icon_char, font=font, fill=fill_color, anchor="mm")
                
                # Add border if enabled
                if border_enabled:
                    if border_radius > 0:
                        # Create a new image with proper rounded corners
                        rounded_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
                        rounded_draw = ImageDraw.Draw(rounded_img)
                        
                        # Draw rounded background only if specified (not transparent)
                        if bg_color and bg_color != "transparent" and bg_color.strip():
                            rounded_draw.rounded_rectangle(
                                [(0, 0), (size-1, size-1)], 
                                radius=border_radius, 
                                fill=bg_color
                            )
                        
                        # Paste the icon on top (with transparency)
                        rounded_img.paste(img, (0, 0), img)
                        
                        # Draw rounded border on top
                        rounded_draw.rounded_rectangle(
                            [(border_thickness//2, border_thickness//2), 
                             (size-1-border_thickness//2, size-1-border_thickness//2)], 
                            radius=border_radius, 
                            outline=border_color, 
                            width=border_thickness
                        )
                        
                        # Create mask for rounded corners to clip everything
                        mask = Image.new('L', (size, size), 0)
                        mask_draw = ImageDraw.Draw(mask)
                        mask_draw.rounded_rectangle([(0, 0), (size-1, size-1)], radius=border_radius, fill=255)
                        
                        # Apply mask to clip to rounded shape
                        rounded_img.putalpha(mask)
                        img = rounded_img
                    else:
                        # Square border
                        draw.rectangle(
                            [(border_thickness//2, border_thickness//2), 
                             (size-1-border_thickness//2, size-1-border_thickness//2)], 
                            outline=border_color, 
                            width=border_thickness
                        )
                
                # Save to output directory with custom pattern
                filename = filename_pattern.replace("{size}", str(size)) + f".{output_format}"
                output_path = output_dir / filename
                
                if output_format == "svg":
                    # Generate SVG
                    self.save_as_svg(output_path, icon_char, size, fill_color, bg_color, font_path,
                                   border_enabled, border_color, border_thickness, border_radius, icon_size_ratio)
                else:
                    img.save(output_path, format=output_format.upper())
                
                success_count += 1
                self.log(f"✓ Generated {size}x{size} → {filename}")
                
            except Exception as e:
                self.log(f"✗ Error at {size}x{size}: {str(e)}")
        
        self.log(f"Conversion complete! {success_count}/{len(dimensions)} icons generated.")
        self.log(f"Output: {output_dir.absolute()}")
        
        # Auto-save output path and last icon
        self.config["output_path"] = str(output_dir)
        self.config["last_icon"] = icon_char
        self.save_config()
        
        # Show success feedback
        self.convert_btn.setStyleSheet(f"background-color: {CP_GREEN}; color: black; font-weight: bold;")
        self.convert_btn.setText("✓ COMPLETE")
        QTimer.singleShot(1000, self.reset_convert_button)
    
    def reset_convert_button(self):
        self.convert_btn.setStyleSheet(f"background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 8px 16px; font-weight: bold;")
        self.convert_btn.setText("⚡ CONVERT ICON")
        self.convert_btn.setEnabled(True)
    
    def load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    self.config.update(loaded)
            except:
                pass
    
    def save_config(self):
        self.config["dimensions"] = self.parse_dimensions()
        self.dimensions_text.setText(", ".join(map(str, self.config["dimensions"])))
        self.config["output_format"] = self.format_combo.currentText()
        self.config["icon_color"] = self.icon_color_input.text().strip()
        self.config["bg_color"] = self.bg_color_input.text().strip()
        self.config["font_path"] = self.font_path_input.text().strip()
        self.config["font_name"] = self.font_combo.currentText()
        self.config["output_path"] = self.output_path_input.text().strip()
        self.config["border_enabled"] = self.border_enabled.isChecked()
        self.config["border_color"] = self.border_color_input.text().strip()
        self.config["border_thickness"] = self.border_thickness.value()
        self.config["border_radius"] = self.border_radius.value()
        self.config["last_icon"] = self.icon_input.text().strip()
        self.config["icon_size_ratio"] = self.icon_size_ratio.value()
        self.config["filename_pattern"] = self.filename_pattern.text().strip()
        
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        self.log("Configuration saved!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NerdFontConverter()
    window.show()
    sys.exit(app.exec())
