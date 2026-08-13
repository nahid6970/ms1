# YT Notifier — Cloudflare Pages + Convex

YouTube channel RSS notifier, rebuilt from the original Flask + SQLite app on a
modern serverless stack:

- **[Convex](https://convex.dev)** — database, backend functions (queries,
  mutations, actions), and scheduled jobs
- **[Cloudflare Pages](https://pages.cloudflare.com)** — serves the static
  frontend (no build step, no framework)

The frontend talks to Convex directly through its [HTTP API](https://docs.convex.dev/http-api)
(`/api/query`, `/api/mutation`, `/api/action`), so no SDK or bundler is needed.

The old Flask app is preserved in [`legacy_flask/`](legacy_flask/).

## Project layout

```
convex/            # Convex backend (schema + functions)
  schema.ts        # channels / videos / settings tables
  youtube.ts       # channel URL resolution + RSS parsing helpers
  channels.ts      # add / remove / list channels
  videos.ts        # list videos, unread count, toggle read, feed ingest
  refresh.ts       # refresh actions (single channel, all, cron)
  stats.ts         # upload heatmap query
  settings.ts      # show_seen preference
  crons.ts         # auto-refresh schedule (every 6h)
public/            # Static frontend (Cloudflare Pages)
  index.html       # Feed
  channels.html    # Manage channels
  stats.html       # Upload heatmap
  settings.html    # Settings
  js/config.js     # Convex deployment URL
  js/app.js        # Shared logic (calls Convex HTTP API)
wrangler.toml      # Cloudflare Pages config
```

## Setup

Requirements: Node.js 18+, a [Convex](https://convex.dev) account (free tier),
and a [Cloudflare](https://dash.cloudflare.com) account.

```bash
npm install
```

### 1. Start Convex

```bash
npx convex dev
```

This logs you in (or opens a signup flow), creates a project, and starts the
local dev server. It also generates the `convex/_generated/` files and writes
your deployment URL into `.env.local`.

### 2. (Optional) Add a YouTube Data API key for reliable fetching

By default the app fetches videos from YouTube's RSS feed
(`feeds/videos.xml`), which works but has been **intermittently unavailable**
since late 2025. For a more reliable fetcher, set a free **YouTube Data API v3**
key and the app will use the official API instead:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and
   create a project (or reuse one).
2. **APIs & Services → Library** → search for *YouTube Data API v3* → **Enable**.
3. **APIs & Services → Credentials** → **Create Credentials → API key**.
   (You can restrict the key to the YouTube Data API only.)
4. Give Convex the key:

   ```bash
   npx convex env set YT_DATA_API_KEY your-api-key
   ```

   For production deployments use:

   ```bash
   npx convex env set --prod YT_DATA_API_KEY your-api-key
   ```

Without a key the app simply falls back to the RSS feed, so it works either way.

### 3. Point the frontend at your deployment

Open `public/js/config.js` and paste your deployment URL:

```js
window.CONVEX_URL = "https://your-project-123.convex.cloud";
```

The URL is on the Convex dashboard (Deployments → Settings → URL) or in the
`CONVEX_URL` line of `.env.local`.

### 4. Serve the frontend locally

```bash
npm run dev:pages        # or: npx wrangler pages dev public
```

Open the printed URL (default http://localhost:8788). Add a channel or two and
hit **Check Updates** to pull in their latest videos.

## Deploying

Deploy the backend:

```bash
npx convex deploy
```

Deploy the frontend to Cloudflare Pages (login with `npx wrangler login` on
first use; `--project-name` can be changed in `package.json`):

```bash
npm run deploy:pages
```

After deploying, your Pages site must know the Convex URL — it is read from
`public/js/config.js`, so make sure that file is committed with your real URL
before deploying.

## How it works

- **Adding a channel** calls the `channels:add` action, which resolves the
  channel ID + thumbnail (via the YouTube Data API when a key is set, otherwise
  by scraping the channel page), inserts it, and immediately pulls its latest
  videos.
- **Check Updates** calls `refresh:refreshAll`, which re-fetches each channel's
  recent videos (YouTube Data API `playlistItems.list` when a key is set,
  otherwise the RSS feed) and inserts only videos not seen before (marked
  unread).
- **Auto-refresh** — `convex/crons.ts` schedules the same refresh every 6 hours
  in production. Edit the interval there if you want a different cadence.
- **Read/unread** is a simple `isNew` flag toggled from the feed page.

## Troubleshooting

- **"Convex URL is not configured yet"** — set `window.CONVEX_URL` in
  `public/js/config.js`.
- **Could not resolve channel** — YouTube sometimes changes its page markup.
  The resolver in `convex/youtube.ts` tries three patterns
  (`"channelId":"..."`, `meta[itemprop=channelId]`, `channel_id=`); add the
  URL directly from a channel's About page.
- **Crons not running** — crons run in the deployed production deployment.
  Use `npx convex deploy` and check the dashboard's Cron section.
- **Feeds return no videos** — YouTube's RSS endpoint has occasional outages.
  If a refresh finds 0 videos, wait a bit and hit **Check Updates** again, or
  set a `YT_DATA_API_KEY` to use the official API instead.
