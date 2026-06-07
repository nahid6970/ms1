# Vite + Cloudflare Workers — Reference Guide

> Upgrade from the basic Workers setup. Vite handles your frontend, Workers handle your backend/API, D1 is your database — all in one project with proper local dev.

---

## Why Vite instead of plain Workers?

| Plain Workers | Vite + Cloudflare Plugin |
|---|---|
| No frontend build system | Full Vite dev server (HMR, bundling) |
| Serve HTML manually | React/Vue/Svelte just works |
| Local dev ≠ production runtime | Local dev runs inside actual Workers runtime |
| `wrangler dev` only | `vite dev` with all Cloudflare bindings available |

With `@cloudflare/vite-plugin`, your Worker code runs inside **workerd** locally — same runtime as production. D1, KV, R2 all work locally without mocking.

---

## Project Setup (React + Workers + D1)

### 1. Create project
```bash
npm create cloudflare@latest my-app -- --framework=react
cd my-app
```
This scaffolds a Vite + React project with the Cloudflare plugin pre-configured.

**Or manually with any Vite framework:**
```bash
npm create vite@latest my-app -- --template react
cd my-app
npm install @cloudflare/vite-plugin
```

---

### 2. File structure
```
my-app/
├── vite.config.ts          ← Cloudflare plugin goes here
├── wrangler.toml           ← same as before
├── worker/
│   └── index.ts            ← your Worker (API/backend)
├── src/
│   ├── main.tsx            ← React frontend entry
│   └── App.tsx
└── public/
```

---

### 3. vite.config.ts
```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { cloudflare } from "@cloudflare/vite-plugin";

export default defineConfig({
  plugins: [
    react(),
    cloudflare(),
  ],
});
```

---

### 4. wrangler.toml
```toml
name = "my-app"
compatibility_date = "2024-01-01"
main = "worker/index.ts"

[[d1_databases]]
binding = "DB"
database_name = "my-db"
database_id = "your-id-here"
```

---

### 5. Worker (worker/index.ts)
```ts
interface Env {
  DB: D1Database;
}

export default {
  async fetch(request: Request, env: Env) {
    const url = new URL(request.url);

    // API routes — frontend fetches these
    if (url.pathname === "/api/notes") {
      if (request.method === "GET") {
        const { results } = await env.DB.prepare(
          "SELECT * FROM notes ORDER BY id DESC"
        ).all();
        return Response.json(results);
      }

      if (request.method === "POST") {
        const { text } = await request.json<{ text: string }>();
        await env.DB.prepare("INSERT INTO notes (text) VALUES (?)").bind(text).run();
        return Response.json({ ok: true });
      }
    }

    return new Response("Not found", { status: 404 });
  },
};
```

---

### 6. Frontend fetching the Worker API (src/App.tsx)
```tsx
import { useEffect, useState } from "react";

export default function App() {
  const [notes, setNotes] = useState<{ id: number; text: string }[]>([]);

  useEffect(() => {
    fetch("/api/notes").then(r => r.json()).then(setNotes);
  }, []);

  async function addNote() {
    await fetch("/api/notes", {
      method: "POST",
      body: JSON.stringify({ text: "new note" }),
      headers: { "Content-Type": "application/json" },
    });
    fetch("/api/notes").then(r => r.json()).then(setNotes);
  }

  return (
    <div>
      <button onClick={addNote}>Add Note</button>
      <ul>{notes.map(n => <li key={n.id}>{n.text}</li>)}</ul>
    </div>
  );
}
```

> `/api/notes` works both locally and in production — Vite proxies it to your Worker automatically.

---

## Commands

| Command | What it does |
|---|---|
| `npm run dev` | Start Vite dev server — Worker runs in real workerd locally |
| `npm run build` | Build frontend + Worker for production |
| `npm run deploy` | Build and deploy everything to Cloudflare |
| `npx wrangler login` | Authenticate (do this once) |

---

## D1 Setup (same as before, just add to wrangler.toml)

```bash
# Create DB
npx wrangler d1 create my-db

# Create tables locally
npx wrangler d1 execute my-db --local --command "CREATE TABLE notes (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT NOT NULL)"

# Create tables in production
npx wrangler d1 execute my-db --remote --command "CREATE TABLE notes (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT NOT NULL)"
```

---

## How it works locally

```
Browser → Vite dev server (port 5173)
              ├── /src/**  → served by Vite (React HMR)
              └── /api/**  → proxied to Worker inside workerd
```

Your Worker runs in the real Workers runtime locally. D1 reads/writes actually work. No mocks.

---

## Key differences from your old setup

| Old (plain Workers) | New (Vite + Plugin) |
|---|---|
| `wrangler dev` only | `npm run dev` (Vite + Worker together) |
| Serve HTML from Worker manually | React/Vue frontend built by Vite |
| Import HTML as string | Proper component-based UI |
| No hot reload | Full HMR on frontend changes |
| Local D1 via wrangler | Local D1 via workerd (same thing, better integrated) |

---

## TypeScript types for Cloudflare bindings

Run this once to get proper types:
```bash
npx wrangler types
```
Generates `worker-configuration.d.ts` so `env.DB`, `env.MY_KV` etc. are fully typed.

---

## Useful Links
- Cloudflare Vite plugin: https://developers.cloudflare.com/workers/vite-plugin/
- Plugin GitHub: https://github.com/cloudflare/workers-sdk/tree/main/packages/vite-plugin
- Full-stack template: https://github.com/cloudflare/templates
- Workers docs: https://developers.cloudflare.com/workers/
