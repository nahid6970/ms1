# KDE Plasma Custom Widget (Plasmoid) Blueprint

> [!NOTE]
> **To the User**: Provide this markdown file to the AI in a future session. It serves as a detailed guide for the AI to build a custom taskbar/panel widget (Plasmoid) for your KDE Plasma desktop.

---

## 🎯 Context & Objective for the AI
The user wants to create a custom **KDE Plasma panel widget (Plasmoid)**. The widget needs to be placed on the panel (taskbar), display information or action buttons, and execute custom shell/Python scripts when clicked.

Your task is to generate the complete code and structure for the widget based on the user's custom specifications.

---

## 📦 Plasmoid Package Structure

Every custom KDE widget must follow this directory layout:
```text
my_custom_widget/
├── metadata.json
└── contents/
    └── ui/
        └── main.qml
```

### 1. The Metadata File (`metadata.json`)
The AI should generate `metadata.json` declaring the properties of the widget.
*For KDE Plasma 6 standard:*
```json
{
    "KPlugin": {
        "Id": "org.kde.plasma.custom_script_runner",
        "Name": "Script Runner Widget",
        "Description": "Launches custom python scripts from the panel",
        "Icon": "utilities-terminal",
        "Category": "Utilities",
        "ServiceTypes": ["Plasma/Applet"],
        "Version": "1.0",
        "Authors": [
            {
                "Name": "User"
            }
        ]
    },
    "X-Plasma-API-Minimum-Version": "6.0"
}
```

### 2. The Interface & Script Execution (`contents/ui/main.qml`)
The AI must write a QML file using **PlasmaCore** / **PlasmaComponents** and utilize `DataSource` or `PlasmaCore.IconItem` to execute shell commands when interacting with the button.

*For example, executing a script on mouse click:*
```qml
import QtQuick
import QtQuick.Layouts
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.plasmoid
import org.kde.plasma.components as PlasmaComponents

PlasmoidItem {
    id: root
    
    // Core sizing for the taskbar representation
    compactRepresentation: MouseArea {
        id: compactArea
        width: 32
        height: 32
        
        PlasmaCore.IconItem {
            anchors.fill: parent
            source: "utilities-terminal" // Icon displayed in taskbar
        }
        
        onClicked: {
            // Trigger script execution
            executable.exec("python3 /path/to/script.py")
        }
    }
    
    // Command executor engine
    PlasmaCore.DataSource {
        id: executable
        engine: "executable"
        connectedSources: []
        
        onNewData: {
            var exitCode = data["exit code"];
            var stdout = data["stdout"];
            console.log("Exit code:", exitCode, "Output:", stdout);
            disconnectSource(sourceName); // clean up execution
        }
        
        function exec(cmd) {
            connectSource(cmd);
        }
    }
}
```

---

## 🚀 Execution Guide (For the AI to follow)

When the user asks to build a widget:
1. **Gather Requirements**: Ask the user what icon to show, what text to display, and what script/command should execute when clicked.
2. **Generate Code**: Output the complete text contents for `metadata.json` and `main.qml`.
3. **Write the Files**: Save the files into a subdirectory (e.g. `widget_package/`).
4. **Provide Installation Commands**: Guide the user on installing the package.

---

## 📋 Instructions for the User

When you want to build your widget:
1. Upload/paste this file (`kde_widget_instructions.md`).
2. Provide your widget requirements: **"I want a panel button that displays [Icon/Text] and runs the script `/path/to/my_script.py` when clicked."**
3. Run the installation command provided by the AI:
   ```bash
   # Install the generated widget
   kpackagetool6 -t Plasma/Applet --install ./widget_package
   ```
4. Right-click your taskbar, select **Add Widgets...**, and drag your custom widget onto the taskbar.
