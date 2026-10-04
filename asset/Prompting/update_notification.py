from datetime import datetime
from pathlib import Path


NOTIFICATION_FILE = Path(r"C:\Users\nahid\notification.txt")


def main() -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    NOTIFICATION_FILE.write_text(timestamp, encoding="utf-8")


if __name__ == "__main__":
    main()
