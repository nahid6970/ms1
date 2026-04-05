# Backend Alternatives to Convex

If Convex goes down or becomes paid, here are free alternatives. All require only changing `sendDataToConvex` and `loadDataFromConvex` in each `background.js` — everything else stays the same.

---

## 1. Supabase (Easiest Swap)

**Free tier:** 500MB DB, unlimited API calls, project pauses after 1 week inactivity on free plan.  
**Docs:** https://supabase.com/docs

### Setup
1. Create project at https://supabase.com
2. Create a table `backups` with columns: `extension_name` (text, primary key), `data` (jsonb)
3. Get your project URL and anon key from Settings → API

### background.js replacement

```javascript
const SUPABASE_URL = "https://your-project.supabase.co";
const SUPABASE_KEY = "your-anon-key";
const EXTENSION_NAME = 'your_extension_name';

async function sendDataToConvex(data) {
  try {
    const res = await fetch(`${SUPABASE_URL}/rest/v1/backups`, {
      method: 'POST',
      headers: {
        'apikey': SUPABASE_KEY,
        'Authorization': `Bearer ${SUPABASE_KEY}`,
        'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates'
      },
      body: JSON.stringify({ extension_name: EXTENSION_NAME, data })
    });
    return { success: res.ok };
  } catch (e) {
    return { success: false, error: e.message };
  }
}

async function loadDataFromConvex() {
  try {
    const res = await fetch(`${SUPABASE_URL}/rest/v1/backups?extension_name=eq.${EXTENSION_NAME}&select=data`, {
      headers: { 'apikey': SUPABASE_KEY, 'Authorization': `Bearer ${SUPABASE_KEY}` }
    });
    const rows = await res.json();
    return { success: true, data: rows[0]?.data || null };
  } catch (e) {
    return { success: false, error: e.message };
  }
}
```

---

## 2. Firebase Firestore

**Free tier:** 1GB storage, 50k reads/day, 20k writes/day. Google-backed, very stable.  
**Docs:** https://firebase.google.com/docs/firestore

### Setup
1. Create project at https://console.firebase.google.com
2. Enable Firestore in test mode
3. Get your Web API key and project ID from Project Settings

### background.js replacement

```javascript
const FIREBASE_PROJECT = "your-project-id";
const FIREBASE_KEY = "your-web-api-key";
const EXTENSION_NAME = 'your_extension_name';
const BASE = `https://firestore.googleapis.com/v1/projects/${FIREBASE_PROJECT}/databases/(default)/documents/backups`;

async function sendDataToConvex(data) {
  try {
    const res = await fetch(`${BASE}/${EXTENSION_NAME}?key=${FIREBASE_KEY}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fields: { data: { stringValue: JSON.stringify(data) } } })
    });
    return { success: res.ok };
  } catch (e) {
    return { success: false, error: e.message };
  }
}

async function loadDataFromConvex() {
  try {
    const res = await fetch(`${BASE}/${EXTENSION_NAME}?key=${FIREBASE_KEY}`);
    if (!res.ok) return { success: true, data: null };
    const doc = await res.json();
    return { success: true, data: JSON.parse(doc.fields.data.stringValue) };
  } catch (e) {
    return { success: false, error: e.message };
  }
}
```

---

## 3. GitHub Gist (No Server, Zero Cost)

**Free tier:** Unlimited, forever. Requires a GitHub account.  
**Docs:** https://docs.github.com/en/rest/gists

### Setup
1. Go to https://github.com/settings/tokens and create a token with `gist` scope
2. Create a gist manually at https://gist.github.com — note the gist ID from the URL

### background.js replacement

```javascript
const GITHUB_TOKEN = "your-github-token";
const GIST_ID = "your-gist-id";
const EXTENSION_NAME = 'your_extension_name';

async function sendDataToConvex(data) {
  try {
    const res = await fetch(`https://api.github.com/gists/${GIST_ID}`, {
      method: 'PATCH',
      headers: { 'Authorization': `token ${GITHUB_TOKEN}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ files: { [`${EXTENSION_NAME}.json`]: { content: JSON.stringify(data) } } })
    });
    return { success: res.ok };
  } catch (e) {
    return { success: false, error: e.message };
  }
}

async function loadDataFromConvex() {
  try {
    const res = await fetch(`https://api.github.com/gists/${GIST_ID}`, {
      headers: { 'Authorization': `token ${GITHUB_TOKEN}` }
    });
    const gist = await res.json();
    const content = gist.files[`${EXTENSION_NAME}.json`]?.content;
    return { success: true, data: content ? JSON.parse(content) : null };
  } catch (e) {
    return { success: false, error: e.message };
  }
}
```

---

## 4. PocketBase (Self-Hosted)

**Free tier:** Free forever — you host it yourself on any VPS (~$4/mo on DigitalOcean/Hetzner).  
**Docs:** https://pocketbase.io/docs

### Setup
1. Download binary from https://pocketbase.io
2. Run `./pocketbase serve` — admin UI at `http://localhost:8090/_/`
3. Create a collection `backups` with fields: `extension_name` (text), `data` (json)

### background.js replacement

```javascript
const PB_URL = "https://your-pocketbase-instance.com";
const EXTENSION_NAME = 'your_extension_name';

async function sendDataToConvex(data) {
  try {
    // Try update first, then create
    const existing = await fetch(`${PB_URL}/api/collections/backups/records?filter=extension_name="${EXTENSION_NAME}"`);
    const list = await existing.json();
    const record = list.items?.[0];

    const method = record ? 'PATCH' : 'POST';
    const url = record ? `${PB_URL}/api/collections/backups/records/${record.id}` : `${PB_URL}/api/collections/backups/records`;

    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ extension_name: EXTENSION_NAME, data })
    });
    return { success: res.ok };
  } catch (e) {
    return { success: false, error: e.message };
  }
}

async function loadDataFromConvex() {
  try {
    const res = await fetch(`${PB_URL}/api/collections/backups/records?filter=extension_name="${EXTENSION_NAME}"`);
    const list = await res.json();
    return { success: true, data: list.items?.[0]?.data || null };
  } catch (e) {
    return { success: false, error: e.message };
  }
}
```

---

## Quick Comparison

| Option | Cost | Hosting | Best For |
|---|---|---|---|
| Supabase | Free tier | Managed | Easiest Convex swap |
| Firebase | Free tier | Managed | Google ecosystem, very reliable |
| GitHub Gist | Free forever | GitHub | Simplest, no setup |
| PocketBase | Free (self-host) | Your VPS | Full control, no limits |

> **Reminder:** Also update `host_permissions` in `manifest.json` to allow the new backend domain.
