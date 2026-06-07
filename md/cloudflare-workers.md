# Cloudflare Workers — Reference Guide

## What is it?
Cloudflare Workers is a serverless platform that runs your JavaScript at Cloudflare's edge (300+ locations worldwide). Unlike GitHub Pages (static only), Workers can handle dynamic requests, databases, APIs, and more.

---

## Project Setup

### File structure
```
├── package.json
├── wrangler.toml
└── src/
    ├── index.js    ← worker logic
    └── page.html   ← HTML page (optional)
```

### package.json
```json
{
  "name": "my-worker",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "wrangler dev",
    "deploy": "wrangler deploy"
  },
  "devDependencies": {
    "wrangler": "^3.0.0"
  }
}
```

### wrangler.toml (basic)
```toml
name = "my-worker"
main = "src/index.js"
compatibility_date = "2024-01-01"
```

### Basic worker (src/index.js)
```js
export default {
  async fetch(request, env) {
    return new Response("Hello World", {
      headers: { "Content-Type": "text/plain" },
    });
  },
};
```

### Serve an HTML file
```js
import html from './page.html';

export default {
  async fetch(request, env) {
    return new Response(html, {
      headers: { "Content-Type": "text/html" },
    });
  },
};
```

---

## Commands

| Command | What it does |
|---|---|
| `npm install` | Install dependencies |
| `npx wrangler login` | Authenticate with Cloudflare |
| `npm run dev` | Run locally at http://127.0.0.1:8787 |
| `npm run deploy` | Deploy to Cloudflare (live URL) |

> **Updating:** just run `npm run deploy` again after any changes.

---

## Routing Example
```js
export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/api/data") {
      return Response.json({ hello: "world" });
    }

    if (request.method === "POST" && url.pathname === "/submit") {
      const body = await request.json();
      // do something with body
      return Response.json({ ok: true });
    }

    return new Response("Not found", { status: 404 });
  },
};
```

---

## D1 Database (SQLite)

### Free tier limits
- 5 GB storage
- 5 million row reads/day
- 100,000 row writes/day

### Setup steps

**1. Create the database:**
```
npx wrangler d1 create my-db
```
Copy the `database_id` from the output.

**2. Add to wrangler.toml:**
```toml
[[d1_databases]]
binding = "DB"
database_name = "my-db"
database_id = "your-id-here"
```

**3. Create table locally:**
```
npx wrangler d1 execute my-db --local --command "CREATE TABLE notes (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT NOT NULL)"
```

**4. Create table on production (remote):**
```
npx wrangler d1 execute my-db --remote --command "CREATE TABLE notes (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT NOT NULL)"
```

### Using D1 in worker
```js
export default {
  async fetch(request, env) {
    // Read
    const { results } = await env.DB.prepare("SELECT * FROM notes ORDER BY id DESC").all();

    // Write
    await env.DB.prepare("INSERT INTO notes (text) VALUES (?)").bind("hello").run();

    return Response.json(results);
  },
};
```

---

## KV (Key-Value Storage)

### Free tier limits
- 1 GB storage
- 100,000 reads/day
- 1,000 writes/day

### Setup

**1. Create KV namespace:**
```
npx wrangler kv namespace create MY_KV
```

**2. Add to wrangler.toml:**
```toml
[[kv_namespaces]]
binding = "MY_KV"
id = "your-kv-id-here"
```

### Using KV in worker
```js
// Write
await env.MY_KV.put("key", JSON.stringify({ name: "Nahid" }));

// Read
const value = await env.MY_KV.get("key", { type: "json" });

// Delete
await env.MY_KV.delete("key");
```

---

## When to use what

| Use case | Best choice |
|---|---|
| Fixed/static data | JSON file (import it) |
| Simple dynamic data, sessions | KV |
| Structured data, real app (users, posts) | D1 |

---

## Workers vs Convex (GitHub Pages)

| | Cloudflare Workers + D1 | GitHub Pages + Convex |
|---|---|---|
| Backend | ✅ Built-in (your Worker) | ✅ Convex functions |
| Database | ✅ D1 (SQL) | ✅ Convex (NoSQL) |
| Real-time | ❌ Manual | ✅ Built-in live queries |
| Speed | ✅ Edge (fastest) | ⚠️ Single region |
| Cold start | ✅ ~0ms | ⚠️ Some latency |
| Vendor lock-in | Low (standard JS/SQL) | High (Convex API) |
| Complexity | You write everything | Less boilerplate |

- **Cloudflare Workers** = faster globally, full control, standard SQL
- **Convex** = easier real-time features, less boilerplate

---

## Free Tier Summary (Workers)

| Resource | Free limit |
|---|---|
| Requests | 100,000/day |
| CPU time | 10ms per request* |
| D1 storage | 5 GB |
| D1 reads | 5M rows/day |
| D1 writes | 100K rows/day |
| KV storage | 1 GB |
| KV reads | 100K/day |
| KV writes | 1K/day |

*CPU time = only active JS execution, waiting for DB/API doesn't count.

---

## Useful Links
- Docs: https://developers.cloudflare.com/workers/
- Limits: https://developers.cloudflare.com/workers/platform/limits/
- D1 docs: https://developers.cloudflare.com/d1/
- KV docs: https://developers.cloudflare.com/kv/
- Dashboard: https://dash.cloudflare.com/
