import sys
import os
import json
import subprocess
import shutil
import psutil
from functools import partial
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QScrollArea, 
                             QFrame, QMessageBox, QGridLayout, QSizePolicy,
                             QProgressBar, QDialog, QLineEdit, QComboBox, 
                             QCheckBox, QColorDialog, QMenu, QTextEdit, QFormLayout,
                             QGroupBox, QSpinBox, QFileDialog, QFontComboBox, QPlainTextEdit,
                             QRadioButton, QButtonGroup, QSplitter)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint, QMimeData
from PyQt6.QtGui import QFont, QCursor, QColor, QDesktopServices, QAction, QIcon, QPainter, QBrush, QPixmap, QDrag
from PyQt6.QtCore import QUrl
import ctypes

# -----------------------------------------------------------------------------
# CYBERPUNK THEME PALETTE
# -----------------------------------------------------------------------------
CP_BG = "#050505"           # Main Background
CP_PANEL = "#111111"        # Panel Background
CP_YELLOW = "#FCEE0A"       # Cyber Yellow
CP_CYAN = "#00F0FF"         # Neon Cyan
CP_RED = "#FF003C"          # Neon Red
CP_DIM = "#3a3a3a"          # Dimmed/Inactive
CP_TEXT = "#E0E0E0"         # Main Text
CP_SUBTEXT = "#808080"      # Sub Text
CP_GREEN = "#00ff21"        # Success Green
CP_ORANGE = "#ff934b"       # Warning Orange

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "script_launcher_config.json")

# -----------------------------------------------------------------------------
# WIDGETS
# -----------------------------------------------------------------------------

class CyberButton(QPushButton):
    def __init__(self, text, parent=None, script_data=None, config=None):
        # Convert <br> variants to \n for multi-line support
        display_text = text.replace("<br>", "\n").replace("<br/>", "\n").replace("<BR>", "\n")
        super().__init__(display_text, parent)
        self.script = script_data or {}
        self.config = config or {}
        self.is_folder = (self.script.get("type") == "folder")
        
        # Cursor
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Dimensions
        w = self.script.get("width", 0)
        h = self.script.get("height", 0)
        if w > 0: self.setFixedWidth(w)
        if h > 0: self.setFixedHeight(h)
        else: self.setMinimumHeight(45)


        # Enable Right Click
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        self.update_style()
        self.drag_start_pos = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event) # Allow standard behavior
        if not (event.buttons() & Qt.MouseButton.LeftButton): return
        if (event.pos() - self.drag_start_pos).manhattanLength() < QApplication.startDragDistance(): return
        
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(self.script.get("name", ""))
        # We store the object pointer for internal transfer
        mime.setData("application/x-script-item", b"")
        drag.setMimeData(mime)
        
        # Pixmap for drag feedback
        pix = self.grab()
        drag.setPixmap(pix)
        drag.setHotSpot(event.pos())
        drag.exec(Qt.DropAction.MoveAction)

    def update_style(self):
        # Defaults
        # Folders -> Yellow (Explorer-like)
        # Scripts -> White
        
        # Use config defaults
        def_sbg = self.config.get("def_script_bg", "#FFFFFF")
        def_sfg = self.config.get("def_script_fg", "#000000")
        def_shbg = self.config.get("def_script_hbg", CP_BG)
        def_shfg = self.config.get("def_script_hfg", def_sbg)

        def_fbg = self.config.get("def_folder_bg", CP_YELLOW)
        def_ffg = self.config.get("def_folder_fg", "#000000")
        def_fhbg = self.config.get("def_folder_hbg", CP_BG)
        def_fhfg = self.config.get("def_folder_hfg", def_fbg)

        if self.is_folder:
            default_color = def_fbg
            default_text_color = def_ffg
            default_hover_bg = def_fhbg
            default_hover_fg = def_fhfg
        else:
            default_color = def_sbg
            default_text_color = def_sfg
            default_hover_bg = def_shbg
            default_hover_fg = def_shfg
        
        # Extract properties
        color = self.script.get("color", default_color)
        text_color = self.script.get("text_color", default_text_color)
        hover_bg = self.script.get("hover_color", default_hover_bg)
        hover_fg = self.script.get("hover_text_color", default_hover_fg)
        
        border_width = self.script.get("border_width", 1 if self.is_folder else 0)
        border_color = self.script.get("border_color", color)
        radius = self.script.get("corner_radius", 0)
        
        # Font
        font_family = self.script.get("font_family", "Consolas")
        font_size = self.script.get("font_size", 10)
        is_bold = self.script.get("is_bold", True)
        is_italic = self.script.get("is_italic", False)
        
        f = QFont(font_family, font_size)
        f.setBold(is_bold)
        f.setItalic(is_italic)
        self.setFont(f)

        # Base Style
        bg_normal = color
        fg_normal = text_color
        
        # Override for folders is NOT needed anymore since we want them filled
        # if self.is_folder:
        #    bg_normal = CP_PANEL
        #    fg_normal = color
            
        # Hover Style defaults (swap)
        bg_hover = hover_bg
        fg_hover = hover_fg

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_normal};
                color: {fg_normal};
                border: {border_width}px solid {border_color};
                padding: 10px;
                border-radius: {radius}px;
            }}
            QPushButton:hover {{
                background-color: {bg_hover};
                color: {fg_hover};
                border: {border_width}px solid {border_color};
            }}
        """)

class StatWidget(QFrame):
    def __init__(self, label, color, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"background-color: {CP_PANEL}; border: 1px solid {CP_DIM};")
        self.setFixedWidth(140)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        lbl = QLabel(label)
        lbl.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {CP_SUBTEXT};")
        layout.addWidget(lbl)
        
        self.lbl_val = QLabel("0%")
        self.lbl_val.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        self.lbl_val.setStyleSheet(f"color: {color};")
        self.lbl_val.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.lbl_val)
        
        self.bar = QProgressBar()
        self.bar.setFixedHeight(4)
        self.bar.setTextVisible(False)
        self.bar.setStyleSheet(f"QProgressBar {{ background: {CP_DIM}; border: none; }} QProgressBar::chunk {{ background: {color}; }}")
        layout.addWidget(self.bar)

    def set_value(self, val):
        self.bar.setValue(int(val))
        self.lbl_val.setText(f"{int(val)}%")

# -----------------------------------------------------------------------------
# SELECTION DIALOG
# -----------------------------------------------------------------------------
# FULL EDIT DIALOG
# -----------------------------------------------------------------------------
class EditDialog(QDialog):
    def __init__(self, script_data, parent=None):
        super().__init__(parent)
        self.script = script_data
        self.setWindowTitle(f"EDIT // {self.script.get('name', 'UNKNOWN')}")
        self.resize(1150, 750)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {CP_BG}; }}
            QWidget {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 10pt; }}
            QGroupBox {{ border: 1px solid {CP_DIM}; margin-top: 10px; padding-top: 10px; font-weight: bold; color: {CP_YELLOW}; }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }}
            QLineEdit, QSpinBox, QFontComboBox, QComboBox, QPlainTextEdit {{
                background-color: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 4px; selection-background-color: {CP_CYAN}; selection-color: black;
            }}
            QLineEdit:focus, QPlainTextEdit:focus, QSpinBox:focus {{ border: 1px solid {CP_CYAN}; }}
            QSpinBox::up-button, QSpinBox::down-button {{ width: 0px; border: none; }}
            QPushButton {{ background-color: {CP_DIM}; border: 1px solid {CP_DIM}; color: white; padding: 6px 12px; }}
            QPushButton:hover {{ background-color: #2a2a2a; border: 1px solid {CP_YELLOW}; }}
            QCheckBox {{ spacing: 8px; }}
            QCheckBox::indicator {{ width: 14px; height: 14px; border: 1px solid {CP_DIM}; background: {CP_PANEL}; }}
            QCheckBox::indicator:checked {{ background: {CP_YELLOW}; border-color: {CP_YELLOW}; }}
        """)
        
        vbox = QVBoxLayout(self)
        
        # Content HBox
        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        
        # === LEFT PANEL ===
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 1. Identity
        grp_basic = QGroupBox("IDENTITY")
        l_basic = QFormLayout()
        self.inp_name = QLineEdit(self.script.get("name", ""))
        l_basic.addRow("Name:", self.inp_name)
        if self.script.get("type") != "folder":
            path_box = QHBoxLayout()
            self.inp_path = QLineEdit(self.script.get("path", ""))
            btn_browse = QPushButton("...")
            btn_browse.setFixedWidth(30)
            btn_browse.clicked.connect(self.browse_path)
            path_box.addWidget(self.inp_path)
            path_box.addWidget(btn_browse)
            l_basic.addRow("Path:", path_box)
        grp_basic.setLayout(l_basic)
        left_layout.addWidget(grp_basic)
        
        # 2. Execution
        if self.script.get("type") != "folder":
            grp_exec = QGroupBox("BEHAVIOR")
            l_exec = QVBoxLayout()
            self.chk_hide = QCheckBox("Hide Term")
            self.chk_hide.setChecked(self.script.get("hide_terminal", False))
            self.chk_keep = QCheckBox("Keep Open")
            self.chk_keep.setChecked(self.script.get("keep_open", False))
            self.chk_kill = QCheckBox("Kill Launch")
            self.chk_kill.setChecked(self.script.get("kill_window", False))
            self.chk_new_term = QCheckBox("New Terminal")
            self.chk_new_term.setChecked(self.script.get("new_terminal", False))
            self.chk_admin = QCheckBox("Run as Admin")
            self.chk_admin.setChecked(self.script.get("run_admin", False))

            row1 = QHBoxLayout()
            row1.addWidget(self.chk_hide)
            row1.addWidget(self.chk_keep)
            row1.addWidget(self.chk_kill)
            row1.addWidget(self.chk_new_term)
            
            row2 = QHBoxLayout()
            row2.addWidget(self.chk_admin)
            row2.addStretch() 
            
            l_exec.addLayout(row1)
            l_exec.addLayout(row2)
            l_sc = QFormLayout()
            self.inp_ctrl_left = QLineEdit(self.script.get("ctrl_left_cmd", ""))
            self.inp_ctrl_right = QLineEdit(self.script.get("ctrl_right_cmd", ""))
            l_sc.addRow("Ctrl+Left:", self.inp_ctrl_left)
            l_sc.addRow("Ctrl+Right:", self.inp_ctrl_right)
            l_exec.addLayout(l_sc)
            grp_exec.setLayout(l_exec)
            left_layout.addWidget(grp_exec)
            
        # 3. Typography
        grp_typo = QGroupBox("TYPOGRAPHY")
        l_typo = QGridLayout()
        self.cmb_font = QFontComboBox()
        self.cmb_font.setCurrentFont(QFont(self.script.get("font_family", "Consolas")))
        self.cmb_font.setEditable(False)
        self.cmb_font.setFontFilters(QFontComboBox.FontFilter.ScalableFonts)
        self.cmb_font.setMaximumWidth(200)
        l_typo.addWidget(QLabel("Font:"), 0, 0)
        l_typo.addWidget(self.cmb_font, 0, 1, 1, 3)
        l_typo.addWidget(QLabel("Size:"), 1, 0)
        self.spn_size = QSpinBox()
        self.spn_size.setRange(6, 72)
        
        # Pull global default if item has no font_size
        default_fs = 10
        if parent and hasattr(parent, "config"):
            default_fs = parent.config.get("default_font_size", 10)
            
        self.spn_size.setValue(self.script.get("font_size", default_fs))
        l_typo.addWidget(self.spn_size, 1, 1)
        self.chk_bold = QCheckBox("Bold")
        self.chk_bold.setChecked(self.script.get("is_bold", True))
        l_typo.addWidget(self.chk_bold, 1, 2)
        self.chk_italic = QCheckBox("Italic")
        self.chk_italic.setChecked(self.script.get("is_italic", False))
        l_typo.addWidget(self.chk_italic, 1, 3)
        grp_typo.setLayout(l_typo)
        left_layout.addWidget(grp_typo)
        
        # 4. Colors
        grp_colors = QGroupBox("COLORS")
        l_colors = QGridLayout()
        self.btn_col_bg = self.create_color_btn("BG Color", "color")
        self.btn_col_fg = self.create_color_btn("Text Color", "text_color")
        self.btn_col_hbg = self.create_color_btn("Hover BG", "hover_color")
        self.btn_col_hfg = self.create_color_btn("Hover Text", "hover_text_color")
        self.btn_col_brd = self.create_color_btn("Border", "border_color")
        l_colors.addWidget(self.btn_col_bg, 0, 0)
        l_colors.addWidget(self.btn_col_fg, 0, 1)
        l_colors.addWidget(self.btn_col_hbg, 1, 0)
        l_colors.addWidget(self.btn_col_hfg, 1, 1)
        l_colors.addWidget(self.btn_col_brd, 2, 0, 1, 2)
        grp_colors.setLayout(l_colors)
        left_layout.addWidget(grp_colors)
        
        # 5. Layout
        grp_layout = QGroupBox("GRID LAYOUT")
        l_lay = QGridLayout()
        self.spn_cspan = QSpinBox(); self.spn_cspan.setRange(1, 10); self.spn_cspan.setValue(self.script.get("col_span", 1))
        self.spn_rspan = QSpinBox(); self.spn_rspan.setRange(1, 10); self.spn_rspan.setValue(self.script.get("row_span", 1))
        self.spn_width = QSpinBox(); self.spn_width.setRange(0, 9999); self.spn_width.setValue(self.script.get("width", 0))
        self.spn_height = QSpinBox(); self.spn_height.setRange(0, 9999); self.spn_height.setValue(self.script.get("height", 0))
        self.spn_radius = QSpinBox(); self.spn_radius.setRange(0, 50); self.spn_radius.setValue(self.script.get("corner_radius", 0))
        self.spn_border = QSpinBox(); self.spn_border.setRange(0, 10); self.spn_border.setValue(self.script.get("border_width", 0))
        
        l_lay.addWidget(QLabel("Col Span:"), 0, 0); l_lay.addWidget(self.spn_cspan, 0, 1)
        l_lay.addWidget(QLabel("Row Span:"), 0, 2); l_lay.addWidget(self.spn_rspan, 0, 3)
        l_lay.addWidget(QLabel("Width:"), 1, 0); l_lay.addWidget(self.spn_width, 1, 1)
        l_lay.addWidget(QLabel("Height:"), 1, 2); l_lay.addWidget(self.spn_height, 1, 3)
        l_lay.addWidget(QLabel("Radius:"), 2, 0); l_lay.addWidget(self.spn_radius, 2, 1)
        l_lay.addWidget(QLabel("Border:"), 2, 2); l_lay.addWidget(self.spn_border, 2, 3)
        grp_layout.setLayout(l_lay)
        left_layout.addWidget(grp_layout)
        
        # 6. Folder Specific View Settings
        if self.script.get("type") == "folder":
            grp_fview = QGroupBox("FOLDER VIEW SETTINGS")
            l_fv = QGridLayout()
            
            l_fv.addWidget(QLabel("Inner Columns:"), 0, 0)
            self.spn_inner_cols = QSpinBox(); self.spn_inner_cols.setRange(0, 20); 
            self.spn_inner_cols.setValue(self.script.get("grid_columns", 0)) # 0 means default
            self.spn_inner_cols.setToolTip("0 = Inherit Global")
            l_fv.addWidget(self.spn_inner_cols, 0, 1)
            
            l_fv.addWidget(QLabel("Inner Row Height:"), 0, 2)
            self.spn_inner_h = QSpinBox(); self.spn_inner_h.setRange(0, 9999); 
            self.spn_inner_h.setValue(self.script.get("grid_btn_height", 0)) # 0 means default
            self.spn_inner_h.setToolTip("0 = Inherit Global")
            l_fv.addWidget(self.spn_inner_h, 0, 3)
            
            grp_fview.setLayout(l_fv)
            left_layout.addWidget(grp_fview)
        
        left_layout.addStretch()
        left_widget.setLayout(left_layout)
        scroll.setWidget(left_widget)
        hbox.addWidget(scroll, stretch=4) # 40% split
        
        # === RIGHT PANEL ===
        if self.script.get("type") != "folder":
            right_grp = QGroupBox("INLINE SCRIPT EDITOR")
            r_lay = QVBoxLayout()
            
            # Switch
            mode_box = QHBoxLayout()
            self.grp_mode = QButtonGroup(self)
            self.rb_file = QRadioButton("Target File")
            self.rb_inline = QRadioButton("Inline Script")
            self.grp_mode.addButton(self.rb_file); self.grp_mode.addButton(self.rb_inline)
            mode_box.addWidget(self.rb_file); mode_box.addWidget(self.rb_inline)
            if self.script.get("use_inline"): self.rb_inline.setChecked(True)
            else: self.rb_file.setChecked(True)
            r_lay.addLayout(mode_box)
            
            # Interpreter
            r_lay.addWidget(QLabel("Interpreter:"))
            self.cmb_type = QComboBox()
            self.cmb_type.addItems(["cmd", "powershell", "pwsh"])
            self.cmb_type.setCurrentText(self.script.get("inline_type", "cmd"))
            r_lay.addWidget(self.cmb_type)
            
            # Editor
            r_lay.addWidget(QLabel("Code:"))
            self.txt_inline = QPlainTextEdit()
            self.txt_inline.setPlainText(self.script.get("inline_script", ""))
            self.txt_inline.setFont(QFont("Consolas", 10))
            r_lay.addWidget(self.txt_inline)
            
            right_grp.setLayout(r_lay)
            hbox.addWidget(right_grp, stretch=6) # 60% split
            
        # === BOTTOM BUTTONS ===
        btn_layout = QHBoxLayout()
        
        btn_reset = QPushButton("RESET")
        btn_reset.setStyleSheet(f"background-color: {CP_DIM}; color: white; padding: 10px;")
        btn_reset.clicked.connect(self.reset_styles)
        
        btn_random = QPushButton("RANDOM")
        btn_random.setStyleSheet(f"background-color: {CP_CYAN}; color: black; padding: 10px;")
        btn_random.clicked.connect(self.randomize_colors)
        
        btn_save = QPushButton("SAVE CHANGES"); 
        btn_save.setStyleSheet(f"background-color: {CP_YELLOW}; color: black; font-weight: bold; padding: 10px;")
        btn_save.clicked.connect(self.save)
        btn_cancel = QPushButton("CANCEL")
        btn_cancel.setStyleSheet(f"background-color: {CP_RED}; color: white; padding: 10px;")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_reset)
        btn_layout.addWidget(btn_random)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        vbox.addLayout(btn_layout)

    def reset_styles(self):
        # Determine defaults
        is_folder = (self.script.get("type") == "folder")
        def_bg = CP_YELLOW if is_folder else "#FFFFFF"
        def_fg = "#000000"
        
        parent = self.parent()
        def_font = "Consolas"
        def_fs = 10
        def_bold = True
        def_italic = False
        if parent and hasattr(parent, "config"):
            def_font = parent.config.get("default_font_family", "Consolas")
            def_fs = parent.config.get("default_font_size", 10)
            def_bold = parent.config.get("default_is_bold", True)
            def_italic = parent.config.get("default_is_italic", False)

        # Reset Typography
        self.cmb_font.setCurrentFont(QFont(def_font))
        self.spn_size.setValue(def_fs)
        self.chk_bold.setChecked(def_bold)
        self.chk_italic.setChecked(def_italic)

        # Reset Colors
        self.script.pop("color", None)
        self.script.pop("text_color", None)
        self.script.pop("hover_color", None)
        self.script.pop("hover_text_color", None)
        self.script.pop("border_color", None)

        self.set_btn_color(self.btn_col_bg, def_bg)
        self.set_btn_color(self.btn_col_fg, def_fg)
        self.set_btn_color(self.btn_col_hbg, CP_BG)
        self.set_btn_color(self.btn_col_hfg, def_bg)
        self.set_btn_color(self.btn_col_brd, def_bg)

        # Reset Layout/Styling Metrics
        self.spn_cspan.setValue(1)
        self.spn_rspan.setValue(1)
        self.spn_width.setValue(0)
        self.spn_height.setValue(0)
        self.spn_radius.setValue(0)
        self.spn_border.setValue(1 if is_folder else 0)

        if is_folder:
            self.spn_inner_cols.setValue(0)
            self.spn_inner_h.setValue(0)

    def randomize_colors(self):
        import random
        
        def rand_color():
            return "#{:06x}".format(random.randint(0, 0xFFFFFF))
        
        def contrasting_text(bg_hex):
            # Calculate luminance and return black or white
            bg = bg_hex.lstrip('#')
            r, g, b = int(bg[0:2], 16), int(bg[2:4], 16), int(bg[4:6], 16)
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            return "#000000" if luminance > 0.5 else "#FFFFFF"
        
        # Generate random colors
        bg_color = rand_color()
        text_color = contrasting_text(bg_color)
        hover_bg = rand_color()
        hover_text = contrasting_text(hover_bg)
        border_color = rand_color()
        border_width = random.randint(1, 3)
        
        # Apply to script
        self.script["color"] = bg_color
        self.script["text_color"] = text_color
        self.script["hover_color"] = hover_bg
        self.script["hover_text_color"] = hover_text
        self.script["border_color"] = border_color
        
        # Update UI
        self.set_btn_color(self.btn_col_bg, bg_color)
        self.set_btn_color(self.btn_col_fg, text_color)
        self.set_btn_color(self.btn_col_hbg, hover_bg)
        self.set_btn_color(self.btn_col_hfg, hover_text)
        self.set_btn_color(self.btn_col_brd, border_color)
        self.spn_border.setValue(border_width)

    def create_color_btn(self, label, key):
        # Determine effective default based on key and type, matching CyberButton logic
        is_folder = (self.script.get("type") == "folder")
        default_val = CP_BG
        
        # 1. Main Color
        if key == "color":
            default_val = CP_YELLOW if is_folder else "#FFFFFF"
            
        # 2. Text Color
        elif key == "text_color":
            default_val = "#000000"
            
        # 3. Hover Color
        elif key == "hover_color":
            default_val = CP_BG
            
        # 4. Hover Text
        elif key == "hover_text_color":
            # This depends on the main color
            default_val = self.script.get("color", CP_YELLOW if is_folder else "#FFFFFF")
            
        # 5. Border Color
        elif key == "border_color":
            default_val = self.script.get("color", CP_YELLOW if is_folder else "#FFFFFF")

        c = self.script.get(key)
        if not c: c = default_val
        
        btn = QPushButton(label)
        self.set_btn_color(btn, c)
        btn.clicked.connect(lambda: self.pick_color(btn, key))
        return btn

    def set_btn_color(self, btn, color_str):
        lc = QColor(color_str).lightness()
        btn.setStyleSheet(f"background-color: {color_str}; color: {'black' if lc > 128 else 'white'}; border: 1px solid {CP_DIM};")

    def pick_color(self, btn, key):
        curr = self.script.get(key) or "#000000"
        c = QColorDialog.getColor(QColor(curr), self)
        if c.isValid():
            h = c.name()
            self.script[key] = h
            self.set_btn_color(btn, h)

    def browse_path(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select Executable")
        if f: self.inp_path.setText(f)

    def save(self):
        self.script["name"] = self.inp_name.text()
        
        if self.script.get("type") != "folder":
            self.script["path"] = self.inp_path.text()
            self.script["hide_terminal"] = self.chk_hide.isChecked()
            self.script["keep_open"] = self.chk_keep.isChecked()
            self.script["kill_window"] = self.chk_kill.isChecked()
            self.script["new_terminal"] = self.chk_new_term.isChecked()
            self.script["run_admin"] = self.chk_admin.isChecked()
            self.script["ctrl_left_cmd"] = self.inp_ctrl_left.text()
            self.script["ctrl_right_cmd"] = self.inp_ctrl_right.text()
            self.script["use_inline"] = self.rb_inline.isChecked()
            self.script["inline_type"] = self.cmb_type.currentText()
            self.script["inline_script"] = self.txt_inline.toPlainText()
            
        self.script["font_family"] = self.cmb_font.currentFont().family()
        self.script["font_size"] = self.spn_size.value()
        self.script["is_bold"] = self.chk_bold.isChecked()
        self.script["is_italic"] = self.chk_italic.isChecked()
        self.script["col_span"] = self.spn_cspan.value()
        self.script["row_span"] = self.spn_rspan.value()
        self.script["width"] = self.spn_width.value()
        self.script["height"] = self.spn_height.value()
        self.script["corner_radius"] = self.spn_radius.value()
        self.script["border_width"] = self.spn_border.value()
        
        if self.script.get("type") == "folder":
            self.script["grid_columns"] = self.spn_inner_cols.value()
            self.script["grid_btn_height"] = self.spn_inner_h.value()
        
        self.accept()

# -----------------------------------------------------------------------------
# MAIN WINDOW
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# SETTINGS DIALOG
# -----------------------------------------------------------------------------
class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("GLOBAL CONFIG")
        self.resize(600, 850)
        self.app_bg = self.config.get("app_bg", CP_BG)
        self.win_border = self.config.get("window_border_color", CP_YELLOW)
        self.cfg_color = self.config.get("cfg_btn_color", CP_DIM)
        
        # Item Style Defaults
        self.def_script_bg = self.config.get("def_script_bg", "#FFFFFF")
        self.def_script_fg = self.config.get("def_script_fg", "#000000")
        self.def_script_hbg = self.config.get("def_script_hbg", CP_BG)
        self.def_script_hfg = self.config.get("def_script_hfg", self.def_script_bg)

        self.def_folder_bg = self.config.get("def_folder_bg", CP_YELLOW)
        self.def_folder_fg = self.config.get("def_folder_fg", "#000000")
        self.def_folder_hbg = self.config.get("def_folder_hbg", CP_BG)
        self.def_folder_hfg = self.config.get("def_folder_hfg", self.def_folder_bg)
        
        self.setStyleSheet(f"""
            QDialog {{ background-color: {self.app_bg}; border: 2px solid {self.win_border}; }}
            QLabel {{ color: {CP_TEXT}; font-family: 'Consolas'; font-weight: bold; }}
            QLineEdit, QSpinBox {{ background: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 5px; }}
            QSpinBox::up-button, QSpinBox::down-button {{ width: 0px; border: none; }}
            QCheckBox {{ color: {CP_TEXT}; font-family: 'Consolas'; spacing: 8px; }}
            QCheckBox::indicator {{ width: 14px; height: 14px; border: 1px solid {CP_DIM}; background: {CP_PANEL}; }}
            QCheckBox::indicator:checked {{ background: {CP_YELLOW}; border-color: {CP_YELLOW}; }}
            QPushButton {{ background: {CP_DIM}; color: white; border: none; padding: 8px; font-weight: bold; }}
            QPushButton:hover {{ background: {CP_DIM}44; border: 1px solid {self.win_border}; }}
        """)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 1. Grid Settings
        grp_grid = QGroupBox("GRID")
        grp_grid.setStyleSheet(f"QGroupBox {{ border: 1px solid {CP_DIM}; margin-top: 10px; padding-top: 10px; color: {CP_YELLOW}; font-weight: bold; }}")
        l_grid = QFormLayout()
        
        self.spn_cols = QSpinBox()
        self.spn_cols.setRange(1, 20)
        self.spn_cols.setValue(self.config.get("columns", 5))
        l_grid.addRow("Columns:", self.spn_cols)
        
        self.spn_btn_h = QSpinBox()
        self.spn_btn_h.setRange(20, 9999)
        self.spn_btn_h.setValue(self.config.get("default_btn_height", 40))
        l_grid.addRow("Btn Height:", self.spn_btn_h)

        # Font settings
        self.cmb_font = QFontComboBox()
        self.cmb_font.setCurrentFont(QFont(self.config.get("default_font_family", "Consolas")))
        self.cmb_font.setEditable(False)
        self.cmb_font.setFontFilters(QFontComboBox.FontFilter.ScalableFonts)
        self.cmb_font.setMaximumWidth(180)
        l_grid.addRow("Font:", self.cmb_font)

        self.spn_font_size = QSpinBox()
        self.spn_font_size.setRange(6, 40)
        self.spn_font_size.setValue(self.config.get("default_font_size", 10))
        l_grid.addRow("Font Size:", self.spn_font_size)

        font_style_box = QHBoxLayout()
        self.chk_bold = QCheckBox("Bold")
        self.chk_bold.setChecked(self.config.get("default_is_bold", True))
        self.chk_italic = QCheckBox("Italic")
        self.chk_italic.setChecked(self.config.get("default_is_italic", False))
        font_style_box.addWidget(self.chk_bold)
        font_style_box.addWidget(self.chk_italic)
        font_style_box.addStretch()
        l_grid.addRow("Style:", font_style_box)

        grp_grid.setLayout(l_grid)
        layout.addWidget(grp_grid)

        # 2. Appearance Settings
        grp_app = QGroupBox("APPEARANCE")
        grp_app.setStyleSheet(f"QGroupBox {{ border: 1px solid {CP_DIM}; margin-top: 10px; padding-top: 10px; color: {CP_YELLOW}; font-weight: bold; }}")
        l_app = QFormLayout()

        self.btn_app_bg = QPushButton("Pick Background Color")
        self.update_color_btn_style(self.btn_app_bg, self.app_bg)
        self.btn_app_bg.clicked.connect(self.pick_app_bg)
        l_app.addRow("Main BG:", self.btn_app_bg)

        self.btn_win_border = QPushButton("Pick Border Color")
        self.update_color_btn_style(self.btn_win_border, self.win_border)
        self.btn_win_border.clicked.connect(self.pick_win_border)
        l_app.addRow("Win Border:", self.btn_win_border)

        self.btn_cfg_col = QPushButton("Pick CFG Button Color")
        self.update_color_btn_style(self.btn_cfg_col, self.cfg_color)
        self.btn_cfg_col.clicked.connect(self.pick_cfg_color)
        l_app.addRow("CFG Button:", self.btn_cfg_col)

        self.chk_widgets = QCheckBox("Show Stats Dashboard")
        self.chk_widgets.setChecked(self.config.get("show_widgets", True))
        l_app.addRow("", self.chk_widgets)

        grp_app.setLayout(l_app)
        layout.addWidget(grp_app)

        # 3. Window Settings
        grp_win = QGroupBox("WINDOW")
        grp_win.setStyleSheet(f"QGroupBox {{ border: 1px solid {CP_DIM}; margin-top: 10px; padding-top: 10px; color: {CP_YELLOW}; font-weight: bold; }}")
        l_win = QFormLayout()
        
        size_box = QHBoxLayout()
        self.spn_w = QSpinBox(); self.spn_w.setRange(400, 3000); self.spn_w.setValue(self.config.get("window_width", 1100))
        self.spn_h = QSpinBox(); self.spn_h.setRange(300, 2000); self.spn_h.setValue(self.config.get("window_height", 800))
        size_box.addWidget(QLabel("W:"))
        size_box.addWidget(self.spn_w)
        size_box.addSpacing(10)
        size_box.addWidget(QLabel("H:"))
        size_box.addWidget(self.spn_h)
        size_box.addStretch()
        l_win.addRow(size_box)
        
        self.chk_top = QCheckBox("Always On Top")
        self.chk_top.setChecked(self.config.get("always_on_top", False))
        l_win.addRow("", self.chk_top)
        
        grp_win.setLayout(l_win)
        layout.addWidget(grp_win)

        # 4. Item Style Defaults
        grp_items = QGroupBox("ITEM DEFAULTS")
        grp_items.setStyleSheet(f"QGroupBox {{ border: 1px solid {CP_DIM}; margin-top: 10px; padding-top: 10px; color: {CP_YELLOW}; font-weight: bold; }}")
        l_items = QGridLayout()

        # Labels
        # l_items.addWidget(QLabel("CATEGORY"), 0, 0)
        l_items.addWidget(QLabel("BG"), 0, 1)
        l_items.addWidget(QLabel("FG"), 0, 2)
        l_items.addWidget(QLabel("H-BG"), 0, 3)
        l_items.addWidget(QLabel("H-FG"), 0, 4)

        # Scripts
        l_items.addWidget(QLabel("SCRIPT:"), 1, 0)
        self.btn_sbg = QPushButton(""); self.update_color_btn_style(self.btn_sbg, self.def_script_bg)
        self.btn_sbg.clicked.connect(lambda: self.pick_config_color("def_script_bg", self.btn_sbg))
        l_items.addWidget(self.btn_sbg, 1, 1)

        self.btn_sfg = QPushButton(""); self.update_color_btn_style(self.btn_sfg, self.def_script_fg)
        self.btn_sfg.clicked.connect(lambda: self.pick_config_color("def_script_fg", self.btn_sfg))
        l_items.addWidget(self.btn_sfg, 1, 2)

        self.btn_shbg = QPushButton(""); self.update_color_btn_style(self.btn_shbg, self.def_script_hbg)
        self.btn_shbg.clicked.connect(lambda: self.pick_config_color("def_script_hbg", self.btn_shbg))
        l_items.addWidget(self.btn_shbg, 1, 3)

        self.btn_shfg = QPushButton(""); self.update_color_btn_style(self.btn_shfg, self.def_script_hfg)
        self.btn_shfg.clicked.connect(lambda: self.pick_config_color("def_script_hfg", self.btn_shfg))
        l_items.addWidget(self.btn_shfg, 1, 4)

        # Folders
        l_items.addWidget(QLabel("FOLDER:"), 2, 0)
        self.btn_fbg = QPushButton(""); self.update_color_btn_style(self.btn_fbg, self.def_folder_bg)
        self.btn_fbg.clicked.connect(lambda: self.pick_config_color("def_folder_bg", self.btn_fbg))
        l_items.addWidget(self.btn_fbg, 2, 1)

        self.btn_ffg = QPushButton(""); self.update_color_btn_style(self.btn_ffg, self.def_folder_fg)
        self.btn_ffg.clicked.connect(lambda: self.pick_config_color("def_folder_fg", self.btn_ffg))
        l_items.addWidget(self.btn_ffg, 2, 2)

        self.btn_fhbg = QPushButton(""); self.update_color_btn_style(self.btn_fhbg, self.def_folder_hbg)
        self.btn_fhbg.clicked.connect(lambda: self.pick_config_color("def_folder_hbg", self.btn_fhbg))
        l_items.addWidget(self.btn_fhbg, 2, 3)

        self.btn_fhfg = QPushButton(""); self.update_color_btn_style(self.btn_fhfg, self.def_folder_hfg)
        self.btn_fhfg.clicked.connect(lambda: self.pick_config_color("def_folder_hfg", self.btn_fhfg))
        l_items.addWidget(self.btn_fhfg, 2, 4)

        grp_items.setLayout(l_items)
        layout.addWidget(grp_items)

        # Save
        btn_save = QPushButton("SAVE CONFIG")
        btn_save.setStyleSheet(f"background-color: {CP_GREEN}; color: black;")
        btn_save.clicked.connect(self.save)
        layout.addStretch()
        layout.addWidget(btn_save)

    def update_color_btn_style(self, btn, color):
        lc = QColor(color).lightness()
        btn.setStyleSheet(f"background-color: {color}; color: {'black' if lc > 128 else 'white'}; border: 1px solid {CP_DIM}; padding: 5px;")

    def pick_app_bg(self):
        c = QColorDialog.getColor(QColor(self.app_bg), self)
        if c.isValid():
            self.app_bg = c.name()
            self.update_color_btn_style(self.btn_app_bg, self.app_bg)
            self.update_dialog_style()

    def pick_win_border(self):
        c = QColorDialog.getColor(QColor(self.win_border), self)
        if c.isValid():
            self.win_border = c.name()
            self.update_color_btn_style(self.btn_win_border, self.win_border)
            self.update_dialog_style()

    def pick_cfg_color(self):
        c = QColorDialog.getColor(QColor(self.cfg_color), self)
        if c.isValid():
            self.cfg_color = c.name()
            self.update_color_btn_style(self.btn_cfg_col, self.cfg_color)

    def pick_config_color(self, attr_name, btn):
        current_color = getattr(self, attr_name)
        c = QColorDialog.getColor(QColor(current_color), self)
        if c.isValid():
            setattr(self, attr_name, c.name())
            self.update_color_btn_style(btn, c.name())

    def update_dialog_style(self):
        self.setStyleSheet(f"""
            QDialog {{ background-color: {self.app_bg}; border: 2px solid {self.win_border}; }}
            QLabel {{ color: {CP_TEXT}; font-family: 'Consolas'; font-weight: bold; }}
            QLineEdit, QSpinBox {{ background: {CP_PANEL}; color: {CP_CYAN}; border: 1px solid {CP_DIM}; padding: 5px; }}
            QSpinBox::up-button, QSpinBox::down-button {{ width: 0px; border: none; }}
            QCheckBox {{ color: {CP_TEXT}; font-family: 'Consolas'; spacing: 8px; }}
            QCheckBox::indicator {{ width: 14px; height: 14px; border: 1px solid {CP_DIM}; background: {CP_PANEL}; }}
            QCheckBox::indicator:checked {{ background: {CP_YELLOW}; border-color: {CP_YELLOW}; }}
            QPushButton {{ background: {CP_DIM}; color: white; border: none; padding: 8px; font-weight: bold; }}
            QPushButton:hover {{ background: {CP_DIM}44; border: 1px solid {self.win_border}; }}
        """)

    def save(self):
        self.config["columns"] = self.spn_cols.value()
        self.config["default_btn_height"] = self.spn_btn_h.value()
        self.config["default_font_family"] = self.cmb_font.currentFont().family()
        self.config["default_font_size"] = self.spn_font_size.value()
        self.config["default_is_bold"] = self.chk_bold.isChecked()
        self.config["default_is_italic"] = self.chk_italic.isChecked()
        self.config["app_bg"] = self.app_bg
        self.config["window_border_color"] = self.win_border
        self.config["cfg_btn_color"] = self.cfg_color
        self.config["show_widgets"] = self.chk_widgets.isChecked()
        self.config["window_width"] = self.spn_w.value()
        self.config["window_height"] = self.spn_h.value()
        self.config["always_on_top"] = self.chk_top.isChecked()
        
        # Item Style Defaults
        self.config["def_script_bg"] = self.def_script_bg
        self.config["def_script_fg"] = self.def_script_fg
        self.config["def_script_hbg"] = self.def_script_hbg
        self.config["def_script_hfg"] = self.def_script_hfg

        self.config["def_folder_bg"] = self.def_folder_bg
        self.config["def_folder_fg"] = self.def_folder_fg
        self.config["def_folder_hbg"] = self.def_folder_hbg
        self.config["def_folder_hfg"] = self.def_folder_hfg
        
        self.accept()

# -----------------------------------------------------------------------------
# MAIN WINDOW
# -----------------------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCRIPT // MANAGER_V3.2")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.config = {}
        self.view_stack = [] 
        self.drag_pos = QPoint()
        
        self.load_config()
        self.setup_icon()
        
        # Clipboard for Cut/Paste
        self.clipboard_item = None
        self.clipboard_source_list = None

        # Apply global settings
        app_bg = self.config.get("app_bg", CP_BG)
        self.setStyleSheet(f"QMainWindow {{ background-color: {app_bg}; }}")
        
        # Apply window settings
        w = self.config.get("window_width", 1100)
        h = self.config.get("window_height", 800)
        self.resize(w, h)
        if self.config.get("always_on_top", False):
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        
        self.setup_ui()
        self.refresh_grid()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(2000)

    def setup_icon(self):
        # Code Icon SVG logic
        svg_data = f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
            <rect width="512" height="512" rx="60" fill="{CP_BG}"/>
            <path d="M160 128L32 256l128 128M352 128l128 128-128 128M288 64kL224 448" 
                  stroke="{CP_YELLOW}" stroke-width="40" stroke-linecap="round" fill="none"/>
            <path d="M160 128L32 256l128 128" stroke="{CP_CYAN}" stroke-width="40" stroke-linecap="round" fill="none"/>
        </svg>
        """
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        # For simplicity, we create a basic icon using QPainter instead of full SVG parsing without extra deps
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(CP_BG)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, 64, 64, 10, 10)
        painter.setPen(QColor(CP_YELLOW))
        font = QFont("Consolas", 30, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "</>")
        painter.end()
        self.setWindowIcon(QIcon(pixmap))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding='utf-8') as f:
                    self.config = json.load(f)
            except: self.config = {"scripts": []}
        else: self.config = {"scripts": []}
            
    def save_config(self):
        try:
            with open(CONFIG_FILE, "w", encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            self.refresh_grid()
            
            # Apply immediate global effects
            app_bg = self.config.get("app_bg", CP_BG)
            win_border = self.config.get("window_border_color", CP_YELLOW)
            self.setStyleSheet(f"QMainWindow {{ background-color: {app_bg}; }}")
            if hasattr(self, 'main_frame'):
                self.main_frame.setStyleSheet(f"#MainFrame {{ border: 2px solid {win_border}; background-color: {app_bg}; }}")

            if hasattr(self, 'btn_cfg'):
                cfg_col = self.config.get("cfg_btn_color", CP_DIM)
                self.btn_cfg.script["color"] = cfg_col
                self.btn_cfg.update_style()

            if self.config.get("always_on_top", False):
                self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
            else:
                self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)

            if hasattr(self, 'dash_frame'):
                self.dash_frame.setVisible(self.config.get("show_widgets", True))

            self.show()
            
        except: pass

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        clayout = QVBoxLayout(central)
        clayout.setContentsMargins(0, 0, 0, 0)

        # MAIN FRAME (for border)
        self.main_frame = QFrame()
        self.main_frame.setObjectName("MainFrame")
        app_bg = self.config.get("app_bg", CP_BG)
        win_border = self.config.get("window_border_color", CP_YELLOW)
        self.main_frame.setStyleSheet(f"#MainFrame {{ border: 2px solid {win_border}; background-color: {app_bg}; }}")
        
        self.main_layout = QVBoxLayout(self.main_frame)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        clayout.addWidget(self.main_frame)

        header = QHBoxLayout()
        header.setSpacing(10)
        self.back_btn = CyberButton("<<", script_data={"color": CP_RED, "type": "script"}, config=self.config); self.back_btn.setFixedSize(50, 40); self.back_btn.clicked.connect(self.go_back); self.back_btn.hide()
        self.breadcrumb_layout = QHBoxLayout()
        self.breadcrumb_layout.setSpacing(0)
        
        header.addWidget(self.back_btn)
        header.addLayout(self.breadcrumb_layout)
        header.addStretch()
        
        # ADD BUTTONS - Script and Folder
        self.btn_add_script = CyberButton("+S", script_data={"color": CP_GREEN, "type": "script"}, config=self.config)
        self.btn_add_script.setFixedSize(40, 30)
        self.btn_add_script.clicked.connect(self.add_new_item)
        
        self.btn_add_folder = CyberButton("+F", script_data={"color": CP_YELLOW, "type": "script"}, config=self.config)
        self.btn_add_folder.setFixedSize(40, 30)
        self.btn_add_folder.clicked.connect(self.add_new_folder)
        
        cfg_col = self.config.get("cfg_btn_color", CP_DIM)
        self.btn_cfg = CyberButton("CFG", script_data={"color": cfg_col, "type": "script"}, config=self.config); self.btn_cfg.setFixedSize(50, 30)
        self.btn_cfg.clicked.connect(self.open_global_settings)

        self.btn_close = CyberButton("X", script_data={"color": CP_RED, "type": "script"}, config=self.config); self.btn_close.setFixedSize(40, 30)
        self.btn_close.clicked.connect(self.close)

        header.addWidget(self.btn_add_script)
        header.addWidget(self.btn_add_folder)
        header.addWidget(self.btn_cfg)
        header.addWidget(self.btn_close)
        
        self.main_layout.addLayout(header)

        # Dashboard
        self.dash_frame = QFrame(); self.dash_frame.setFixedHeight(60); 
        dash_layout = QHBoxLayout(self.dash_frame); dash_layout.setContentsMargins(0,0,0,0)
        self.stat_cpu = StatWidget("CPU", CP_CYAN); self.stat_ram = StatWidget("RAM", CP_ORANGE); self.stat_disk = StatWidget("SSD", CP_GREEN)
        dash_layout.addWidget(self.stat_cpu); dash_layout.addWidget(self.stat_ram); dash_layout.addWidget(self.stat_disk)
        lbl_status = QLabel(" GITHUB: OK | RCLONE: IDLE "); lbl_status.setFont(QFont("Consolas", 9)); lbl_status.setStyleSheet(f"color: {CP_SUBTEXT}; background: {CP_PANEL}; border: 1px solid {CP_DIM}; padding: 5px;")
        dash_layout.addWidget(lbl_status); dash_layout.addStretch()
        self.main_layout.addWidget(self.dash_frame)
        self.dash_frame.setVisible(self.config.get("show_widgets", True))

        # Grid
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(f"background: transparent; border: none;")
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.grid_container = QWidget()
        self.grid_container.setAcceptDrops(True)
        self.grid_container.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.grid_container.customContextMenuRequested.connect(self.show_grid_context_menu)
        
        # Event filters for drag/drop on container
        self.grid_container.dragEnterEvent = self.gridDragEnterEvent
        self.grid_container.dropEvent = self.gridDropEvent
        
        self.grid = QGridLayout(self.grid_container)
        self.grid.setSpacing(10)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        self.scroll.setWidget(self.grid_container)
        self.main_layout.addWidget(self.scroll)

    def show_grid_context_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet(f"QMenu {{ background-color: {CP_PANEL}; color: {CP_TEXT}; border: 1px solid {CP_CYAN}; }} QMenu::item:selected {{ background-color: {CP_CYAN}; color: {CP_BG}; }}")
        
        paste_act = menu.addAction("Paste Here")
        paste_act.setEnabled(self.clipboard_item is not None)
        paste_act.triggered.connect(self.paste_item)
        
        menu.addSeparator()
        menu.addAction("Add Script").triggered.connect(self.add_new_item)
        menu.addAction("Add Folder").triggered.connect(self.add_new_folder)
        
        menu.exec(self.grid_container.mapToGlobal(pos))

    def gridDragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-script-item"):
            event.acceptProposedAction()

    def gridDropEvent(self, event):
        source_btn = event.source()
        if not isinstance(source_btn, CyberButton): return
        
        # Find where it was dropped
        drop_pos = event.position().toPoint()
        
        scripts = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
        
        # Find nearest item index
        target_idx = -1
        min_dist = 999999
        for i in range(self.grid.count()):
            w = self.grid.itemAt(i).widget()
            if w:
                dist = (w.geometry().center() - drop_pos).manhattanLength()
                if dist < min_dist:
                    min_dist = dist
                    target_idx = i
        
        if source_btn.script in scripts:
            old_idx = scripts.index(source_btn.script)
            
            # Guard: If dropping on itself or no meaningful change, skip refresh
            if target_idx == old_idx or target_idx == -1:
                event.accept()
                return

            # Perform the move
            scripts.pop(old_idx)
            scripts.insert(target_idx, source_btn.script)
            
            self.save_config()
            event.acceptProposedAction()

    def update_stats(self):
        if not self.config.get("show_widgets", True): return
        try:
            self.stat_cpu.set_value(psutil.cpu_percent())
            self.stat_ram.set_value(psutil.virtual_memory().percent)
            self.stat_disk.set_value(psutil.disk_usage('C://').percent)
        except: pass

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            elif item.layout(): self.clear_layout(item.layout())

    def refresh_grid(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        self.clear_layout(self.breadcrumb_layout)
        
        # Helper for breadcrumb clicks
        def navigate_to(index):
            if index == -1: self.view_stack = []
            else: self.view_stack = self.view_stack[:index+1]
            self.refresh_grid()

        def create_bc_btn(text, action):
            btn = QPushButton(text)
            btn.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
            btn.setStyleSheet(f"""
                QPushButton {{ 
                    color: {CP_YELLOW}; border: none; background: transparent; padding: 2px 5px; text-transform: uppercase;
                }}
                QPushButton:hover {{ color: {CP_CYAN}; text-decoration: underline; }}
            """)
            btn.clicked.connect(action)
            return btn

        def create_sep():
            lbl = QLabel("/")
            lbl.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
            lbl.setStyleSheet(f"color: white; padding: 0 5px;")
            return lbl

        # Initial // ROOT
        self.breadcrumb_layout.addWidget(QLabel("// "))
        self.breadcrumb_layout.itemAt(0).widget().setStyleSheet(f"color: {CP_YELLOW}; font-family: 'Consolas'; font-size: 14pt; font-weight: bold;")
        
        root_btn = create_bc_btn("ROOT", lambda: navigate_to(-1))
        self.breadcrumb_layout.addWidget(root_btn)

        if self.view_stack:
            for i, folder in enumerate(self.view_stack):
                self.breadcrumb_layout.addWidget(create_sep())
                name = folder.get("name", "???").replace("<br>", " ").replace("<br/>", " ").replace("<BR>", " ")
                name = " ".join(name.split())
                btn = create_bc_btn(name, partial(lambda idx: navigate_to(idx), i))
                self.breadcrumb_layout.addWidget(btn)

        if self.view_stack:
            folder = self.view_stack[-1]
            scripts = folder.get("scripts", [])
            self.back_btn.show()
            
            # Context settings (fallback to global)
            cols = folder.get("grid_columns", 0)
            if cols == 0: cols = self.config.get("columns", 5)
            
            def_h = folder.get("grid_btn_height", 0)
            if def_h == 0: def_h = self.config.get("default_btn_height", 40)
        else:
            scripts = self.config.get("scripts", [])
            self.back_btn.hide()
            
            # Global settings
            cols = self.config.get("columns", 5)
            def_h = self.config.get("default_btn_height", 40)

        # Default typography
        def_fs = self.config.get("default_font_size", 10)
        def_font = self.config.get("default_font_family", "Consolas")
        def_bold = self.config.get("default_is_bold", True)
        def_italic = self.config.get("default_is_italic", False)

        grid_map = {} # (row, col) -> occupied
        r, c = 0, 0
        
        for script in scripts:
            # Force height update if not specifically set
            if "height" not in script or script["height"] == 0:
                script["_runtime_height"] = def_h
            
            # Apply default font settings if item doesn't have them
            if "font_size" not in script:
                script["_runtime_font_size"] = def_fs
            else:
                script["_runtime_font_size"] = script["font_size"]
            
            if "font_family" not in script:
                script["_runtime_font_family"] = def_font
            else:
                script["_runtime_font_family"] = script["font_family"]
                
            if "is_bold" not in script:
                script["_runtime_is_bold"] = def_bold
            else:
                script["_runtime_is_bold"] = script["is_bold"]
                
            if "is_italic" not in script:
                script["_runtime_is_italic"] = def_italic
            else:
                script["_runtime_is_italic"] = script["is_italic"]
            
            # Determine spans
            c_span = script.get("col_span", 1)
            r_span = script.get("row_span", 1)
            
            # Find next free slot
            while True:
                conflict = False
                for ir in range(r, r + r_span):
                    for ic in range(c, c + c_span):
                         if (ir, ic) in grid_map:
                             conflict = True
                             break
                    if conflict: break
                
                # Check column boundary
                if c + c_span > cols:
                    r += 1
                    c = 0
                    continue

                if not conflict:
                    break # Found spot
                
                c += 1
                if c >= cols:
                     r += 1
                     c = 0
            
            # Mark occupied
            for ir in range(r, r + r_span):
                for ic in range(c, c + c_span):
                    grid_map[(ir, ic)] = True
            
            # Add widget
            btn = CyberButton(script.get("name", "Unnamed"), script_data=script, config=self.config)
            
            # Apply dynamic preferences - calculate height based on row span
            item_h = script.get("height", 0)
            if item_h == 0:
                item_h = def_h
            
            # For row span > 1, calculate total height including spacing
            if r_span > 1:
                spacing = self.grid.spacing()
                total_h = (item_h * r_span) + (spacing * (r_span - 1))
                btn.setFixedHeight(total_h)
            else:
                btn.setFixedHeight(item_h)
            
            # Apply runtime font settings
            f = QFont(script.get("_runtime_font_family", def_font), script.get("_runtime_font_size", def_fs))
            f.setBold(script.get("_runtime_is_bold", def_bold))
            f.setItalic(script.get("_runtime_is_italic", def_italic))
            btn.setFont(f)
                
            btn.clicked.connect(partial(self.handle_click, script))
            btn.customContextMenuRequested.connect(partial(self.show_context_menu, btn, script))
            self.grid.addWidget(btn, r, c, r_span, c_span, Qt.AlignmentFlag.AlignTop)
        


    def handle_click(self, script):
        if script.get("type") == "folder":
            self.view_stack.append(script)
            self.refresh_grid()
        else:
            self.launch_script(script)

    def _run_shell(self, executable, params=None, work_dir=None, admin=False, hide=False):
        # Centralized helper for robust Windows process launching
        verb = "runas" if admin else None
        show = 0 if hide else 1 # SW_HIDE=0, SW_SHOWNORMAL=1
        try:
            # ShellExecuteW handles path quoting and working directories natively
            res = ctypes.windll.shell32.ShellExecuteW(None, verb, str(executable), params, str(work_dir or ""), show)
            if res <= 32:
                 QMessageBox.warning(self, "Launch Error", f"ShellExecute failed (Code {res}) for:\n{executable}")
        except Exception as e:
            QMessageBox.critical(self, "System Error", f"Failed to execute {executable}:\n{str(e)}")

    def launch_script(self, script):
        # Handle Inline
        if script.get("use_inline"):
            self.launch_inline(script)
            if script.get("kill_window"): self.close()
            return

        path = os.path.expandvars(script.get("path", ""))
        hide = script.get("hide_terminal", False)
        
        if not path: return
        cwd = os.path.dirname(path) if os.path.isfile(path) else None
        
        new_term = script.get("new_terminal", False)
        keep = script.get("keep_open", False)
        admin = script.get("run_admin", False)

        try:
            if path.endswith(".py"):
                if admin or new_term:
                    # Use cmd to host python so /k (keep open) works
                    mode = "/k" if keep else "/c"
                    params = f'{mode} python "{path}"'
                    self._run_shell("cmd.exe", params, cwd, admin=admin, hide=hide)
                else:
                    # Simple launch
                    py_exe = "pythonw" if hide else "python"
                    self._run_shell(py_exe, f'"{path}"', cwd, hide=hide)
            elif path.endswith(".ps1"):
                # Determine shell
                ps_exe = script.get("inline_type")
                if ps_exe not in ["pwsh", "powershell"]:
                    ps_exe = "pwsh" if shutil.which("pwsh") else "powershell"
                
                # Construct params
                no_exit = "-NoExit" if keep else ""
                params = f'{no_exit} -File "{path}"'
                
                if admin or new_term:
                    self._run_shell(ps_exe, params, cwd, admin=admin, hide=hide)
                else:
                    self._run_shell(ps_exe, params, cwd, hide=hide)
            else:
                # Generic launch (Executables, Batch files, Folders)
                if admin or new_term:
                    mode = "/k" if keep else "/c"
                    self._run_shell("cmd.exe", f'{mode} "{path}"', cwd, admin=admin, hide=hide)
                else:
                    self._run_shell(path, None, cwd, hide=hide)
            
            if script.get("kill_window"): self.close()
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

    def launch_inline(self, script):
        import tempfile
        code = script.get("inline_script", "")
        # Very simple execution
        ext = ".ps1" if script.get("inline_type") in ["pwsh", "powershell"] else ".bat"
        with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False) as f:
            f.write(code)
            tmp = f.name
        
        hide = script.get("hide_terminal", False)
        new_term = script.get("new_terminal", False)
        keep = script.get("keep_open", False)
        admin = script.get("run_admin", False)

        if ext == ".ps1":
            ps_exe = script.get("inline_type", "powershell")
            if ps_exe not in ["pwsh", "powershell"]:
                 ps_exe = "pwsh" if shutil.which("pwsh") else "powershell"
            
            no_exit = "-NoExit" if keep else ""
            params = f'{no_exit} -File "{tmp}"'
            self._run_shell(ps_exe, params, os.getcwd(), admin=admin, hide=hide)
        else:
            # Inline batch/command
            mode = "/k" if keep else "/c"
            self._run_shell("cmd.exe", f'{mode} "{tmp}"', os.getcwd(), admin=admin, hide=hide)

    def go_back(self):
        if self.view_stack: self.view_stack.pop(); self.refresh_grid()

    def show_context_menu(self, btn, script, pos):
        menu = QMenu(self)
        menu.setStyleSheet(f"QMenu {{ background-color: {CP_PANEL}; color: {CP_TEXT}; border: 1px solid {CP_CYAN}; }} QMenu::item:selected {{ background-color: {CP_CYAN}; color: {CP_BG}; }}")
        
        menu.addAction("Edit").triggered.connect(lambda: self.open_edit(script))
        menu.addAction("Reset Styles").triggered.connect(lambda: self.reset_item_styles(script))
        menu.addAction("Duplicate").triggered.connect(lambda: self.duplicate_item(script))
        menu.addSeparator()
        menu.addAction("Cut").triggered.connect(lambda: self.cut_item(script))
        
        paste_act = menu.addAction("Paste")
        paste_act.setEnabled(self.clipboard_item is not None)
        paste_act.triggered.connect(self.paste_item)
        
        menu.addSeparator()
        menu.addAction("Delete").triggered.connect(lambda: self.delete_item(script))
        menu.exec(btn.mapToGlobal(pos))

    def reset_item_styles(self, script):
        """Reset item styles to global defaults"""
        is_folder = (script.get("type") == "folder")
        
        # Remove custom style keys to use defaults
        keys_to_remove = ["color", "text_color", "hover_color", "hover_text_color", 
                         "border_color", "font_family", "font_size", "is_bold", 
                         "is_italic", "corner_radius", "border_width", "width", "height"]
        for key in keys_to_remove:
            script.pop(key, None)
        
        # Reset spans
        script["col_span"] = 1
        script["row_span"] = 1
        
        # Reset folder-specific settings
        if is_folder:
            script["grid_columns"] = 0
            script["grid_btn_height"] = 0
        
        self.save_config()

    def duplicate_item(self, script):
        import copy
        new_script = copy.deepcopy(script)
        if "name" in new_script: new_script["name"] += " (Copy)"
        
        target_list = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
        target_list.append(new_script)
        self.save_config()

    def cut_item(self, script):
        self.clipboard_item = script
        self.clipboard_source_list = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
        # Visual feedback could be added here (e.g. ghosting the button)
        QApplication.beep()

    def paste_item(self):
        if not self.clipboard_item: return
        
        target_list = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
        
        # Remove from old
        if self.clipboard_source_list is not None and self.clipboard_item in self.clipboard_source_list:
            self.clipboard_source_list.remove(self.clipboard_item)
            
        # Add to new
        target_list.append(self.clipboard_item)
        
        self.clipboard_item = None
        self.clipboard_source_list = None
        self.save_config()

    def open_edit(self, script):
        if EditDialog(script, self).exec(): self.save_config()

    def delete_item(self, script):
        dlg = QDialog(self)
        dlg.setWindowTitle("DELETE")
        dlg.setFixedSize(350, 120)
        dlg.setStyleSheet(f"""
            QDialog {{ background-color: {CP_BG}; border: 2px solid {CP_RED}; }}
            QLabel {{ color: {CP_TEXT}; font-family: 'Consolas'; font-size: 11pt; }}
        """)
        
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 20, 20, 20)
        
        lbl = QLabel(f"Delete '{script.get('name')}'?")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_yes = QPushButton("YES")
        btn_yes.setStyleSheet(f"background-color: {CP_RED}; color: white; border: none; padding: 8px 25px; font-family: 'Consolas'; font-weight: bold;")
        btn_yes.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_yes.clicked.connect(dlg.accept)
        
        btn_no = QPushButton("NO")
        btn_no.setStyleSheet(f"background-color: {CP_DIM}; color: white; border: none; padding: 8px 25px; font-family: 'Consolas'; font-weight: bold;")
        btn_no.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_no.clicked.connect(dlg.reject)
        
        btn_layout.addWidget(btn_yes)
        btn_layout.addWidget(btn_no)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        if dlg.exec():
            target_list = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
            if script in target_list:
                target_list.remove(script)
                self.save_config()

    def add_new_item(self):
        new_script = {"name": "New Script", "path": "", "type": "script", "color": "#FFFFFF"}
        target_list = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
        target_list.append(new_script)
        if EditDialog(new_script, self).exec(): self.save_config()
        else: target_list.remove(new_script)

    def add_new_folder(self):
        new_folder = {
            "name": "New Folder", 
            "type": "folder", 
            "scripts": [], 
            "color": CP_YELLOW,
            "col_span": 1,
            "row_span": 1
        }
        target_list = self.view_stack[-1]["scripts"] if self.view_stack else self.config["scripts"]
        target_list.append(new_folder)
        if EditDialog(new_folder, self).exec(): 
            self.save_config()
        else: 
            target_list.remove(new_folder)

    def open_global_settings(self):
        dlg = SettingsDialog(self.config, self)
        if dlg.exec():
            self.save_config()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
