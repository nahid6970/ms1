"use strict";

const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
const canManageRoots = document.body.dataset.canManageRoots === "true";
const state = { roots: [], root: null, folder: "", file: "", revision: "", dirty: false };
const $ = (id) => document.getElementById(id);

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[char]);
}

async function request(url, options = {}) {
  const headers = Object.assign({}, options.headers || {});
  if (options.body) headers["Content-Type"] = "application/json";
  if (options.method && options.method !== "GET") headers["X-CSRF-Token"] = csrfToken;
  const response = await fetch(url, Object.assign({}, options, { headers }));
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || ("Request failed (" + response.status + ")."));
  return data;
}

function showNotice(message, kind) {
  const box = $("notice");
  box.textContent = message;
  box.className = "notice toast " + (kind || "");
  clearTimeout(showNotice.timer);
  showNotice.timer = setTimeout(() => box.classList.add("hidden"), 4500);
}

function setSaveState(text, kind) {
  $("save-state").textContent = text;
  $("save-state").className = "save-state " + (kind || "");
}

function markDirty() {
  state.dirty = true;
  setSaveState("UNSAVED CHANGES", "warning");
  $("save-file").disabled = false;
}

async function loadRoots() {
  try {
    state.roots = (await request("/api/roots")).roots;
    renderRoots();
  } catch (error) {
    showNotice(error.message, "error");
  }
}

function renderRoots() {
  const list = $("root-list");
  if (!state.roots.length) {
    list.innerHTML = '<div class="empty">No project folders added yet.</div>';
    $("welcome").classList.remove("hidden");
    $("editor-shell").classList.add("hidden");
    return;
  }
  list.innerHTML = state.roots.map((root) =>
    '<div class="root-row ' + (state.root === root.id ? "active" : "") + '">' +
    '<button class="root-select" data-root="' + escapeHtml(root.id) + '">' +
    '<span class="folder-icon">▰</span><span class="root-label"><strong>' + escapeHtml(root.name) +
    '</strong><small>/' + escapeHtml(root.url_path) + '/</small></span></button>' +
    (canManageRoots ? '<button class="root-url-edit" data-url-edit="' + escapeHtml(root.id) + '" title="Change URL path">↗</button>' : "") +
    '<button class="root-remove" data-remove="' + escapeHtml(root.id) + '" title="Remove access">×</button></div>'
  ).join("");
  list.querySelectorAll("[data-root]").forEach((button) =>
    button.addEventListener("click", () => selectRoot(button.dataset.root)));
  list.querySelectorAll("[data-remove]").forEach((button) =>
    button.addEventListener("click", () => removeRoot(button.dataset.remove)));
  list.querySelectorAll("[data-url-edit]").forEach((button) =>
    button.addEventListener("click", () => editRootUrl(button.dataset.urlEdit)));
}

async function editRootUrl(rootId) {
  const root = state.roots.find((item) => item.id === rootId);
  if (!root) return;
  const urlPath = window.prompt("URL path for this folder (example: ms1/temporary):", root.url_path);
  if (urlPath === null || !urlPath.trim() || urlPath.trim() === root.url_path) return;
  try {
    await request("/api/roots/" + encodeURIComponent(rootId), {
      method: "PUT",
      body: JSON.stringify({ url_path: urlPath.trim() })
    });
    await loadRoots();
    showNotice("Folder URL updated to /" + urlPath.trim() + "/", "success");
  } catch (error) {
    showNotice(error.message, "error");
  }
}

function confirmDiscard() {
  return !state.dirty || window.confirm("Discard your unsaved changes?");
}

async function selectRoot(rootId) {
  if (!confirmDiscard()) return;
  state.root = rootId;
  state.folder = "";
  state.file = "";
  state.dirty = false;
  state.revision = "";
  renderRoots();
  $("welcome").classList.add("hidden");
  $("editor-shell").classList.add("hidden");
  await loadFolder("");
}

async function loadFolder(path) {
  if (!state.root) return;
  try {
    const query = "?root=" + encodeURIComponent(state.root) + "&path=" + encodeURIComponent(path);
    const data = await request("/api/tree" + query);
    state.folder = path;
    state.file = "";
    renderTree(data.entries);
  } catch (error) {
    showNotice(error.message, "error");
  }
}

function renderTree(entries) {
  const crumbs = [];
  if (state.root) {
    const root = state.roots.find((item) => item.id === state.root);
    crumbs.push('<button data-crumb="">' + escapeHtml(root ? root.name : "PROJECT") + '</button>');
  }
  let current = "";
  state.folder.split("/").filter(Boolean).forEach((part) => {
    current = current ? current + "/" + part : part;
    crumbs.push('<span>/</span><button data-crumb="' + escapeHtml(current) + '">' + escapeHtml(part) + '</button>');
  });
  $("breadcrumbs").innerHTML = crumbs.join("");
  $("breadcrumbs").querySelectorAll("[data-crumb]").forEach((button) =>
    button.addEventListener("click", async () => {
      if (confirmDiscard()) await loadFolder(button.dataset.crumb);
    }));

  let tree = document.querySelector(".file-tree");
  if (!tree) {
    tree = document.createElement("div");
    tree.className = "file-tree";
    document.querySelector(".sidebar").insertBefore(tree, document.querySelector(".sidebar-foot"));
  }
  const parentPath = state.folder.split("/").slice(0, -1).join("/");
  const parent = state.folder
    ? '<button class="tree-entry folder-entry" data-folder="' + escapeHtml(parentPath) + '"><span>↰</span> ..</button>'
    : "";
  const rows = entries.map((entry) => {
    const isDirectory = entry.kind === "directory";
    const key = isDirectory ? "folder" : "file";
    const size = isDirectory ? "" : "<small>" + formatSize(entry.size) + "</small>";
    return '<button class="tree-entry ' + (isDirectory ? "folder-entry" : "file-entry") +
      (state.file === entry.path ? " selected" : "") + '" data-' + key + '="' +
      escapeHtml(entry.path) + '"><span>' + (isDirectory ? "▰" : "·") +
      '</span><span class="entry-name">' + escapeHtml(entry.name) + "</span>" + size + "</button>";
  }).join("");
  tree.innerHTML = parent + (rows || '<div class="empty tree-empty">This folder is empty.</div>');
  tree.querySelectorAll("[data-folder]").forEach((button) =>
    button.addEventListener("click", async () => {
      if (confirmDiscard()) await loadFolder(button.dataset.folder);
    }));
  tree.querySelectorAll("[data-file]").forEach((button) =>
    button.addEventListener("click", async () => {
      if (confirmDiscard()) await openFile(button.dataset.file);
    }));
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + " B";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
  return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}

async function openFile(path) {
  try {
    const query = "?root=" + encodeURIComponent(state.root) + "&path=" + encodeURIComponent(path);
    const data = await request("/api/file" + query);
    state.file = path;
    state.revision = data.revision;
    state.dirty = false;
    $("editor").value = data.content;
    $("file-name").textContent = path.split("/").pop();
    $("file-path").textContent = path;
    $("editor-shell").classList.remove("hidden");
    $("welcome").classList.add("hidden");
    $("save-file").disabled = true;
    $("reload-file").disabled = false;
    setSaveState("ALL CHANGES SAVED", "success");
    renderTreeStatus();
  } catch (error) {
    showNotice(error.message, "error");
  }
}

function renderTreeStatus() {
  document.querySelectorAll(".tree-entry[data-file]").forEach((button) =>
    button.classList.toggle("selected", button.dataset.file === state.file));
}

async function saveFile() {
  if (!state.file || !state.root || !state.dirty) return;
  $("save-file").disabled = true;
  setSaveState("SAVING…", "");
  try {
    const data = await request("/api/file", {
      method: "PUT",
      body: JSON.stringify({
        root: state.root, path: state.file, content: $("editor").value, revision: state.revision
      })
    });
    state.revision = data.revision;
    state.dirty = false;
    setSaveState("ALL CHANGES SAVED", "success");
    showNotice("Saved to the PC.", "success");
  } catch (error) {
    $("save-file").disabled = false;
    setSaveState(error.message.includes("changed on the PC") ? "FILE CONFLICT" : "SAVE FAILED", "error");
    showNotice(error.message, "error");
  }
}

async function reloadFile() {
  if (state.file && confirmDiscard()) await openFile(state.file);
}

async function removeRoot(rootId) {
  const root = state.roots.find((item) => item.id === rootId);
  if (!root || !window.confirm('Remove access to "' + root.name + '"? The files will not be deleted.')) return;
  try {
    await request("/api/roots/" + encodeURIComponent(rootId), { method: "DELETE" });
    if (state.root === rootId) {
      state.root = null;
      state.file = "";
      state.dirty = false;
      $("editor-shell").classList.add("hidden");
      $("welcome").classList.remove("hidden");
      document.querySelector(".file-tree")?.remove();
    }
    await loadRoots();
    showNotice("Folder access removed. Files were not changed.", "success");
  } catch (error) {
    showNotice(error.message, "error");
  }
}

const dialog = $("add-root-dialog");
function openAddDialog() {
  if (!dialog) return;
  dialog.showModal();
  $("root-path").focus();
}
function closeAddDialog() { dialog.close(); }

 $("add-root-open")?.addEventListener("click", openAddDialog);
 $("add-root-welcome")?.addEventListener("click", openAddDialog);
 $("add-root-close")?.addEventListener("click", closeAddDialog);
 $("cancel-root")?.addEventListener("click", closeAddDialog);
$("editor").addEventListener("input", markDirty);
$("save-file").addEventListener("click", saveFile);
$("reload-file").addEventListener("click", reloadFile);
$("add-root-form")?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = event.currentTarget.querySelector('[type="submit"]');
  button.disabled = true;
  try {
    const data = await request("/api/roots", {
      method: "POST",
      body: JSON.stringify({
        name: $("root-name").value, path: $("root-path").value, url_path: $("root-url").value
      })
    });
    closeAddDialog();
    $("add-root-form").reset();
    await loadRoots();
    await selectRoot(data.root.id);
    showNotice('Added "' + data.root.name + '".', "success");
  } catch (error) {
    showNotice(error.message, "error");
  } finally {
    button.disabled = false;
  }
});
document.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "s") {
    event.preventDefault();
    saveFile();
  }
});

loadRoots();
