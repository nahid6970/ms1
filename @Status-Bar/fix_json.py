import json

data = {
    "git": [
        {
            "name": "ms1",
            "path": "C:/@delta/ms1",
            "label": "ms1"
        },
        {
            "name": "db",
            "path": "C:/@delta/db",
            "label": "db"
        },
        {
            "name": "test",
            "path": "C:/@delta/test",
            "label": "test"
        }
    ],
    "rclone": [
        {
            "name": "msBackups",
            "path": "C:/@delta/msBackups",
            "dst": "gu:/msBackups",
            "label": "󰆲",
            "cmd": "rclone check src dst --fast-list --size-only"
        },
        {
            "name": "software",
            "path": "D:/software",
            "dst": "gu:/software",
            "label": "",
            "cmd": "rclone check src dst --fast-list --size-only"
        },
        {
            "name": "song",
            "path": "D:/song",
            "dst": "gu:/song",
            "label": "",
            "cmd": "rclone check src dst --fast-list --size-only"
        },
        {
            "name": "ms1",
            "path": "C:/@delta/ms1/",
            "dst": "o0:/ms1/",
            "label": "ms1",
            "cmd": 'rclone check src dst --fast-list --size-only --exclude ".git/**" --exclude "__pycache__/**"',
            "left_click_cmd": 'rclone sync src dst -P --fast-list --exclude ".git/**" --exclude "__pycache__/**"  --log-level INFO',
            "right_click_cmd": "rclone sync dst src -P --fast-list"
        },
        {
            "name": "Photos",
            "path": "C:/Users/nahid/Pictures/",
            "dst": "gu:/Pictures/",
            "label": "",
            "cmd": 'rclone check src dst --fast-list --size-only --exclude ".globalTrash/**" --exclude ".stfolder/**" --exclude ".stfolder (1)/**"',
            "left_click_cmd": 'rclone sync src dst -P --fast-list --track-renames --exclude ".globalTrash/**" --exclude ".stfolder/**" --log-level INFO',
            "right_click_cmd": "rclone sync dst src -P --fast-list"
        }
    ]
}

with open('projects_config.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)
