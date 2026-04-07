import { ConvexHttpClient } from "convex/browser";

// --- CONFIGURATION ---
const CONVEX_URL = import.meta.env.VITE_CONVEX_URL; 
const client = new ConvexHttpClient(CONVEX_URL);

// --- STATE ---
let masterKey = null;
let vaultEntries = [];
let currentGroup = "ALL ENTRIES";

// --- DOM ELEMENTS ---
const loginContainer = document.getElementById('login-container');
const vaultContainer = document.getElementById('vault-container');
const masterPassInput = document.getElementById('master-password');
const loginBtn = document.getElementById('login-btn');
const logoutBtn = document.getElementById('logout-btn');
const saveBtn = document.getElementById('save-btn');
const genBtn = document.getElementById('gen-btn');
const searchInput = document.getElementById('global-search');
const entriesList = document.getElementById('entries-list');
const groupListContainer = document.getElementById('group-list');
const currentGroupLabel = document.getElementById('current-group-label');

// --- CRYPTO HELPERS ---
async function deriveKey(password, salt) {
    const enc = new TextEncoder();
    const keyMaterial = await crypto.subtle.importKey(
        "raw",
        enc.encode(password),
        { name: "PBKDF2" },
        false,
        ["deriveKey"]
    );
    return crypto.subtle.deriveKey(
        {
            name: "PBKDF2",
            salt: salt,
            iterations: 100000,
            hash: "SHA-256"
        },
        keyMaterial,
        { name: "AES-GCM", length: 256 },
        false,
        ["encrypt", "decrypt"]
    );
}

async function encrypt(text, password, existingSalt = null, existingIv = null) {
    const salt = existingSalt || crypto.getRandomValues(new Uint8Array(16));
    const iv = existingIv || crypto.getRandomValues(new Uint8Array(12));
    const key = await deriveKey(password, salt);
    const enc = new TextEncoder();
    const encrypted = await crypto.subtle.encrypt(
        { name: "AES-GCM", iv: iv },
        key,
        enc.encode(text)
    );

    return {
        salt: salt,
        iv: iv,
        data: btoa(String.fromCharCode(...new Uint8Array(encrypted)))
    };
}

async function decrypt(bundle, password) {
    try {
        const salt = new Uint8Array(atob(bundle.salt).split("").map(c => c.charCodeAt(0)));
        const iv = new Uint8Array(atob(bundle.iv).split("").map(c => c.charCodeAt(0)));
        const data = new Uint8Array(atob(bundle.data).split("").map(c => c.charCodeAt(0)));
        const key = await deriveKey(password, salt);
        
        const decrypted = await crypto.subtle.decrypt(
            { name: "AES-GCM", iv: iv },
            key,
            data
        );
        return new TextDecoder().decode(decrypted);
    } catch (e) {
        return null;
    }
}

// --- APP LOGIC ---
async function handleLogin() {
    const password = masterPassInput.value;
    if (!password) return;

    loginBtn.disabled = true;
    loginBtn.innerText = "VERIFYING...";

    try {
        const canary = await client.query("passwords:getCanary");
        
        if (canary) {
            const decrypted = await decrypt({ salt: canary.salt, iv: canary.iv, data: canary.p }, password);
            if (decrypted !== "CANARY_OK") {
                alert("ACCESS DENIED: INVALID MASTER PASSWORD");
                loginBtn.disabled = false;
                loginBtn.innerText = "ACCESS SYSTEM";
                return;
            }
        } else {
            if (confirm("No vault found. Initialize new vault with this password?")) {
                const enc = await encrypt("CANARY_OK", password);
                await client.mutation("passwords:add", {
                    domain: "SYSTEM_CANARY",
                    salt: btoa(String.fromCharCode(...enc.salt)),
                    iv: btoa(String.fromCharCode(...enc.iv)),
                    u: "SYSTEM",
                    p: enc.data,
                    fields: "{}"
                });
            } else {
                loginBtn.disabled = false;
                loginBtn.innerText = "ACCESS SYSTEM";
                return;
            }
        }

        masterKey = password;
        loginContainer.classList.add('hidden');
        vaultContainer.classList.remove('hidden');
        loadVault();
    } catch (e) {
        console.error("Login error:", e);
        alert("CONNECTION ERROR: Check Convex status");
        loginBtn.disabled = false;
        loginBtn.innerText = "ACCESS SYSTEM";
    }
}

async function loadVault() {
    try {
        console.log("Loading vault...");
        const encryptedRecords = await client.query("passwords:list");
        console.log(`Found ${encryptedRecords.length} records total.`);
        vaultEntries = [];
        
        for (const record of encryptedRecords) {
            if (record.domain === "SYSTEM_CANARY") continue;

            const u = await decrypt({ salt: record.salt, iv: record.iv, data: record.u }, masterKey);
            const p = await decrypt({ salt: record.salt, iv: record.iv, data: record.p }, masterKey);
            
            if (u !== null && p !== null) {
                vaultEntries.push({
                    id: record._id,
                    domain: record.domain,
                    u,
                    p,
                    fields: JSON.parse(record.fields || "{}")
                });
            } else {
                console.warn("Could not decrypt record:", record.domain);
            }
        }
        console.log(`Successfully decrypted ${vaultEntries.length} entries.`);
        renderGroups();
        renderEntries();
    } catch (e) {
        console.error("Failed to load vault", e);
    }
}

function renderGroups() {
    const groups = new Set(["ALL ENTRIES"]);
    vaultEntries.forEach(e => groups.add(e.domain));
    
    groupListContainer.innerHTML = '';
    Array.from(groups).sort().forEach(group => {
        const div = document.createElement('div');
        div.className = `group-item ${currentGroup === group ? 'active' : ''}`;
        div.innerText = group;
        div.onclick = () => {
            currentGroup = group;
            currentGroupLabel.innerText = group;
            renderGroups();
            renderEntries();
        };
        groupListContainer.appendChild(div);
    });
}

function renderEntries() {
    const query = searchInput.value.toLowerCase();
    entriesList.innerHTML = '';
    
    const filtered = vaultEntries.filter(e => {
        const inGroup = currentGroup === "ALL ENTRIES" || e.domain === currentGroup;
        const matchesSearch = e.domain.toLowerCase().includes(query) || e.u.toLowerCase().includes(query);
        return inGroup && matchesSearch;
    });

    if (filtered.length === 0) {
        entriesList.innerHTML = '<div class="entry-item" style="text-align:center; color:var(--cp-subtext);">NO ENTRIES FOUND</div>';
    }

    filtered.forEach(entry => {
        const div = document.createElement('div');
        div.className = 'entry-item';
        div.innerHTML = `
            <div class="entry-header">
                <div class="entry-info">
                    <div class="entry-domain">${entry.domain}</div>
                    <div class="entry-user">USER: ${entry.u}</div>
                </div>
                <div class="entry-actions">
                    <button class="copy-user-btn" data-val="${entry.u}">USER</button>
                    <button class="copy-pass-btn" data-val="${entry.p}">PASS</button>
                    <button class="delete-btn" data-id="${entry.id}">DEL</button>
                </div>
            </div>
            <div class="details-toggle">▼ SHOW DETAILS ▼</div>
            <div class="entry-details hidden">
                <div class="detail-row">
                    <span class="detail-label">PASSWORD:</span>
                    <span>********</span>
                    <button class="copy-pass-btn" data-val="${entry.p}">COPY</button>
                </div>
                ${Object.entries(entry.fields).map(([k, v]) => `
                    <div class="detail-row">
                        <span class="detail-label">${k.toUpperCase()}:</span>
                        <span>${v}</span>
                        <button class="copy-field-btn" data-val="${v}">COPY</button>
                    </div>
                `).join('')}
            </div>
        `;

        const toggle = div.querySelector('.details-toggle');
        const details = div.querySelector('.entry-details');
        toggle.onclick = () => {
            const isHidden = details.classList.toggle('hidden');
            toggle.innerText = isHidden ? "▼ SHOW DETAILS ▼" : "▲ HIDE DETAILS ▲";
        };

        entriesList.appendChild(div);
    });

    // Event listeners
    document.querySelectorAll('.copy-user-btn').forEach(b => b.onclick = () => copyToClipboard(b.dataset.val));
    document.querySelectorAll('.copy-pass-btn').forEach(b => b.onclick = () => copyToClipboard(b.dataset.val));
    document.querySelectorAll('.copy-field-btn').forEach(b => b.onclick = () => copyToClipboard(b.dataset.val));
    document.querySelectorAll('.delete-btn').forEach(b => b.onclick = () => deleteEntry(b.dataset.id));
}

async function saveEntry() {
    const domain = document.getElementById('new-domain').value || "UNCATEGORIZED";
    const username = document.getElementById('new-username').value;
    const password = document.getElementById('new-password').value;

    if (!username || !password) {
        alert("Username and Password are required");
        return;
    }

    // Use SAME salt and IV for both fields in the record
    const baseEnc = await encrypt(username, masterKey);
    const encU = baseEnc.data;
    const encPObj = await encrypt(password, masterKey, baseEnc.salt, baseEnc.iv);
    const encP = encPObj.data;
    
    await client.mutation("passwords:add", {
        domain: domain.toUpperCase(),
        salt: btoa(String.fromCharCode(...baseEnc.salt)),
        iv: btoa(String.fromCharCode(...baseEnc.iv)),
        u: encU,
        p: encP,
        fields: "{}" 
    });

    document.getElementById('new-domain').value = '';
    document.getElementById('new-username').value = '';
    document.getElementById('new-password').value = '';
    loadVault();
}

async function deleteEntry(id) {
    if (confirm("Delete this entry?")) {
        await client.mutation("passwords:remove", { id });
        loadVault();
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Copied
    });
}

function generatePassword() {
    const chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+";
    let pass = "";
    for (let i = 0; i < 16; i++) {
        pass += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    document.getElementById('new-password').value = pass;
    document.getElementById('new-password').type = 'text';
}

// --- EVENTS ---
loginBtn.onclick = handleLogin;
logoutBtn.onclick = () => {
    masterKey = null;
    vaultEntries = [];
    loginContainer.classList.remove('hidden');
    vaultContainer.classList.add('hidden');
    masterPassInput.value = '';
};
saveBtn.onclick = saveEntry;
genBtn.onclick = generatePassword;
searchInput.oninput = renderEntries;
masterPassInput.onkeypress = (e) => { if (e.key === 'Enter') handleLogin(); };
