# Share Text - Convex Version

Simple text sharing app using Convex backend and vanilla HTML/JS.

## Setup Instructions (Run Manually)

1. Install dependencies:
```bash
npm install
```

2. Initialize Convex:
```bash
npx convex dev
```
- This will create a Convex account if needed
- Copy the deployment URL provided

3. Update `index.html`:
- Replace `YOUR_CONVEX_URL_HERE` with your actual Convex URL

4. Open `index.html` in browser to test

## Features

- Add text entries with timestamps
- Copy text to clipboard
- Delete individual entries
- Clean all entries
- Auto-refresh every 5 seconds

## Deployment

For production:
```bash
npx convex deploy
```
- Use the production URL in `index.html`
- Deploy `index.html` to any static host (GitHub Pages, etc.)
