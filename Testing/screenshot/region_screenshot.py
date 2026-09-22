"""Fast PyQt6 region screenshot tool with lazy OCR integrations."""
from __future__ import annotations
import io, json, os, struct, subprocess, sys, tempfile
from datetime import datetime
from pathlib import Path
from PIL import ImageGrab, ImageQt
from PyQt6.QtCore import QPoint, QRect, QSize, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import (QApplication, QDialog, QFileDialog, QGridLayout, QHBoxLayout,
    QLabel, QMessageBox, QPushButton, QScrollArea, QTextEdit, QToolButton, QVBoxLayout,
    QWidget, QInputDialog, QMenu, QStyle,
    QColorDialog)

# CYBERPUNK THEME PALETTE (THEME_GUIDE.md)
CP_BG="#050505"; CP_PANEL="#111111"; CP_YELLOW="#FCEE0A"; CP_CYAN="#00F0FF"; CP_RED="#FF003C"; CP_GREEN="#00ff21"; CP_ORANGE="#ff934b"; CP_DIM="#3a3a3a"; CP_TEXT="#E0E0E0"; CP_SUBTEXT="#808080"
UI_FONT="JetBrainsMono NFP"
BASE_DIR=Path(__file__).resolve().parent; CONFIG_FILE=BASE_DIR / "folders.json"

def load_folders():
    try:
        data=json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        if isinstance(data,list) and (not data or isinstance(data[0],str)): return [{"path":p,"color":CP_GREEN} for p in data]
        return data if isinstance(data,list) else []
    except (OSError,ValueError): return []

def save_folders(folders):
    try: CONFIG_FILE.write_text(json.dumps(folders,indent=4),encoding="utf-8")
    except OSError as exc: QMessageBox.critical(None,"Save error",str(exc))

def capture_screen():
    try: return ImageGrab.grab(all_screens=True,include_layered_windows=True)
    except TypeError: return ImageGrab.grab(all_screens=True)

def pil_to_pixmap(image): return QPixmap.fromImage(ImageQt.toqimage(image.convert("RGBA")))

def send_to_clipboard(image,text_path=None):
    """Copy both an image and a file item for editors and Windows Explorer."""
    try:
        import win32clipboard
        if text_path:
            file_path=Path(text_path)
        else:
            temp_dir=Path(tempfile.gettempdir())/"screenshot_temp"; temp_dir.mkdir(exist_ok=True)
            file_path=temp_dir/f"clipboard_{datetime.now():%Y%m%d_%H%M%S_%f}.png"; image.save(file_path)
        output=io.BytesIO(); image.convert("RGB").save(output,"BMP"); dib=output.getvalue()[14:]
        dropfiles=struct.pack("IiiII",20,0,0,0,1)+(str(file_path)+"\0\0").encode("utf-16le")
        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB,dib)
            win32clipboard.SetClipboardData(win32clipboard.CF_HDROP,dropfiles)
            if text_path: win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT,str(file_path))
        finally: win32clipboard.CloseClipboard()
        return True
    except Exception:
        app=QApplication.instance()
        if not app: return False
        app.clipboard().setImage(ImageQt.toqimage(image.convert("RGBA")))
        if text_path: app.clipboard().setText(str(text_path))
        return True

def copy_image_for_browser(image):
    """Put a durable Windows bitmap on the clipboard before opening Chrome."""
    return send_to_clipboard(image)

GLOBAL_QSS=f"""QMainWindow,QDialog{{background:{CP_BG};}} QWidget{{color:{CP_TEXT};font-family:'{UI_FONT}';font-size:10pt;}}
QPushButton,QToolButton{{background:{CP_DIM};border:1px solid {CP_DIM};color:white;padding:7px 12px;font-weight:bold;}}
QPushButton:hover,QToolButton:hover{{background:#2a2a2a;border-color:{CP_YELLOW};color:{CP_YELLOW};}} QPushButton:pressed,QToolButton:checked{{background:{CP_YELLOW};color:#000;}}
QTextEdit{{background:{CP_PANEL};color:{CP_CYAN};border:1px solid {CP_DIM};padding:5px;selection-background-color:{CP_CYAN};selection-color:#000;}}
QScrollArea{{background:transparent;border:none;}} QScrollBar:vertical{{background:{CP_BG};width:10px;}} QScrollBar::handle:vertical{{background:{CP_CYAN};min-height:20px;border-radius:5px;}} QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{height:0;}}"""

class RegionSelector(QDialog):
    def __init__(self,image):
        super().__init__(None,Qt.WindowType.FramelessWindowHint|Qt.WindowType.WindowStaysOnTopHint); self.image=image; self.start=self.end=self.selection=None; self.setCursor(Qt.CursorShape.CrossCursor); self.setWindowState(Qt.WindowState.WindowFullScreen); self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    def showEvent(self,event): self.pixmap=pil_to_pixmap(self.image).scaled(self.size(),Qt.AspectRatioMode.IgnoreAspectRatio,Qt.TransformationMode.FastTransformation); super().showEvent(event)
    def paintEvent(self,event):
        p=QPainter(self); p.drawPixmap(0,0,self.pixmap); p.fillRect(self.rect(),QColor(0,0,0,85))
        if self.start and self.end:
            r=QRect(self.start,self.end).normalized(); p.drawPixmap(r,self.pixmap,r); p.setPen(QPen(QColor(CP_CYAN),2)); p.drawRect(r); p.setPen(QPen(QColor(CP_YELLOW),1)); p.drawText(r.topLeft()+QPoint(8,-8),f"{r.width()} x {r.height()}")
    def mousePressEvent(self,e):
        if e.button()==Qt.MouseButton.LeftButton: self.start=self.end=e.position().toPoint(); self.update()
    def mouseMoveEvent(self,e):
        if self.start: self.end=e.position().toPoint(); self.update()
    def mouseReleaseEvent(self,e):
        if self.start and self.end:
            r=QRect(self.start,self.end).normalized()
            if r.width()>2 and r.height()>2: self.selection=(r.left(),r.top(),r.right()+1,r.bottom()+1)
            self.accept()
    def keyPressEvent(self,e):
        if e.key()==Qt.Key.Key_Escape: self.reject()
    @classmethod
    def select(cls,image):
        d=cls(image); d.show(); d.raise_(); d.activateWindow(); return d.exec()==QDialog.DialogCode.Accepted and d.selection

class SettingsDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent); self.setWindowTitle("SETTINGS"); self.setMinimumWidth(400); l=QVBoxLayout(self); l.addWidget(QLabel("SETTINGS SYSTEM\nReserved for future customizations.")); b=QPushButton("CLOSE"); b.clicked.connect(self.accept); l.addWidget(b)

class FolderCardButton(QToolButton):
    def __init__(self,parent=None):
        super().__init__(parent); self.setProperty("cardHover",False)
    def _set_hover(self,value):
        self.setProperty("cardHover",value); self.style().unpolish(self); self.style().polish(self); self.update()
    def enterEvent(self,event):
        self._set_hover(True); super().enterEvent(event)
    def leaveEvent(self,event):
        self._set_hover(False); super().leaveEvent(event)

class FolderChooser(QDialog):
    def __init__(self,folders,image,parent=None):
        super().__init__(parent); self.folders=folders; self.image=image; self.choice=None; self.edit_mode=False; self.setWindowTitle("DESTINATION SELECTOR"); self.setWindowFlags(Qt.WindowType.FramelessWindowHint|Qt.WindowType.WindowStaysOnTopHint); self.setMinimumSize(760,420)
        root=QVBoxLayout(self); head=QHBoxLayout(); title=QLabel("DESTINATION SELECTOR"); title.setStyleSheet(f"color:{CP_GREEN};font-weight:bold;font-size:12pt;"); head.addWidget(title); head.addStretch(); temp=QPushButton("TEMP IMAGES"); temp.clicked.connect(self.open_temp_folder); head.addWidget(temp); settings=QPushButton("⚙ SETTINGS"); settings.clicked.connect(lambda:SettingsDialog(self).exec()); head.addWidget(settings); restart=QPushButton("↺ RESTART"); restart.clicked.connect(self.restart); head.addWidget(restart); root.addLayout(head)
        action_label=QLabel("WHAT DO YOU WANT TO DO WITH THIS SCREENSHOT?"); action_label.setStyleSheet(f"color:{CP_YELLOW};font-weight:bold;"); root.addWidget(action_label)
        actions=QHBoxLayout()
        for text,value,color in (("📋 COPY","CLIPBOARD",CP_CYAN),("💾 COPY + PATH","CLIPBOARD_PATH",CP_GREEN),("📁 MOVE TO FOLDER","MOVE_TO_FOLDER",CP_YELLOW),("🌏 OPEN IN CHROME","BROWSER",CP_ORANGE),("🔍 GOOGLE LENS","GOOGLE_IMG","#4285f4"),("📝 EXTRACT TEXT","OCR","#e040fb")):
            b=QPushButton(text); b.setStyleSheet(f"QPushButton{{color:{color};}}")
            if value=="MOVE_TO_FOLDER": b.clicked.connect(self.move_to_folder)
            elif value=="BROWSER": b.clicked.connect(self.open_browser)
            elif value=="GOOGLE_IMG": b.clicked.connect(self.google_images)
            else: b.clicked.connect(lambda checked=False,v=value:self.choose(v))
            actions.addWidget(b)
        root.addLayout(actions)
        folder_label=QLabel("DESTINATIONS"); folder_label.setStyleSheet(f"color:{CP_SUBTEXT};font-weight:bold;"); root.addWidget(folder_label)
        self.scroll=QScrollArea(); self.scroll.setWidgetResizable(True); self.host=QWidget(); self.grid=QGridLayout(self.host); self.grid.setSpacing(8); self.scroll.setWidget(self.host); root.addWidget(self.scroll); close=QPushButton("EXIT [ESC]"); close.clicked.connect(self.reject); root.addWidget(close,alignment=Qt.AlignmentFlag.AlignCenter); self.render()
    def keyPressEvent(self,e):
        if e.key()==Qt.Key.Key_Escape: self.reject()
    def restart(self): os.execv(sys.executable,[sys.executable]+sys.argv)
    def open_temp_folder(self):
        folder=Path(tempfile.gettempdir())/"screenshot_temp"; folder.mkdir(exist_ok=True); os.startfile(str(folder))
    def toggle_edit(self): self.edit_mode=not self.edit_mode; self.edit_button.setText("EDIT: ON" if self.edit_mode else "EDIT: OFF"); self.render()
    def render(self):
        while self.grid.count():
            item=self.grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        items=[(f.get("name") or os.path.basename(f["path"]) or f["path"],f.get("color",CP_GREEN),f.get("icon","▣"),f["path"]) for f in self.folders]
        for i,item in enumerate(items): self.add_card(i//4,i%4,*item)
        self.add_card(len(items)//4,len(items)%4,"ADD FOLDER",CP_SUBTEXT,"+","ADD")
    def add_card(self,row,col,label,color,icon,value):
        b=FolderCardButton(); b.setFixedSize(160,108); is_folder=value in [f["path"] for f in self.folders]
        b.setStyleSheet(f"QToolButton{{background:{CP_PANEL};border:none;border-radius:8px;}} QToolButton[cardHover=\"true\"]{{background:#1c1c1c;border:none;}} QToolButton:pressed{{background:#252525;border:none;}}")
        card_layout=QVBoxLayout(b); card_layout.setContentsMargins(4,0,4,0); card_layout.setSpacing(0)
        if value in [f["path"] for f in self.folders]:
            icon_pixmap=QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon).pixmap(QSize(32,32))
            tinted=QPixmap(icon_pixmap.size()); tinted.fill(Qt.GlobalColor.transparent)
            icon_painter=QPainter(tinted); icon_painter.drawPixmap(0,0,icon_pixmap); icon_painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn); icon_painter.fillRect(tinted.rect(),QColor(color)); icon_painter.end()
            icon_label=QLabel(); icon_label.setPixmap(tinted)
        else:
            icon_label=QLabel(icon)
        icon_label.setFixedHeight(29); icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter); icon_label.setStyleSheet(f"color:{color};font-family:'{UI_FONT}';font-size:23pt;border:none;")
        name_color=color if is_folder else CP_TEXT
        name_label=QLabel(label.upper()[:16]); name_label.setFixedHeight(16); name_label.setAlignment(Qt.AlignmentFlag.AlignCenter); name_label.setStyleSheet(f"color:{name_color};font-family:'{UI_FONT}';font-size:9pt;border:none;")
        for child in (icon_label,name_label): child.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        card_layout.addWidget(icon_label); card_layout.addWidget(name_label)
        if value=="ADD": b.clicked.connect(self.add_folder)
        elif self.edit_mode and value in [f["path"] for f in self.folders]: b.clicked.connect(lambda checked=False,v=value:self.edit_folder(v))
        elif value=="BROWSER": b.clicked.connect(self.open_browser)
        elif value=="GOOGLE_IMG": b.clicked.connect(self.google_images)
        else: b.clicked.connect(lambda checked=False,v=value:self.choose(v))
        if value in [f["path"] for f in self.folders]:
            b.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            b.customContextMenuRequested.connect(lambda pos,v=value,button=b: self.folder_menu(button.mapToGlobal(pos),v))
        self.grid.addWidget(b,row,col)
    def choose(self,value): self.choice=value; self.accept()
    def move_to_folder(self):
        folder=QFileDialog.getExistingDirectory(self,"Move Screenshot To")
        if folder:
            self.choice=folder; self.accept()
    def folder_menu(self,global_pos,path):
        menu=QMenu(self); menu.setMinimumWidth(150); menu.setStyleSheet(f"QMenu{{background:{CP_PANEL};color:{CP_TEXT};border:1px solid {CP_CYAN};font-family:'{UI_FONT}';font-size:10pt;padding:4px;}} QMenu::item{{padding:6px 18px;}} QMenu::item:selected{{background:{CP_CYAN};color:{CP_BG};}} QMenu::separator{{height:1px;background:{CP_DIM};margin:4px 8px;}}")
        rename=menu.addAction("Rename"); color=menu.addAction("Color"); menu.addSeparator(); remove=menu.addAction("Remove")
        action=menu.exec(global_pos)
        if action==rename: self.rename_folder(path)
        elif action==color: self.color_folder(path)
        elif action==remove: self.remove_folder(path)
    def folder_index(self,path): return next(i for i,f in enumerate(self.folders) if f["path"]==path)
    def rename_folder(self,path):
        i=self.folder_index(path); old=self.folders[i].get("name") or os.path.basename(path) or path
        name,ok=QInputDialog.getText(self,"Rename Folder Button","Displayed name:",text=old)
        if ok and name.strip(): self.folders[i]["name"]=name.strip(); save_folders(self.folders); self.render()
    def color_folder(self,path):
        i=self.folder_index(path); c=QColorDialog.getColor(QColor(self.folders[i].get("color",CP_GREEN)),self,"Choose Folder Color")
        if c.isValid(): self.folders[i]["color"]=c.name(); save_folders(self.folders); self.render()
    def icon_folder(self,path):
        i=self.folder_index(path); icon,ok=QInputDialog.getText(self,"Folder Icon","Enter an emoji or Unicode glyph:",text=self.folders[i].get("icon","▣"))
        if ok and icon.strip(): self.folders[i]["icon"]=icon.strip(); save_folders(self.folders); self.render()
    def remove_folder(self,path):
        i=self.folder_index(path)
        if QMessageBox.question(self,"Remove Folder Button","Remove this folder button?",QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)==QMessageBox.StandardButton.Yes:
            self.folders.pop(i); save_folders(self.folders); self.render()
    def add_folder(self):
        path=QFileDialog.getExistingDirectory(self,"Select Folder to Add")
        if path:
            c=QColorDialog.getColor(QColor(CP_GREEN),self,"Choose Folder Color"); self.folders.append({"path":path,"color":c.name() if c.isValid() else CP_GREEN}); save_folders(self.folders); self.render()
    def edit_folder(self,path):
        i=next(i for i,f in enumerate(self.folders) if f["path"]==path)
        current=self.folders[i].get("icon","▣")
        icon,ok=QInputDialog.getText(self,"Folder Icon","Enter an emoji or Unicode glyph:",text=current)
        if ok and icon.strip(): self.folders[i]["icon"]=icon.strip()
        c=QColorDialog.getColor(QColor(self.folders[i].get("color",CP_GREEN)),self,"Choose Folder Color")
        if c.isValid(): self.folders[i]["color"]=c.name()
        if (ok and icon.strip()) or c.isValid(): save_folders(self.folders); self.render()
    def open_browser(self):
        f=Path(tempfile.gettempdir())/f"screenshot_{datetime.now():%Y%m%d_%H%M%S}.png"; self.image.save(f); subprocess.Popen(["cmd","/c","start","","chrome",str(f)]); self.accept()
    def google_images(self):
        f=Path(tempfile.gettempdir())/"google_img_search.png"; self.image.save(f); copy_image_for_browser(self.image); self.accept(); subprocess.Popen(["cmd","/c","start","","chrome","https://lens.google.com/"])

class OCRWorker(QThread):
    done=pyqtSignal(str,str)
    def __init__(self,image,mode): super().__init__(); self.image=image; self.mode=mode
    def run(self):
        langs={"en":(["en"],"eng","ENGLISH"),"bn":(["bn"],"ben","BANGLA"),"mixed":(["bn","en"],"ben+eng","MIXED (EN/BN)")}[self.mode]
        try:
            import numpy as np, easyocr; text="\n".join(easyocr.Reader(langs[0]).readtext(np.array(self.image),detail=0))
        except ImportError:
            try:
                import pytesseract; text=pytesseract.image_to_string(self.image,lang=langs[1])
            except Exception as exc: text=f"OCR dependency/error: {exc}"
        except Exception as exc: text=f"OCR error: {exc}"
        self.done.emit(langs[2],text)

class OCRDialog(QDialog):
    def __init__(self,image,parent=None):
        super().__init__(parent); self.setWindowTitle("OCR EXTRACTION"); self.resize(650,500); l=QVBoxLayout(self); self.title=QLabel("SELECT EXTRACTION MODE"); self.title.setStyleSheet("color:#e040fb;font-weight:bold;"); l.addWidget(self.title); row=QHBoxLayout()
        for text,mode in (("ENGLISH ONLY","en"),("BANGLA ONLY","bn"),("MIXED (EN + BN)","mixed")):
            b=QPushButton(text); b.clicked.connect(lambda checked=False,m=mode:self.start(image,m)); row.addWidget(b)
        l.addLayout(row); self.text=QTextEdit(); l.addWidget(self.text); self.worker=None
    def start(self,image,mode): self.title.setText("EXTRACTING... PLEASE WAIT"); self.worker=OCRWorker(image,mode); self.worker.done.connect(self.show_result); self.worker.start()
    def show_result(self,mode,text):
        self.title.setText(f"EXTRACTED TEXT ({mode})"); self.text.setPlainText(text); b=QPushButton("COPY TO CLIPBOARD"); b.clicked.connect(lambda:QApplication.clipboard().setText(self.text.toPlainText())); self.layout().addWidget(b)

def main():
    app=QApplication.instance() or QApplication(sys.argv)
    app.setStyleSheet(GLOBAL_QSS); app.setFont(QFont(UI_FONT,10))
    try:
        screen=capture_screen(); selection=RegionSelector.select(screen)
        if not selection: return 0
        x1,y1,x2,y2=selection; image=screen.crop((x1,y1,x2,y2)); chooser=FolderChooser(load_folders(),image)
        chooser.show(); chooser.raise_(); chooser.activateWindow()
        if chooser.exec()!=QDialog.DialogCode.Accepted or not chooser.choice: return 0
        target=chooser.choice
        if target=="CLIPBOARD": send_to_clipboard(image)
        elif target=="CLIPBOARD_PATH":
            d=Path(tempfile.gettempdir())/"screenshot_temp"; d.mkdir(exist_ok=True); f=d/f"screenshot_{datetime.now():%Y%m%d_%H%M%S}.png"; image.save(f); send_to_clipboard(image,f)
        elif target=="OCR": OCRDialog(image).exec()
        else:
            folder=Path(target); folder.mkdir(parents=True,exist_ok=True); image.save(folder/f"screenshot_{datetime.now():%Y%m%d_%H%M%S}.png")
        return 0
    except Exception as exc:
        QMessageBox.critical(None,"Screenshot error",f"{type(exc).__name__}: {exc}")
        return 1

if __name__=="__main__": sys.exit(main())
