# Frameworks & Build Tools — Reference Guide

## The Two Layers

Every modern web project has two separate concerns:

| Layer | What it is | Examples |
|---|---|---|
| **UI Framework** | What you write — components, state, reactivity | React, Vue, Svelte |
| **Build Tool** | Compiles/bundles your code for dev & production | Vite, Next.js, Astro |

You pick one from each. They don't compete — they work together.

---

## Build Tools

### Vite
The current standard. Fast dev server + bundler. Works with any UI framework.
```bash
npm create vite@latest my-app
# prompts: pick framework (React, Vue, Svelte, etc.)
cd my-app
npm install
npm run dev
```

### Next.js (React only)
Full-stack React framework. Has its own build system — you don't add Vite separately. Good for SSR, file-based routing, and API routes built in.
```bash
npx create-next-app@latest my-app
cd my-app
npm run dev
```

### Nuxt (Vue only)
Same idea as Next.js but for Vue. SSR, file-based routing, built-in.
```bash
npx nuxi@latest init my-app
cd my-app
npm run dev
```

### Astro
For content-heavy sites (blogs, docs, marketing). Ships zero JS by default. Can use React/Vue/Svelte components inside it.
```bash
npm create astro@latest my-app
cd my-app
npm run dev
```

### SvelteKit (Svelte only)
Full-stack Svelte framework with SSR and file-based routing. Like Next.js but for Svelte.
```bash
npm create svelte@latest my-app
cd my-app
npm install
npm run dev
```

---

## UI Frameworks

### React
Most popular. JSX syntax. Large ecosystem.
- Maintained by Meta
- Use with: Vite, Next.js, Astro
```bash
npm create vite@latest my-app -- --template react
```

### Vue
Easier learning curve than React. Template syntax (closer to HTML).
- Maintained by the community (Evan You — same guy behind Vite)
- Use with: Vite, Nuxt, Astro
```bash
npm create vite@latest my-app -- --template vue
```

### Svelte
Compiles away at build time — no framework runtime in the browser. Cleanest syntax.
- Use with: Vite, SvelteKit, Astro
```bash
npm create vite@latest my-app -- --template svelte
```

### Solid
Like React but faster. No virtual DOM. Small but growing.
```bash
npm create vite@latest my-app -- --template solid
```

### No framework (vanilla JS)
Just plain JS with Vite for bundling.
```bash
npm create vite@latest my-app -- --template vanilla
```

---

## How They Combine

```
Vite + React       → SPA, most common choice
Vite + Vue         → SPA alternative to React
Vite + Svelte      → SPA, small bundle size
Next.js            → React + SSR + API routes (Vite built-in)
Nuxt               → Vue + SSR + API routes (Vite built-in)
SvelteKit          → Svelte + SSR + API routes (Vite built-in)
Astro + React/Vue  → Static sites with interactive islands
```

---

## With Cloudflare Workers

Any of these can deploy to Cloudflare. Add `@cloudflare/vite-plugin` for Workers integration.

| Stack | Best for |
|---|---|
| Vite + React + Workers | SPA frontend + Worker API + D1 |
| Next.js + Workers | SSR React on the edge (via `@opennextjs/cloudflare`) |
| Astro + Workers | Content sites with edge API routes |
| SvelteKit + Workers | SSR Svelte on the edge (native support) |

**Quickest start with Cloudflare:**
```bash
npm create cloudflare@latest my-app -- --framework=react    # React
npm create cloudflare@latest my-app -- --framework=vue      # Vue
npm create cloudflare@latest my-app -- --framework=svelte   # SvelteKit
npm create cloudflare@latest my-app -- --framework=astro    # Astro
npm create cloudflare@latest my-app -- --framework=next     # Next.js
```
Each one scaffolds the correct Vite config, wrangler.toml, and Cloudflare plugin automatically.

---

## Quick Decision Guide

**Just want to build something and you know React a bit?**
→ `Vite + React`

**Want the most beginner-friendly syntax?**
→ `Vite + Vue`

**Want smallest bundle, cleanest code?**
→ `Vite + Svelte`

**Need SEO / server-side rendering?**
→ `Next.js` (React) or `SvelteKit` (Svelte) or `Nuxt` (Vue)

**Building a blog or docs site?**
→ `Astro`

**Deploying to Cloudflare Workers with D1?**
→ Any of the above via `npm create cloudflare@latest`

---

## What TypeScript adds

All frameworks above support TypeScript. Just add `--template react-ts` (or `-ts` suffix) in Vite:
```bash
npm create vite@latest my-app -- --template react-ts
npm create vite@latest my-app -- --template vue-ts
npm create vite@latest my-app -- --template svelte-ts
```
Next.js, Nuxt, SvelteKit, Astro all include TypeScript by default.

---

## Useful Links
- Vite docs: https://vite.dev
- React docs: https://react.dev
- Vue docs: https://vuejs.org
- Svelte docs: https://svelte.dev
- Next.js docs: https://nextjs.org
- Nuxt docs: https://nuxt.com
- SvelteKit docs: https://kit.svelte.dev
- Astro docs: https://astro.build
- Cloudflare templates: https://developers.cloudflare.com/workers/frameworks/
