from __future__ import annotations

import hashlib
import hmac
import ipaddress
import json
import os
import re
import secrets
import socket
import stat
import tempfile
import uuid
from functools import wraps
from pathlib import Path
from typing import Any, Callable
from urllib.parse import quote

from flask import Flask, abort, jsonify, render_template, request, session

BASE_DIR = Path(__file__).resolve().parent
ROOTS_FILE = BASE_DIR / "folder_roots.json"
MAX_EDIT_BYTES = 2 * 1024 * 1024
app = Flask(__name__)
app.secret_key = os.environ.get("FILE_EDITOR_SECRET") or secrets.token_hex(32)
app.config.update(
    MAX_CONTENT_LENGTH=MAX_EDIT_BYTES + 64 * 1024,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,
)
def load_roots() -> list[dict[str, str]]:
    try:
        data = json.loads(ROOTS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(data, list):
        return []
    return [
        {
            "id": str(x["id"]),
            "name": str(x["name"]),
            "path": str(x["path"]),
            "url_path": str(x.get("url_path") or re.sub(r"[^a-zA-Z0-9._-]+", "-", str(x["name"]).strip()).strip("-").lower()),
        }
        for x in data
        if isinstance(x, dict) and x.get("id") and x.get("name") and x.get("path")
    ]


def save_roots(roots: list[dict[str, str]]) -> None:
    temporary = ROOTS_FILE.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(roots, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(ROOTS_FILE)


def normalize_url_path(value: str) -> str:
    parts = value.strip().strip("/").split("/")
    if not parts or any(not re.fullmatch(r"[A-Za-z0-9._-]+", part) or part in {".", ".."} for part in parts):
        raise ValueError("URL path must contain simple folder names, for example ms1/tools.")
    if parts[0].lower() in {"api", "static"}:
        raise ValueError("URL path cannot start with api or static.")
    return "/".join(parts)


def find_root(root_id: str) -> Path:
    for item in load_roots():
        if item["id"] == root_id:
            root = Path(item["path"]).expanduser().resolve()
            if root.is_dir():
                return root
            abort(404, description="The configured folder is no longer available.")
    abort(404, description="Folder not found.")


def safe_path(root_id: str, relative: str) -> tuple[Path, Path]:
    root = find_root(root_id)
    clean = relative.replace("\\", "/")
    part = Path(clean)
    if part.is_absolute() or any(segment == ".." for segment in clean.split("/")):
        abort(400, description="Invalid relative path.")
    try:
        result = (root / part).resolve(strict=True)
        result.relative_to(root)
    except (OSError, ValueError):
        abort(400, description="Path is outside the selected folder or unavailable.")
    return root, result


def require_session(view: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(view)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        if not session.get("authenticated"):
            session["authenticated"] = True
            session["csrf_token"] = secrets.token_urlsafe(32)
        return view(*args, **kwargs)
    return wrapped


def require_csrf() -> None:
    token = str(session.get("csrf_token", ""))
    supplied = request.headers.get("X-CSRF-Token", "") or request.form.get("csrf", "")
    if not token or not hmac.compare_digest(token, supplied):
        abort(403, description="Request verification failed. Reload the page and try again.")


@app.after_request
def security_headers(response: Any) -> Any:
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
        "connect-src 'self'; frame-ancestors 'none'; base-uri 'self'"
    )
    return response


@app.errorhandler(413)
def too_large(_: Any) -> tuple[Any, int]:
    return jsonify(error="Request exceeds the 2 MB editing limit."), 413


@app.get("/")
@require_session
def index() -> Any:
    try:
        can_add_roots = ipaddress.ip_address(request.remote_addr or "").is_loopback
    except ValueError:
        can_add_roots = False
    return render_template(
        "index.html",
        csrf_token=session["csrf_token"],
        can_add_roots=can_add_roots,
    )


@app.get("/api/roots")
@require_session
def roots_list() -> Any:
    return jsonify(roots=[
        {"id": x["id"], "name": x["name"], "url_path": x["url_path"]}
        for x in load_roots()
    ])


@app.post("/api/roots")
@require_session
def roots_add() -> Any:
    require_csrf()
    try:
        is_local_request = ipaddress.ip_address(request.remote_addr or "").is_loopback
    except ValueError:
        is_local_request = False
    if not is_local_request:
        return jsonify(error="Add folders from the PC using http://127.0.0.1:7777. Android can edit added folders."), 403
    data = request.get_json(silent=True) or {}
    raw = str(data.get("path", "")).strip()
    name = str(data.get("name", "")).strip()
    raw_url_path = str(data.get("url_path", "")).strip()
    try:
        path = Path(raw).expanduser().resolve(strict=True)
    except (OSError, RuntimeError):
        return jsonify(error="That folder path does not exist or cannot be accessed."), 400
    if not path.is_dir():
        return jsonify(error="The selected path is not a folder."), 400
    if not name:
        name = path.name or str(path)
    if not raw_url_path:
        raw_url_path = re.sub(r"[^a-zA-Z0-9._-]+", "-", name).strip("-").lower() or "project"
    try:
        url_path = normalize_url_path(raw_url_path)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    roots = load_roots()
    normalized = os.path.normcase(str(path))
    if any(os.path.normcase(str(Path(x["path"]).resolve())) == normalized for x in roots):
        return jsonify(error="That folder is already added."), 409
    if any(x["url_path"].lower() == url_path.lower() for x in roots):
        return jsonify(error="That URL path is already in use."), 409
    root = {
        "id": uuid.uuid4().hex,
        "name": name[:60],
        "path": str(path),
        "url_path": url_path,
    }
    roots.append(root)
    save_roots(roots)
    return jsonify(root={"id": root["id"], "name": root["name"], "url_path": root["url_path"]})


@app.delete("/api/roots/<root_id>")
@require_session
def roots_remove(root_id: str) -> Any:
    require_csrf()
    roots = load_roots()
    updated = [x for x in roots if x["id"] != root_id]
    if len(updated) == len(roots):
        return jsonify(error="Folder not found."), 404
    save_roots(updated)
    return jsonify(ok=True)


@app.get("/api/tree")
@require_session
def tree() -> Any:
    root_id, relative = request.args.get("root", ""), request.args.get("path", "")
    root, directory = safe_path(root_id, relative)
    if not directory.is_dir():
        return jsonify(error="That path is not a folder."), 400
    entries = []
    try:
        for child in sorted(directory.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower())):
            try:
                resolved = child.resolve(strict=True)
                resolved.relative_to(root)
                is_dir = resolved.is_dir()
                info = resolved.stat()
            except (OSError, ValueError):
                continue
            entries.append({
                "name": child.name,
                "path": child.relative_to(root).as_posix(),
                "kind": "directory" if is_dir else "file",
                "size": None if is_dir else info.st_size,
            })
    except OSError:
        return jsonify(error="Could not read this folder."), 400
    return jsonify(entries=entries)


@app.get("/api/file")
@require_session
def file_read() -> Any:
    root, path = safe_path(request.args.get("root", ""), request.args.get("path", ""))
    del root
    if not path.is_file():
        return jsonify(error="That path is not a file."), 400
    try:
        raw = path.read_bytes()
        if len(raw) > MAX_EDIT_BYTES:
            return jsonify(error="File is larger than 2 MB and cannot be opened here."), 413
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        return jsonify(error="This is not a UTF-8 text file."), 415
    except OSError:
        return jsonify(error="Could not read this file."), 400
    return jsonify(content=content, revision=hashlib.sha256(raw).hexdigest())


@app.put("/api/file")
@require_session
def file_save() -> Any:
    require_csrf()
    data = request.get_json(silent=True) or {}
    root_id, relative = str(data.get("root", "")), str(data.get("path", ""))
    content, revision = data.get("content"), str(data.get("revision", ""))
    if not isinstance(content, str):
        return jsonify(error="File content must be text."), 400
    encoded = content.encode("utf-8")
    if len(encoded) > MAX_EDIT_BYTES:
        return jsonify(error="Files must be at most 2 MB."), 413
    _, path = safe_path(root_id, relative)
    if not path.is_file():
        return jsonify(error="That path is not a file."), 400
    temporary_path: Path | None = None
    try:
        current = path.read_bytes()
        if hashlib.sha256(current).hexdigest() != revision:
            return jsonify(error="This file changed on the PC since you opened it. Reload before saving."), 409
        mode = stat.S_IMODE(path.stat().st_mode)
        with tempfile.NamedTemporaryFile(mode="wb", dir=path.parent, prefix=".lan-edit-", delete=False) as handle:
            handle.write(encoded)
            temporary_path = Path(handle.name)
        os.chmod(temporary_path, mode)
        temporary_path.replace(path)
    except OSError:
        if temporary_path:
            temporary_path.unlink(missing_ok=True)
        return jsonify(error="Could not save this file."), 400
    return jsonify(revision=hashlib.sha256(encoded).hexdigest(), saved=True)


@app.route("/<path:virtual_path>", methods=["GET", "PUT"])
@require_session
def direct_folder_access(virtual_path: str) -> Any:
    requested = virtual_path.strip("/")
    roots = sorted(load_roots(), key=lambda item: len(item["url_path"]), reverse=True)
    selected = None
    relative = ""
    for item in roots:
        prefix = item["url_path"].strip("/")
        if requested == prefix:
            selected, relative = item, ""
            break
        if requested.startswith(prefix + "/"):
            selected, relative = item, requested[len(prefix) + 1:]
            break
    if selected is None:
        abort(404, description="No added folder is mapped to this URL.")

    root, path = safe_path(selected["id"], relative)
    csrf = session["csrf_token"]
    if request.method == "GET":
        if path.is_dir():
            entries = []
            try:
                for child in sorted(path.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower())):
                    try:
                        resolved = child.resolve(strict=True)
                        resolved.relative_to(root)
                        is_directory = resolved.is_dir()
                        info = resolved.stat()
                    except (OSError, ValueError):
                        continue
                    child_relative = child.relative_to(root).as_posix()
                    entries.append({
                        "name": child.name,
                        "kind": "directory" if is_directory else "file",
                        "size": None if is_directory else info.st_size,
                        "url": "/" + quote(selected["url_path"] + "/" + child_relative, safe="/"),
                    })
            except OSError:
                abort(400, description="Could not read this folder.")
            response = jsonify(
                kind="directory",
                path="/" + quote(selected["url_path"] + (("/" + relative) if relative else ""), safe="/"),
                entries=entries,
            )
        else:
            if not path.is_file():
                abort(400, description="This path is not a file or folder.")
            try:
                raw = path.read_bytes()
                if len(raw) > MAX_EDIT_BYTES:
                    abort(413, description="File is larger than 2 MB.")
                content = raw.decode("utf-8")
            except UnicodeDecodeError:
                abort(415, description="This file is not UTF-8 text.")
            response = app.response_class(content, mimetype="text/plain")
            response.headers["ETag"] = '"' + hashlib.sha256(raw).hexdigest() + '"'
        response.headers["X-CSRF-Token"] = csrf
        response.headers["Cache-Control"] = "no-store"
        return response

    require_csrf()
    if not path.is_file():
        abort(400, description="Only existing text files can be edited.")
    data = request.get_json(silent=True)
    content = data.get("content") if isinstance(data, dict) else request.get_data(as_text=True)
    expected = str(data.get("revision", "")) if isinstance(data, dict) else request.headers.get("If-Match", "").strip('"')
    if not isinstance(content, str):
        abort(400, description="Send UTF-8 text as the request body or JSON content field.")
    encoded = content.encode("utf-8")
    if len(encoded) > MAX_EDIT_BYTES:
        abort(413, description="Files must be at most 2 MB.")
    try:
        current = path.read_bytes()
        if hashlib.sha256(current).hexdigest() != expected:
            return jsonify(error="File changed since it was read. GET it again before saving."), 409
        mode = stat.S_IMODE(path.stat().st_mode)
        with tempfile.NamedTemporaryFile(mode="wb", dir=path.parent, prefix=".lan-edit-", delete=False) as handle:
            handle.write(encoded)
            temporary = Path(handle.name)
        os.chmod(temporary, mode)
        temporary.replace(path)
    except OSError:
        try:
            temporary.unlink(missing_ok=True)
        except (OSError, UnboundLocalError):
            pass
        abort(400, description="Could not save this file.")
    revision = hashlib.sha256(encoded).hexdigest()
    response = jsonify(saved=True, revision=revision)
    response.headers["ETag"] = '"' + revision + '"'
    response.headers["X-CSRF-Token"] = csrf
    return response


def local_addresses() -> list[str]:
    addresses: set[str] = set()
    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            probe.connect(("192.0.2.1", 80))
            addresses.add(probe.getsockname()[0])
        finally:
            probe.close()
    except OSError:
        pass
    try:
        for result in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            address = result[4][0]
            if not ipaddress.ip_address(address).is_loopback:
                addresses.add(address)
    except OSError:
        pass
    return sorted(addresses)


if __name__ == "__main__":
    print("LAN Code Editor")
    print("Open one of these addresses from another device on this Wi-Fi:")
    for address in local_addresses():
        print(f"  http://{address}:7777")
    print("No password is required. Add folders from this PC at http://127.0.0.1:7777")
    app.run(host="0.0.0.0", port=7777, debug=False, threaded=True)
