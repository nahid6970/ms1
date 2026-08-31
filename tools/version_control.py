import os
import hashlib
import json
import shutil
from datetime import datetime

REPO_DIR = ".localhub"
COMMITS_DIR = os.path.join(REPO_DIR, "commits")
HISTORY_FILE = os.path.join(REPO_DIR, "history.json")


def init_repo():
    if not os.path.exists(REPO_DIR):
        os.makedirs(COMMITS_DIR)
        with open(HISTORY_FILE, "w") as f:
            json.dump([], f)
        print("Initialized empty LocalHub repository.")
    else:
        print("Repository already initialized.")


def hash_file(filepath):
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def commit(message):
    if not os.path.exists(REPO_DIR):
        print("Repository not initialized.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_id = hashlib.sha1(timestamp.encode()).hexdigest()[:7]
    commit_path = os.path.join(COMMITS_DIR, commit_id)
    os.makedirs(commit_path)

    files = [f for f in os.listdir() if os.path.isfile(f) and not f.startswith(".") and f != os.path.basename(__file__)]

    for file in files:
        shutil.copy(file, os.path.join(commit_path, file))

    with open(HISTORY_FILE, "r+") as f:
        history = json.load(f)
        history.append({
            "id": commit_id,
            "message": message,
            "timestamp": timestamp,
            "files": files
        })
        f.seek(0)
        json.dump(history, f, indent=2)
        f.truncate()

    print(f"Committed as {commit_id}: {message}")


def log():
    if not os.path.exists(HISTORY_FILE):
        print("No history found.")
        return

    with open(HISTORY_FILE) as f:
        history = json.load(f)

    for commit in reversed(history):
        print(f"{commit['id']} - {commit['timestamp']} - {commit['message']}")


def checkout(commit_id):
    commit_path = os.path.join(COMMITS_DIR, commit_id)
    if not os.path.exists(commit_path):
        print("Commit not found.")
        return

    files = os.listdir(commit_path)
    for file in files:
        shutil.copy(os.path.join(commit_path, file), file)

    print(f"Checked out commit {commit_id}.")


def diff():
    if not os.path.exists(HISTORY_FILE):
        print("No history found.")
        return

    with open(HISTORY_FILE) as f:
        history = json.load(f)

    if len(history) < 2:
        print("Not enough commits to show differences.")
        return

    latest = history[-1]
    previous = history[-2]

    latest_files = set(latest["files"])
    previous_files = set(previous["files"])

    added = latest_files - previous_files
    removed = previous_files - latest_files
    common = latest_files & previous_files

    modified = []
    for file in common:
        latest_path = os.path.join(COMMITS_DIR, latest["id"], file)
        previous_path = os.path.join(COMMITS_DIR, previous["id"], file)
        if hash_file(latest_path) != hash_file(previous_path):
            modified.append(file)

    print(f"Changes from {previous['id']} to {latest['id']}:")
    if added:
        print("  Added:", ", ".join(added))
    if removed:
        print("  Removed:", ", ".join(removed))
    if modified:
        print("  Modified:", ", ".join(modified))
    if not (added or removed or modified):
        print("  No changes detected.")


if __name__ == "__main__":
    import sys
    args = sys.argv

    if len(args) < 2:
        print("Usage: python localhub.py [init|commit|log|diff|checkout <id>]")
    elif args[1] == "init":
        init_repo()
    elif args[1] == "commit":
        if len(args) < 3:
            print("Please provide a commit message.")
        else:
            commit(" ".join(args[2:]))
    elif args[1] == "log":
        log()
    elif args[1] == "diff":
        diff()
    elif args[1] == "checkout":
        if len(args) < 3:
            print("Please provide a commit ID.")
        else:
            checkout(args[2])
