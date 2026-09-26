# LAN Code Editor

A small Flask app for editing UTF-8 text files on this PC from a phone or another device on the same Wi-Fi. It listens on port 7777 and only exposes folders explicitly added from the web interface.

## Start

Flask is the only dependency. If it is not installed in the Python environment you use, install it yourself:

    python -m pip install -r requirements.txt

Start the server:

    python app.py

The terminal prints the LAN addresses. Open an address such as http://192.168.0.101:7777 on your mobile device. No password is required.

Keep the server terminal running while you edit. Both devices must be on the same Wi-Fi. If Windows Firewall asks, allow Python on your private network. A firewall rule for TCP port 7777 may also be required.

## Use

1. On the PC, open http://127.0.0.1:7777 and select Add Project Folder.
2. Enter the absolute path of a folder on the PC.
   Set its URL path to a name such as ms1/temporary. For a folder that is already added, use the ↗ control beside it on the PC to change its URL path.
3. From Android, open the printed LAN address, browse added folders, tap a text file, edit it, then press Save.
4. Remove a folder from the sidebar to revoke access. This never deletes the folder or its files.

The root list is saved locally in folder_roots.json, which is ignored by Git. The browser does not receive the configured absolute paths.

## Direct URLs for AI agents

When adding a folder on the PC, give it a URL path such as ms1/tools. That maps the approved PC folder to:

    http://192.168.0.101:7777/ms1/tools/

Replace the example address with the LAN address printed by the server. A GET of a folder URL returns JSON entries with direct URLs. A GET of a file URL returns its UTF-8 text and includes an ETag revision plus an X-CSRF-Token response header.

An agent that can make HTTP requests can edit an existing file with PUT to its direct URL. Send a JSON body with content and revision, preserve the session cookie from the GET request, and send the X-CSRF-Token header returned by that GET. Saves are rejected if the file changed since it was read. The agent must be able to reach the private LAN address; public web search or chat alone cannot access it.

The Gemini CLI can also send shell commands directly through its `lan_workspace` tool using action `run`; it does not need to create a temporary script file. Commands use the PC shell and run with the selected shared folder as the working directory. The working directory does not restrict shell access to that folder.

## Access and limits

- The app binds to all network interfaces so other devices on the LAN can connect. Use it only on a trusted private Wi-Fi network.
- No password is required. Folder access can only be granted from the PC itself; devices on Wi-Fi can browse and edit folders already added. The command endpoint also allows reachable devices to execute commands as the PC user.
- File browsing and editing are restricted to configured roots. Shell commands are not sandboxed and can access anything the PC user can access.
- UTF-8 text files up to 2 MB can be edited, and new files can be created inside an added root. Binary files, deletion, and renaming are not supported.
- Before saving, the app checks whether the PC file changed since it was opened and refuses to overwrite a conflicting edit.
- Traffic uses HTTP on the local network. Avoid untrusted or public Wi-Fi.
- The built-in Flask server is intended for personal LAN use, not direct exposure to the public internet.
