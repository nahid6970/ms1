
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
"komorebi"       :("C:\\Users\\nahid\\komorebi.json"                                                                                  ,"C:\\ms1\\asset\\komorebi\\komorebi.json"                         ),
"glaze-wm"       :("C:\\Users\\nahid\\.glaze-wm"                                                                                      ,"C:\\ms1\\asset\\glazewm\\.glaze-wm"                              ),
"Nilesoft"       :("C:\\Program Files\\Nilesoft Shell\\imports"                                                                       ,"C:\\ms1\\asset\\nilesoft_shell\\imports"                         ),
"whkd"           :("C:\\Users\\nahid\\.config\\whkdrc"                                                                                ,"C:\\ms1\\asset\\whkd\\whkdrc\\whkdrc"                            ),
"pwshH":("C:\\Users\\nahid\\AppData\\Roaming\\Microsoft\\Windows\\PowerShell\\PSReadLine\\ConsoleHost_history.txt"          ,"C:\\Users\\nahid\\OneDrive\\backup\\ConsoleHost_history.txt"     ),
"terminal"       :("C:\\Users\\nahid\\AppData\\Local\\Packages\\Microsoft.WindowsTerminal_8wekyb3d8bbwe\\LocalState\\settings.json"   ,"C:\\ms1\\asset\\terminal\\settings.json\\settings.json"          ),
"rclone_config"  :("C:\\Users\\nahid\\scoop\\apps\\rclone\\current\\rclone.conf"                                                      ,"C:\\Users\\nahid\\OneDrive\\backup\\rclone\\rclone.conf"         ),
"pwsh_profile"   :("C:\\Users\\nahid\\OneDrive\\Documents\\PowerShell\\Microsoft.PowerShell_profile.ps1"                              ,"C:\\ms1\\asset\\Powershell\\Microsoft.PowerShell_profile.ps1"    ),

"Sr_db"      :("C:\\ProgramData\\Sonarr\\sonarr.db"                                                                               ,"C:\\Users\\nahid\\OneDrive\\backup\\arr\\sonarr\\sonarr.db"      ),
"Sr_cf"  :("C:\\ProgramData\\Sonarr\\config.xml"                                                                              ,"C:\\Users\\nahid\\OneDrive\\backup\\arr\\sonarr\\config.xml"     ),

"Rr_db"       :("C:\\ProgramData\\Radarr\\radarr.db"                                                                               ,"C:\\Users\\nahid\\OneDrive\\backup\\arr\\radarr\\radarr.db"      ),
"Rr_cf"   :("C:\\ProgramData\\Radarr\\config.xml"                                                                              ,"C:\\Users\\nahid\\OneDrive\\backup\\arr\\radarr\\config.xml"     ),

"Pr_db"     :("C:\\ProgramData\\Prowlarr\\prowlarr.db"                                                                           ,"C:\\Users\\nahid\\OneDrive\\backup\\arr\\prowlarr\\prowlarr.db"  ),
"Pr_cf" :("C:\\ProgramData\\Prowlarr\\config.xml"                                                                            ,"C:\\Users\\nahid\\OneDrive\\backup\\arr\\prowlarr\\config.xml"   ),

"br_db"      :("C:\\ProgramData\\Bazarr\\data\\db\\bazarr.db"                                                                     ,"C:\\Users\\nahid\\OneDrive\\backup\\arr\\bazarr\\bazarr.db"      ),
"br_cf"  :("C:\\ProgramData\\Bazarr\\data\\config\\config.yaml"                                                               ,"C:\\Users\\nahid\\OneDrive\\backup\\arr\\bazarr\\config.yaml"    ),

"Rss_db"    :("C:\\Users\\nahid\\scoop\\apps\\rssguard\\current\\data4\\database"                                                ,"C:\\Users\\nahid\\OneDrive\\backup\\rssguard\\database"          ),
"Rss_cf":("C:\\Users\\nahid\\scoop\\apps\\rssguard\\current\\data4\\config\\config.ini"                                      ,"C:\\Users\\nahid\\OneDrive\\backup\\rssguard\\config\\config.ini"),

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
            name = "✅"
        else:
            emoji = "❌"
            names_per_row = 4
            formatted_names = [", ".join(names[i:i+names_per_row]) for i in range(0, len(names), names_per_row)]
            name = "\n".join(formatted_names)

        # Update status label text
        self._status_label.setText(f"{name}")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align text to center
        self._status_label.setStyleSheet("font-size: 12px;")


if __name__ == "__main__":
    app = QApplication([])
    widget = CustomWidget("", "", 1000, {"on_left": "", "on_right": "", "on_middle": "", "update_label": ""})
    widget.show()
    app.exec()
