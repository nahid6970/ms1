# from core.widgets.base import BaseWidget
# from core.validation.widgets.yasb.traffic import VALIDATION_SCHEMA
# from PyQt6.QtWidgets import QLabel, QApplication
# from PyQt6.QtCore import Qt
# import os

# class CustomWidget(BaseWidget):
#     validation_schema = VALIDATION_SCHEMA

#     def __init__(
#         self,
#         label: str,
#         label_alt: str,
#         update_interval: int,
#         callbacks: dict[str, str],
#     ):
#         super().__init__(update_interval, class_name="path_status")
#         self.interval = update_interval // 1000

#         self._status_label = QLabel("")
#         self.widget_layout.addWidget(self._status_label)  # Add status label

#         self.callbacks = callbacks  # Store callbacks

#         self.callback_left = callbacks["on_left"]
#         self.callback_right = callbacks["on_right"]
#         self.callback_middle = callbacks["on_middle"]
#         self.callback_timer = "update_label"

#         self.register_callback("update_label", self._update_label)  # Register update_label callback

#         self.start_timer()

#     def _update_label(self):
#         # Source and destination directories
#         source_dest_pairs = [
#             ("C:\\ms1\\yasb\\core\\widgets\\yasb\\ex", "C:\\ms1\\yasb\\core\\widgets\\yasb\\ex"),
#             ("C:\\ms1\\yasb\\core\\widgets\\yasb\\uptime.py", "C:\\ms1\\asset\\komorebi.json")
#         ]

#         # Check if source and destination directories are the same
#         statuses = []
#         for source, dest in source_dest_pairs:
#             if os.path.abspath(source) == os.path.abspath(dest):
#                 statuses.append("✅")  # Source and destination are the same
#             else:
#                 statuses.append("❌")  # Source and destination are different

#         # Update status label text
#         self._status_label.setText(f"Status: {', '.join(statuses)}")
#         self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align text to center
#         self._status_label.setStyleSheet("font-size: 16px;")

# if __name__ == "__main__":
#     app = QApplication([])
#     widget = CustomWidget("", "", 1000, {"on_left": "", "on_right": "", "on_middle": "", "update_label": ""})
#     widget.show()
#     app.exec()








import os
import filecmp
from core.widgets.base import BaseWidget
from core.validation.widgets.yasb.traffic import VALIDATION_SCHEMA
from PyQt6.QtWidgets import QLabel, QApplication
from PyQt6.QtCore import Qt

class CustomWidget(BaseWidget):
    validation_schema = VALIDATION_SCHEMA

    def __init__(
        self,
        label: str,
        label_alt: str,
        update_interval: int,
        callbacks: dict[str, str],
    ):
        super().__init__(update_interval, class_name="path_status")
        self.interval = update_interval // 1000

        self._status_label = QLabel("")
        self.widget_layout.addWidget(self._status_label)  # Add status label

        self.callbacks = callbacks  # Store callbacks

        self.callback_left = callbacks["on_left"]
        self.callback_right = callbacks["on_right"]
        self.callback_middle = callbacks["on_middle"]
        self.callback_timer = "update_label"

        self.register_callback("update_label", self._update_label)  # Register update_label callback

        self.start_timer()

    def _update_label(self):
        # Source and destination paths (files or directories)
        source_dest_pairs = {
            "komorebi": ("C:\\Users\\nahid\\komorebi.json", "C:\\ms1\\asset\\komorebi\\komorebi.json"),
            "glaze-wm": ("C:\\Users\\nahid\\.glaze-wm", "C:\\ms1\\asset\\glazewm\\.glaze-wm"),
            "glaze-wm": ("C:\\Program Files\\Nilesoft Shell\\imports", "C:\\ms1\\asset\\nilesoft_shell\\imports"),
        }

        # Check if all source and destination paths have the same content
        is_all_same = True
        names = []
        for name, (source, dest) in source_dest_pairs.items():
            if os.path.isdir(source) and os.path.isdir(dest):
                dcmp = filecmp.dircmp(source, dest)
                if dcmp.diff_files or dcmp.left_only or dcmp.right_only:
                    is_all_same = False
                    names.append(name)
            elif os.path.isfile(source) and os.path.isfile(dest):
                if not filecmp.cmp(source, dest):
                    is_all_same = False
                    names.append(name)
            else:
                # Handle the case where source or destination file/directory is missing
                is_all_same = False
                names.append(name)

        # Set the emoji and name accordingly
        if is_all_same:
            emoji = "✅"
            #! name = "All paths have identical content"
            name = ""
        else:
            emoji = "❌"
            name = ", ".join(names)

        # Update status label text
        self._status_label.setText(f"{emoji} {name}")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align text to center
        self._status_label.setStyleSheet("font-size: 16px;")

if __name__ == "__main__":
    app = QApplication([])
    widget = CustomWidget("", "", 1000, {"on_left": "", "on_right": "", "on_middle": "", "update_label": ""})
    widget.show()
    app.exec()
