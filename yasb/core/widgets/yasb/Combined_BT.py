from tkinter import messagebox
import psutil
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.traffic import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel, QApplication
from PyQt6.QtCore import Qt
import subprocess
import os
import time
from PyQt6.QtGui import QMouseEvent, QKeyEvent


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


#! Example
    #     self._XXX = HoverLabel(
    #         initial_color    ="font-size: 20px; background-color:#4b95e9; color:#000000; border:1px solid black; border-radius:5px; margin:4px 0px;",
    #         hover_color      ="font-size: 20px; background-color:#55c9ff; color:#000000; border:1px solid black; border-radius:5px; margin:4px 0px;",
    #         hover_after_color="font-size: 20px; background-color:#4b95e9; color:#000000; border:1px solid black; border-radius:5px; margin:4px 0px;"
    #     )
    #     self.widget_layout.addWidget(self._XXX)
    #     self._XXX.setText("Display")
    #     self._XXX.mousePressEvent=lambda event:self._XXX_action(event,self._XXX)
    # def _XXX_action(self, event, label):
    #     if event.button() == Qt.MouseButton.LeftButton:
    #        subprocess.Popen('cmd /c start C:/ms1/mypygui_import/app_store.py')
    #     elif event.button() == Qt.MouseButton.RightButton:
    #        subprocess.Popen('cmd /c start C:/ms1/mypygui_import/applist.py')



#! Step 1
        self._Edit_label = HoverLabel(
            initial_color    ="font-size: 20px; ; color:#ffffff; ; ; margin:4px 0px;",
            hover_color      ="font-size: 20px; ; color:#000000; ; ; margin:4px 0px;",
            hover_after_color="font-size: 20px; ; color:#ffffff; ; ; margin:4px 0px;"
        )

        self._info_get = HoverLabel(
            initial_color    ="font-size: 20px; ; color:#ffffff; ; ; margin:4px 0px;",
            hover_color      ="font-size: 20px; ; color:#000000; ; ; margin:4px 0px;",
            hover_after_color="font-size: 20px; ; color:#ffffff; ; ; margin:4px 0px;"
        )

        self._Tools_label = HoverLabel(
            initial_color    ="font-size: 20px; ; color:#ffffff; ; ; margin:4px 0px;",
            hover_color      ="font-size: 20px; ; color:#000000; ; ; margin:4px 0px;",
            hover_after_color="font-size: 20px; ; color:#ffffff; ; ; margin:4px 0px;"
        )

        self._desktop = HoverLabel(
            initial_color    ="font-size: 20px; ; color:#ffffff; ; ; margin:4px 0px;",
            hover_color      ="font-size: 20px; ; color:#000000; ; ; margin:4px 0px;",
            hover_after_color="font-size: 20px; ; color:#ffffff; ; ; margin:4px 0px;"
        )

        self._folder = HoverLabel(
            initial_color    ="font-size: 20px; ; color:#f5c33c; ; ; margin:4px 0px;",
            hover_color      ="font-size: 20px; ; color:#d37800; ; ; margin:4px 0px;",
            hover_after_color="font-size: 20px; ; color:#f5c33c; ; ; margin:4px 0px;"
        )

        self._appmanager = HoverLabel(
            initial_color    ="font-size: 16px; background-color:#4b95e9; color:#000000; border:1px solid black; border-radius:5px; margin:4px 3px;",
            hover_color      ="font-size: 16px; background-color:#55c9ff; color:#000000; border:1px solid black; border-radius:5px; margin:4px 3px;",
            hover_after_color="font-size: 16px; background-color:#4b95e9; color:#000000; border:1px solid black; border-radius:5px; margin:4px 3px;"
        )

        self._shutdown_restart = HoverLabel(
            initial_color    ="font-size: 20px; ; color:#f55e06; ; ; margin:4px 0px;",
            hover_color      ="font-size: 20px; ; color:#fa0606; ; ; margin:4px 0px;",
            hover_after_color="font-size: 20px; ; color:#f55e06; ; ; margin:4px 0px;"
        )

        self._color_pallet = HoverLabel(
            initial_color    ="font-size: 20px; ; color:#ffaefb; ; ; margin:4px 0px;",
            hover_color      ="font-size: 20px; ; color:#ff00ff; ; ; margin:4px 0px;",
            hover_after_color="font-size: 20px; ; color:#ffaefb; ; ; margin:4px 0px;"
        )

        self._xy_position = HoverLabel(
            initial_color    ="font-size: 20px; ; color:#ffffff; ; ; margin:4px 0px;",
            hover_color      ="font-size: 20px; ; color:#e75c1c; ; ; margin:4px 0px;",
            hover_after_color="font-size: 20px; ; color:#ffffff; ; ; margin:4px 0px;"
        )

        self.PowerToys_Mouse_Pointer = HoverLabel(
            initial_color    ="font-size: 20px; ; color:#00ecfd; ; ; margin:4px 0px;",
            hover_color      ="font-size: 20px; ; color:#008394; ; ; margin:4px 0px;",
            hover_after_color="font-size: 20px; ; color:#00ecfd; ; ; margin:4px 0px;"
        )

        self.PowerToys_Text_Extract = HoverLabel(
            initial_color    ="font-size: 20px; ; color:#00ecfd; ; ; margin:4px 0px;",
            hover_color      ="font-size: 20px; ; color:#008394; ; ; margin:4px 0px;",
            hover_after_color="font-size: 20px; ; color:#00ecfd; ; ; margin:4px 0px;"
        )

        self.PowerToys_Screen_Ruler = HoverLabel(
            initial_color    ="font-size: 20px; ; color:#00ecfd; ; ; margin:4px 0px;",
            hover_color      ="font-size: 20px; ; color:#008394; ; ; margin:4px 0px;",
            hover_after_color="font-size: 20px; ; color:#00ecfd; ; ; margin:4px 0px;"
        )

        self.PowerToys_Screen_Color = HoverLabel(
            initial_color    ="font-size: 20px; ; color:#00ecfd; ; ; margin:4px 0px;",
            hover_color      ="font-size: 20px; ; color:#008394; ; ; margin:4px 0px;",
            hover_after_color="font-size: 20px; ; color:#00ecfd; ; ; margin:4px 0px;"
        )

        self._potplaylist = HoverLabel(
            initial_color    ="font-size: 20px; color:#91fd2b; margin:4px 0px;",
            hover_color      ="font-size: 20px; color:#798602; margin:4px 0px;",
            hover_after_color="font-size: 20px; color:#91fd2b; margin:4px 0px;"
        )



#! Step 2
        self.widget_layout.addWidget(self._Tools_label)
        self.widget_layout.addWidget(self.PowerToys_Mouse_Pointer)
        self.widget_layout.addWidget(self.PowerToys_Text_Extract)
        self.widget_layout.addWidget(self.PowerToys_Screen_Ruler)
        self.widget_layout.addWidget(self.PowerToys_Screen_Color)
        self.widget_layout.addWidget(self._info_get)
        self.widget_layout.addWidget(self._Edit_label)
        self.widget_layout.addWidget(self._color_pallet)
        self.widget_layout.addWidget(self._xy_position)
        self.widget_layout.addWidget(self._potplaylist)
        self.widget_layout.addWidget(self._appmanager)
        self.widget_layout.addWidget(self._folder)
        self.widget_layout.addWidget(self._desktop)
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
        self._Edit_label.setText("\uf005")
        self._info_get.setText("\uf129")
        self._Tools_label.setText("\ue20f")
        self._desktop.setText("\udb80\uddc4")
        self._folder.setText("\uf07c")
        self._appmanager.setText("\uf40e")
        self._shutdown_restart.setText("\uf011")
        self._color_pallet.setText("\ue22b")
        self._xy_position.setText("\udb83\ude51")
        self.PowerToys_Mouse_Pointer.setText("\uf245")
        self.PowerToys_Text_Extract.setText("\uf15c")
        self.PowerToys_Screen_Ruler.setText("\udb84\udf53")
        self.PowerToys_Screen_Color.setText("\ue275")
        self._potplaylist.setText("\ueba6")


#! Step 4
        self._Edit_label.mousePressEvent=lambda event:self._on_Edit_click(event,self._Edit_label)
        self._info_get.mousePressEvent=lambda event:self._get_info(event,self._info_get)
        self._Tools_label.mousePressEvent =lambda event:self._Tools_yasb(event,self._Tools_label)
        self._desktop.mousePressEvent=lambda event:self._desktop_action(event,self._desktop)
        self._folder.mousePressEvent=lambda event:self._folder_action(event,self._folder)
        self._appmanager.mousePressEvent=lambda event:self._appmanager_action(event,self._appmanager)
        self._shutdown_restart.mousePressEvent=lambda event:self._shutdown_restart_action(event,self._shutdown_restart)
        self._color_pallet.mousePressEvent=lambda event:self._color_pallet_action(event,self._color_pallet)
        self._xy_position.mousePressEvent=lambda event:self._xy_position_action(event,self._xy_position)
        self.PowerToys_Mouse_Pointer.mousePressEvent=lambda event:self.PowerToys_Mouse_Pointer_action(event,self.PowerToys_Mouse_Pointer)
        self.PowerToys_Text_Extract.mousePressEvent=lambda event:self.PowerToys_Text_Extract_action(event,self.PowerToys_Text_Extract)
        self.PowerToys_Screen_Ruler.mousePressEvent=lambda event:self.PowerToys_Screen_Ruler_action(event,self.PowerToys_Screen_Ruler)
        self.PowerToys_Screen_Color.mousePressEvent=lambda event:self.PowerToys_Screen_Color_action(event,self.PowerToys_Screen_Color)
        self._potplaylist.mousePressEvent=lambda event:self._potplaylist_action(event,self._potplaylist)


#! Step 5
    def _on_Edit_click(self, event: QMouseEvent, label: HoverLabel):
        modifiers = QApplication.keyboardModifiers()
        if event.button() == Qt.MouseButton.LeftButton:
            if modifiers == Qt.KeyboardModifier.ControlModifier:
                subprocess.Popen(['cmd.exe', '/c', 'Code C:\ms1\mypygui_import\edit_files.py']) 
            else:
                subprocess.Popen(['cmd.exe', '/c', 'C:\ms1\mypygui_import\edit_files.py']) 
        elif event.button() == Qt.MouseButton.RightButton:
            if modifiers == Qt.KeyboardModifier.ControlModifier:
                self.callback_right()  # Call the right mouse click callback
            else:
                subprocess.Popen(['cmd.exe', '/c', 'code', '-g', 'C:\\ms1\\mypygui_import\\edit_files.py:89'])
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.callback_middle()


    def _get_info(self, event, label):
        if event.button() == Qt.MouseButton.LeftButton:
           subprocess.Popen(['cmd.exe', '/c', 'start', 'C:\\ms1\\utility\\info.py'])
        elif event.button() == Qt.MouseButton.RightButton:
           subprocess.Popen(['cmd.exe', '/c', 'code', 'C:\\ms1\\utility\\info.py'])


    def _Tools_yasb(self, event, label):
        if event.button() == Qt.MouseButton.LeftButton:
            subprocess.Popen('cmd /c start C:/ms1/mypygui_import/tools.py')
        elif event.button() == Qt.MouseButton.RightButton:
           subprocess.Popen(['cmd.exe', '/c', ''])


    def _desktop_action(self, event, label):
        if event.button() == Qt.MouseButton.LeftButton:
            subprocess.Popen('cmd /c C:\\ms1\\desktop_icon.py')
        elif event.button() == Qt.MouseButton.RightButton:
           subprocess.Popen()


    def _folder_action(self, event, label):
        if event.button() == Qt.MouseButton.LeftButton:
            subprocess.Popen('cmd /c C:/ms1/mypygui_import/folder.py')
        elif event.button() == Qt.MouseButton.RightButton:
            subprocess.Popen('cmd /c Code C:/ms1/mypygui_import/folder.py')


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


    def _color_pallet_action(self, event: QMouseEvent, label: HoverLabel):
        modifiers = QApplication.keyboardModifiers()
        if event.button() == Qt.MouseButton.LeftButton:
            if modifiers == Qt.KeyboardModifier.ControlModifier:
                subprocess.Popen('cmd /c Code C:/ms1/utility/color/color_picker.py')
            else:
                subprocess.Popen('cmd /c C:/ms1/utility/color/color_picker.py')
        elif event.button() == Qt.MouseButton.RightButton:
            if modifiers == Qt.KeyboardModifier.ControlModifier:
                subprocess.Popen('cmd /c Code C:/ms1/utility/color/color_pallet_rand_fg_bgFF00.py')
            else:
                subprocess.Popen('cmd /c C:/ms1/utility/color/color_pallet_rand_fg_bgFF00.py')
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.callback_middle()


    def _xy_position_action(self, event, label):
        if event.button() == Qt.MouseButton.LeftButton:
           subprocess.Popen('cmd /c C:/ms1/utility/position_x_y.py')
        elif event.button() == Qt.MouseButton.RightButton:
           subprocess.Popen('cmd /c code C:/ms1/utility/position_x_y.py')


    def PowerToys_Mouse_Pointer_action(self, event, label):
        if event.button() == Qt.MouseButton.LeftButton:
           subprocess.Popen('cmd /c python C:/ms1/HotKeys.py powertoys_mouse_crosshair')
        elif event.button() == Qt.MouseButton.RightButton:
           subprocess.Popen('cmd /c python C:/ms1/HotKeys.py x_mouse_enable')


    def PowerToys_Text_Extract_action(self, event, label):
        if event.button() == Qt.MouseButton.LeftButton:
           subprocess.Popen('cmd /c python C:/ms1/HotKeys.py powertoys_TextExtract')


    def PowerToys_Screen_Ruler_action(self, event, label):
        if event.button() == Qt.MouseButton.LeftButton:
           subprocess.Popen('cmd /c python C:/ms1/HotKeys.py powertoys_ruler')


    def PowerToys_Screen_Color_action(self, event, label):
        if event.button() == Qt.MouseButton.LeftButton:
           subprocess.Popen('cmd /c python C:/ms1/HotKeys.py powertoys_color_picker')


    def _potplaylist_action(self, event, label):
        if event.button() == Qt.MouseButton.LeftButton:
           subprocess.Popen('cmd /c start C:/ms1/scripts/playlist.py')


    def _killProcess_action(self, event, label):
        if event.button() == Qt.MouseButton.LeftButton:
            subprocess.Popen('cmd /c start pwsh -Command "$processName = (Get-Process | Select-Object Name, CPU | Sort-Object CPU -Descending | Format-Table -AutoSize | Out-String | fzf) -split \'\\s{2,}\' | Select-Object -First 1; if ($processName) { Stop-Process -Name $processName -Force; Write-Host \"Process $processName terminated.\" } else { Write-Host \"No process selected.\" }"')



if __name__ == "__main__":
    app = QApplication([])
    widget = CombinedWidget("Download", "Upload", 1000, {"on_left": "", "on_right": "", "on_middle": ""})
    widget.show()
    app.exec()






