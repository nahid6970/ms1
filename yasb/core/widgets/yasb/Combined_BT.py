from tkinter import messagebox
import psutil
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.traffic import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel, QApplication
from PyQt6.QtCore import Qt
import subprocess
import os
import time

class HoverLabel(QLabel):
    def __init__(self, initial_color, hover_color, hover_after_color, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setStyleSheet(initial_color)
        self.hover_color = hover_color
        self.hover_after_color = hover_after_color

    def enterEvent(self, event):
        self.setStyleSheet(self.hover_color)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self.hover_after_color)
        super().leaveEvent(event)

class CombinedWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA
    def __init__(
        self,
        label: str,
        label_alt: str,
        update_interval: int,
        callbacks: dict[str, str],
    ):
        super().__init__(update_interval, class_name="combined-widget")
        self.interval = update_interval // 1000

        self._show_alt_label = False
        self._label_content = label
        self._label_alt_content = label_alt

#! Step 1
        self._Edit_label = HoverLabel(
            initial_color    ="font-size: 16px; background-color:#020163; color:#FFFFFF; border:1px solid black; border-radius:5px; margin:4px 3px;",
            hover_color      ="font-size: 16px; background-color:#ffffff; color:#000000; border:1px solid black; border-radius:5px; margin:4px 3px;",
            hover_after_color="font-size: 16px; background-color:#020163; color:#FFFFFF; border:1px solid black; border-radius:5px; margin:4px 3px;"
        )

        self._info_get = HoverLabel(
            initial_color    ="font-size: 16px; background-color:#eddebe; color:#000000; border:1px solid black; border-radius:5px; margin:4px 3px;",
            hover_color      ="font-size: 16px; background-color:#5b1033; color:#FFFFFF; border:1px solid black; border-radius:5px; margin:4px 3px;",
            hover_after_color="font-size: 16px; background-color:#eddebe; color:#000000; border:1px solid black; border-radius:5px; margin:4px 3px;"
        )

        self._reload_label = HoverLabel(
            initial_color    ="font-size: 16px; background-color:#08684a; color:#FFFFFF; border:1px solid black; border-radius:5px; margin:4px 3px;",
            hover_color      ="font-size: 16px; background-color:#1a8357; color:#FFFFFF; border:1px solid black; border-radius:5px; margin:4px 3px;",
            hover_after_color="font-size: 16px; background-color:#08684a; color:#FFFFFF; border:1px solid black; border-radius:5px; margin:4px 3px;"
        )

        self._desktop = HoverLabel(
            initial_color    ="font-size: 16px; background-color:#fafffb; color:#000000; border:1px solid black; border-radius:5px; margin:4px 3px;",
            hover_color      ="font-size: 16px; background-color:#55c9ff; color:#000000; border:1px solid black; border-radius:5px; margin:4px 3px;",
            hover_after_color="font-size: 16px; background-color:#fafffb; color:#000000; border:1px solid black; border-radius:5px; margin:4px 3px;"
        )

        self._folder = HoverLabel(
            initial_color    ="font-size: 16px; background-color:#ffda72; color:#000000; border:1px solid black; border-radius:5px; margin:4px 3px;",
            hover_color      ="font-size: 16px; background-color:#b98e18; color:#000000; border:1px solid black; border-radius:5px; margin:4px 3px;",
            hover_after_color="font-size: 16px; background-color:#ffda72; color:#000000; border:1px solid black; border-radius:5px; margin:4px 3px;"
        )

        self._appmanager = HoverLabel(
            initial_color    ="font-size: 16px; background-color:#4b95e9; color:#000000; border:1px solid black; border-radius:5px; margin:4px 3px;",
            hover_color      ="font-size: 16px; background-color:#55c9ff; color:#000000; border:1px solid black; border-radius:5px; margin:4px 3px;",
            hover_after_color="font-size: 16px; background-color:#4b95e9; color:#000000; border:1px solid black; border-radius:5px; margin:4px 3px;"
        )

        self._shutdown_restart = HoverLabel(
            initial_color    ="font-size: 16px; background-color:#ffffff; color:#000000; border:1px solid black; border-radius:5px; margin:4px 3px;",
            hover_color      ="font-size: 16px; background-color:#ff0000; color:#ffffff; border:1px solid black; border-radius:5px; margin:4px 3px;",
            hover_after_color="font-size: 16px; background-color:#ffffff; color:#000000; border:1px solid black; border-radius:5px; margin:4px 3px;"
        )

#! Step 2
        self.widget_layout.addWidget(self._Edit_label)
        self.widget_layout.addWidget(self._info_get)
        self.widget_layout.addWidget(self._reload_label)
        self.widget_layout.addWidget(self._desktop)
        self.widget_layout.addWidget(self._folder)
        self.widget_layout.addWidget(self._appmanager)
        self.widget_layout.addWidget(self._shutdown_restart)

        self.register_callback("toggle_label", self._toggle_label)
        self.register_callback("update_label", self._update_label)

        self.callback_left = callbacks["on_left"]
        self.callback_right = callbacks["on_right"]
        self.callback_middle = callbacks["on_middle"]
        self.callback_timer = "update_label"

        self.start_timer()

    def _toggle_label(self):
        self._show_alt_label = not self._show_alt_label
        self._update_label()

    def _update_label(self):
        # Update the active label at each timer interval
        active_label_content = self._label_alt_content if self._show_alt_label else self._label_content


#! Step 3
        # Set text and colors for additional labels
        self._Edit_label.setText("\uf044")
        self._info_get.setText("\uf129")
        self._reload_label.setText("\uf256")
        self._desktop.setText("\udb80\uddc4")
        self._folder.setText("\uf07c")
        self._appmanager.setText("\uf40e")
        self._shutdown_restart.setText("\uf011")

#! Step 4
        self._Edit_label.mousePressEvent   =lambda event:self._on_Edit_click    (event,self._Edit_label  )
        self._info_get.mousePressEvent     =lambda event:self._get_info         (event,self._info_get    )
        self._reload_label.mousePressEvent =lambda event:self._reload_yasb      (event,self._reload_label)
        self._desktop.mousePressEvent      =lambda event:self._desktop_action   (event,self._desktop     )
        self._folder.mousePressEvent       =lambda event:self._folder_action    (event,self._folder      )
        self._appmanager.mousePressEvent   =lambda event:self._appmanager_action(event,self._appmanager  )
        self._shutdown_restart.mousePressEvent   =lambda event:self._shutdown_restart_action(event,self._shutdown_restart  )


#! Step 5
    def _on_Edit_click(self, event, label):
        if event.button() == Qt.MouseButton.LeftButton:
           subprocess.Popen(['cmd.exe', '/c', 'C:\ms1\mypygui_import\edit_files.py'])
        elif event.button() == Qt.MouseButton.RightButton:
           subprocess.Popen(['cmd.exe', '/c', 'code', '-g', 'C:\\ms1\\mypygui_import\\edit_files.py:89'])

    def _get_info(self, event, label):
        if event.button() == Qt.MouseButton.LeftButton:
           subprocess.Popen(['cmd.exe', '/c', 'start', 'C:\\ms1\\utility\\info.py'])
        elif event.button() == Qt.MouseButton.RightButton:
           subprocess.Popen(['cmd.exe', '/c', 'code', 'C:\\ms1\\utility\\info.py'])

    def _reload_yasb(self, event, label):
        if event.button() == Qt.MouseButton.LeftButton:
            subprocess.Popen('cmd /c start taskkill /f /im python.exe')
        elif event.button() == Qt.MouseButton.RightButton:
           subprocess.Popen(['cmd.exe', '/c', 'start', 'taskmgr.exe'])

    def _desktop_action(self, event, label):
        if event.button() == Qt.MouseButton.LeftButton:
            subprocess.Popen('cmd /c C:\\ms1\\desktop_icon.py')
        elif event.button() == Qt.MouseButton.RightButton:
           subprocess.Popen()

    def _folder_action(self, event, label):
        if event.button() == Qt.MouseButton.LeftButton:
            subprocess.Popen('cmd /c C:/ms1/mypygui_import/folder.py')
        elif event.button() == Qt.MouseButton.RightButton:
           subprocess.Popen()

    def _appmanager_action(self, event, label):
        if event.button() == Qt.MouseButton.LeftButton:
           subprocess.Popen('cmd /c start C:/ms1/mypygui_import/app_store.py')
        elif event.button() == Qt.MouseButton.RightButton:
           subprocess.Popen('cmd /c start C:/ms1/mypygui_import/applist.py')

    def _shutdown_restart_action(self, event, label):
        if event.button() == Qt.MouseButton.LeftButton:
            confirmed = messagebox.askyesno("Confirmation", "Are you sure you want to shutdown?")
            if confirmed:
                subprocess.Popen(["shutdown", "/s", "/f", "/t", "0"])
        elif event.button() == Qt.MouseButton.RightButton:
            confirmed = messagebox.askyesno("Confirmation", "Are you sure you want to restart?")
            if confirmed:
                subprocess.Popen(["shutdown", "/r", "/f", "/t", "0"])

if __name__ == "__main__":
    app = QApplication([])
    widget = CombinedWidget("Download", "Upload", 1000, {"on_left": "", "on_right": "", "on_middle": ""})
    widget.show()
    app.exec()






