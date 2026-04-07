import { ConvexHttpClient } from "convex/browser";

// --- CONFIGURATION ---
const CONVEX_URL = import.meta.env.VITE_CONVEX_URL; 
const client = new ConvexHttpClient(CONVEX_URL);

// --- STATE ---
let masterKey = null;
let vaultEntries = [];
let currentGroup = "ALL ENTRIES";
let editingEntryId = null;
let unlockTime = null;
let settings = { autolock: 0, autodomain: true };

// --- DOM ELEMENTS ---
const loginContainer = document.getElementById('login-container');
const vaultContainer = document.getElementById('vault-container');
const masterPassInput = document.getElementById('master-password');
const loginBtn = document.getElementById('login-btn');
const entriesList = document.getElementById('entries-list');
const groupListContainer = document.getElementById('group-list');
const currentGroupLabel = document.getElementById('current-group-label');

const addModal = document.getElementById('add-modal');
const editModal = document.getElementById('edit-modal');
const settingsModal = document.getElementById('settings-modal');

// --- INITIALIZE ---
async function init() {
    const result = await chrome.storage.local.get(['vaultSettings', 'sessionData']);
    if (result.vaultSettings) {
        settings = result.vaultSettings;
        document.getElementById('setting-autolock').value = settings.autolock;
        document.getElementById('setting-autodomain').checked = settings.autodomain;
    }
    if (result.sessionData && result.sessionData.unlockTime && result.sessionData.masterKey) {
        const elapsed = (Date.now() - result.sessionData.unlockTime) / 60000;
        if (settings.autolock === 0 || elapsed < settings.autolock) {
            masterKey = result.sessionData.masterKey;
            unlockTime = result.sessionData.unlockTime;
            loginContainer.classList.add('hidden');
            vaultContainer.classList.remove('hidden');
            loadVault();
        } else {
            chrome.storage.local.remove('sessionData');
        }
    }
}
init();

// Auto-lock checker
setInterval(() => {
    if (masterKey && settings.autolock > 0 && unlockTime) {
        const elapsed = (Date.now() - unlockTime) / 60000;
        if (elapsed >= settings.autolock) {
            chrome.storage.local.remove('sessionData');
            logout();
        }
    }
}, 10000);

function resetActivityTimer() {
    if (masterKey) {
        unlockTime = Date.now();
        chrome.storage.local.set({ sessionData: { unlockTime, masterKey } });
    }
}

// Global activity listeners
window.addEventListener('click', resetActivityTimer);
window.addEventListener('keypress', resetActivityTimer);
window.addEventListener('mousemove', resetActivityTimer);

// --- CRYPTO HELPERS ---
async function deriveKey(password, salt) {
    const enc = new TextEncoder();
    const keyMaterial = await crypto.subtle.importKey("raw", enc.encode(password), { name: "PBKDF2" }, false, ["deriveKey"]);
    return crypto.subtle.deriveKey(
        { name: "PBKDF2", salt: salt, iterations: 100000, hash: "SHA-256" },
        keyMaterial, { name: "AES-GCM", length: 256 }, false, ["encrypt", "decrypt"]
    );
}

async function encrypt(text, password, existingSalt = null, existingIv = null) {
    const salt = existingSalt || crypto.getRandomValues(new Uint8Array(16));
    const iv = existingIv || crypto.getRandomValues(new Uint8Array(12));
    const key = await deriveKey(password, salt);
    const encrypted = await crypto.subtle.encrypt({ name: "AES-GCM", iv: iv }, key, new TextEncoder().encode(text));
    return { salt, iv, data: btoa(String.fromCharCode(...new Uint8Array(encrypted))) };
}

async function decrypt(bundle, password) {
    try {
        const salt = new Uint8Array(atob(bundle.salt).split("").map(c => c.charCodeAt(0)));
        const iv = new Uint8Array(atob(bundle.iv).split("").map(c => c.charCodeAt(0)));
        const data = new Uint8Array(atob(bundle.data).split("").map(c => c.charCodeAt(0)));
        const key = await deriveKey(password, salt);
        const decrypted = await crypto.subtle.decrypt({ name: "AES-GCM", iv: iv }, key, data);
        return new TextDecoder().decode(decrypted);
    } catch (e) { return null; }
}

// --- APP LOGIC ---
async function handleLogin() {
    const password = masterPassInput.value;
    if (!password) return;
    loginBtn.disabled = true;
    try {
        const canary = await client.query("passwords:getCanary");
        if (canary) {
            const dec = await decrypt({ salt: canary.salt, iv: canary.iv, data: canary.p }, password);
            if (dec !== "CANARY_OK") { alert("INVALID PASSWORD"); loginBtn.disabled = false; return; }
        } else {
            if (confirm("Initialize new vault?")) {
                const enc = await encrypt("CANARY_OK", password);
                await client.mutation("passwords:add", { domain: "SYSTEM_CANARY", salt: btoa(String.fromCharCode(...enc.salt)), iv: btoa(String.fromCharCode(...enc.iv)), u: "SYSTEM", p: enc.data, fields: "{}" });
            } else { loginBtn.disabled = false; return; }
        }
        masterKey = password;
        unlockTime = Date.now();
        chrome.storage.local.set({ sessionData: { unlockTime, masterKey: password } });
        loginContainer.classList.add('hidden');
        vaultContainer.classList.remove('hidden');
        loadVault();
    } catch (e) { alert("CONNECTION ERROR"); loginBtn.disabled = false; }
}

async function loadVault() {
    try {
        const records = await client.query("passwords:list");
        vaultEntries = [];
        for (const r of records) {
            if (r.domain === "SYSTEM_CANARY") continue;
            const u = await decrypt({ salt: r.salt, iv: r.iv, data: r.u }, masterKey);
            const p = await decrypt({ salt: r.salt, iv: r.iv, data: r.p }, masterKey);
            if (u !== null && p !== null) vaultEntries.push({ id: r._id, domain: r.domain, u, p, fields: JSON.parse(r.fields || "{}"), salt: r.salt, iv: r.iv });
        }
        updateSuggestions();
        renderGroups();
        if (settings.autodomain) await prefillSearchFromCurrentTab();
        renderEntries();
    } catch (e) { console.error(e); }
}

async function prefillSearchFromCurrentTab() {
    if (typeof chrome !== 'undefined' && chrome.tabs) {
        const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
        if (tabs[0] && tabs[0].url) {
            try {
                const url = new URL(tabs[0].url);
                let domain = url.hostname;
                if (domain.startsWith('www.')) domain = domain.substring(4);
                if (domain && !domain.includes('newtab')) document.getElementById('global-search').value = domain;
            } catch (e) {}
        }
    }
}

function updateSuggestions() {
    const suggestions = new Set(["Note", "Phone", "Domain", "Email", "URL"]);
    vaultEntries.forEach(e => Object.keys(e.fields).forEach(k => suggestions.add(k)));
    const html = Array.from(suggestions).sort().map(s => `<option value="${s}">`).join('');
    document.getElementById('field-suggestions').innerHTML = html;
    document.getElementById('edit-field-suggestions').innerHTML = html;
}

function renderGroups() {
    const groups = new Set(["ALL ENTRIES"]);
    vaultEntries.forEach(e => groups.add(e.domain));
    groupListContainer.innerHTML = '';
    Array.from(groups).sort().forEach(g => {
        const div = document.createElement('div');
        div.className = `group-item ${currentGroup === g ? 'active' : ''}`;
        div.innerText = g;
        div.onclick = () => { currentGroup = g; currentGroupLabel.innerText = g; renderGroups(); renderEntries(); };
        groupListContainer.appendChild(div);
    });
}

function renderEntries() {
    const query = document.getElementById('global-search').value.toLowerCase();
    entriesList.innerHTML = '';
    const filtered = vaultEntries.filter(e => (currentGroup === "ALL ENTRIES" || e.domain === currentGroup) && (e.domain.toLowerCase().includes(query) || e.u.toLowerCase().includes(query)));

    if (filtered.length === 0) entriesList.innerHTML = '<div style="text-align:center; padding:20px; color:var(--cp-subtext);">NO ENTRIES</div>';

    filtered.forEach(e => {
        const div = document.createElement('div');
        div.className = 'entry-item';
        div.innerHTML = `
            <div class="entry-header">
                <div class="entry-info"><div class="entry-domain">${e.domain}</div><div class="entry-user">${e.u}</div></div>
                <div class="entry-actions">
                    <button class="copy-user" data-val="${e.u}">USER</button>
                    <button class="copy-pass" data-val="${e.p}">PASS</button>
                    <button class="edit-btn">EDIT</button>
                    <button class="del-btn danger">X</button>
                </div>
            </div>
            ${Object.keys(e.fields).length ? '<div class="details-toggle">▼ DETAILS ▼</div>' : ''}
            <div class="entry-details hidden">
                ${Object.entries(e.fields).map(([k,v]) => `<div class="detail-row"><span class="detail-label">${k}:</span><span>${v}</span><button class="copy-field" data-val="${v}">COPY</button></div>`).join('')}
            </div>
        `;
        const toggle = div.querySelector('.details-toggle');
        if (toggle) toggle.onclick = () => {
            const det = div.querySelector('.entry-details');
            const h = det.classList.toggle('hidden');
            toggle.innerText = h ? "▼ DETAILS ▼" : "▲ HIDE ▲";
        };
        div.querySelector('.copy-user').onclick = () => copy(e.u);
        div.querySelector('.copy-pass').onclick = () => copy(e.p);
        
        div.querySelectorAll('.copy-field').forEach(btn => {
            btn.onclick = () => copy(btn.dataset.val);
        });
        
        div.querySelector('.edit-btn').onclick = () => openEditModal(e);
        div.querySelector('.del-btn').onclick = async () => { if(confirm("Delete?")) { await client.mutation("passwords:remove", {id: e.id}); loadVault(); } };
        entriesList.appendChild(div);
    });
}

function copy(t) { navigator.clipboard.writeText(t); }

function logout() { chrome.storage.local.remove('sessionData'); location.reload(); }

// --- MODALS ---
function openEditModal(e) {
    editingEntryId = e.id;
    document.getElementById('edit-domain').value = e.domain;
    document.getElementById('edit-username').value = e.u;
    document.getElementById('edit-password').value = e.p;
    document.getElementById('edit-custom-fields').innerHTML = '';
    Object.entries(e.fields).forEach(([k,v]) => createFieldRow('edit-custom-fields', k, v));
    editModal.classList.remove('hidden');
}

function createFieldRow(containerId, name, value = "") {
    const row = document.createElement('div');
    row.className = 'custom-field-row';
    row.innerHTML = `<input type="text" class="field-name" value="${name}" readonly style="width:80px; color:var(--cp-yellow);"><input type="text" class="field-value" value="${value}"><button class="remove-field-btn danger">X</button>`;
    row.querySelector('.remove-field-btn').onclick = () => row.remove();
    document.getElementById(containerId).appendChild(row);
}

// --- PASSWORD GENERATOR (Python Style) ---
function generatePassword() {
    const length = parseInt(document.getElementById('gen-length').value);
    let chars = "abcdefghijklmnopqrstuvwxyz";
    if (document.getElementById('gen-upper').checked) chars += "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    if (document.getElementById('gen-nums').checked) chars += "0123456789";
    if (document.getElementById('gen-syms').checked) chars += "!@#$%^&*()_+-=[]{}|;:,.<>?";
    
    let pass = "";
    for (let i = 0; i < length; i++) pass += chars.charAt(Math.floor(Math.random() * chars.length));
    document.getElementById('new-password').value = pass;
    document.getElementById('new-password').type = 'text';
}

// --- EVENTS ---
loginBtn.onclick = handleLogin;
masterPassInput.onkeypress = (e) => { if(e.key==='Enter') handleLogin(); };

document.getElementById('logout-btn').onclick = logout;
document.getElementById('settings-btn').onclick = () => settingsModal.classList.remove('hidden');
document.getElementById('add-btn').onclick = () => addModal.classList.remove('hidden');

// Add Form
document.getElementById('save-btn').onclick = async () => {
    const domain = document.getElementById('new-domain').value || "UNCATEGORIZED";
    const u = document.getElementById('new-username').value;
    const p = document.getElementById('new-password').value;
    if(!u || !p) return alert("Required fields missing");
    const fields = {};
    document.querySelectorAll('#new-custom-fields .custom-field-row').forEach(row => { fields[row.querySelector('.field-name').value] = row.querySelector('.field-value').value; });
    const b = await encrypt(u, masterKey);
    const eP = await encrypt(p, masterKey, b.salt, b.iv);
    await client.mutation("passwords:add", { domain: domain.toUpperCase(), salt: btoa(String.fromCharCode(...b.salt)), iv: btoa(String.fromCharCode(...b.iv)), u: b.data, p: eP.data, fields: JSON.stringify(fields) });
    addModal.classList.add('hidden');
    loadVault();
};
document.getElementById('close-add-modal-btn').onclick = () => addModal.classList.add('hidden');
document.getElementById('add-field-btn').onclick = () => { const n = document.getElementById('new-field-name'); if(n.value) { createFieldRow('new-custom-fields', n.value); n.value = ''; } };

// Generator Panel
document.getElementById('gen-options-btn').onclick = () => document.getElementById('gen-options-panel').classList.toggle('hidden');
document.getElementById('gen-length').oninput = (e) => document.getElementById('gen-len-val').innerText = e.target.value;
document.getElementById('gen-execute-btn').onclick = generatePassword;

// Edit Form
document.getElementById('update-btn').onclick = async () => {
    const domain = document.getElementById('edit-domain').value.toUpperCase();
    const u = document.getElementById('edit-username').value;
    const p = document.getElementById('edit-password').value;
    const fields = {};
    document.querySelectorAll('#edit-custom-fields .custom-field-row').forEach(row => { fields[row.querySelector('.field-name').value] = row.querySelector('.field-value').value; });
    const b = await encrypt(u, masterKey);
    const eP = await encrypt(p, masterKey, b.salt, b.iv);
    await client.mutation("passwords:update", { id: editingEntryId, domain, salt: btoa(String.fromCharCode(...b.salt)), iv: btoa(String.fromCharCode(...b.iv)), u: b.data, p: eP.data, fields: JSON.stringify(fields) });
    editModal.classList.add('hidden');
    loadVault();
};
document.getElementById('close-modal-btn').onclick = () => editModal.classList.add('hidden');
document.getElementById('edit-add-field-btn').onclick = () => { const n = document.getElementById('edit-new-field-name'); if(n.value) { createFieldRow('edit-custom-fields', n.value); n.value = ''; } };

// Settings
document.getElementById('save-settings-btn').onclick = () => {
    settings.autolock = parseInt(document.getElementById('setting-autolock').value);
    settings.autodomain = document.getElementById('setting-autodomain').checked;
    chrome.storage.local.set({ vaultSettings: settings });
    settingsModal.classList.add('hidden');
    loadVault();
};
document.getElementById('close-settings-btn').onclick = () => settingsModal.classList.add('hidden');

document.getElementById('global-search').oninput = renderEntries;
