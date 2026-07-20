# Deploying Projects with Flask, Convex, and Vercel

This guide explains how this project is structured, how to deploy it, and how to adapt your projects to run on Vercel with Convex database integration.

---

## 1. Project Architecture Overview

This project consists of:
1. **Frontend**: Static files (`index.html`, `static/css/style.css`, `static/js/main.js`).
2. **Backend**: A Flask application (`app.py`).
3. **Database**: A serverless cloud database on **Convex** (migrated from local SQLite `wwe.db`).
4. **Scraper**: A script (`scraper.py`) that fetches WWE PPV events and saves them directly to Convex.

---

## 2. Using Convex with Vercel

Because Vercel serverless functions are read-only and stateless, a local database like SQLite won't save data persistently. **Convex** solves this by providing a cloud-hosted serverless database.

### Configuring Environment Variables (`CONVEX_URL`)
To allow the Python backend to talk to Convex:
1. Locally, the Convex URL is saved inside `.env.local` (automatically created by `npx convex dev`).
2. On Vercel, secret files like `.env.local` are ignored for security. You must manually add it:
   * Go to the **Vercel Dashboard** and click on your project.
   * Go to the **Settings** tab -> **Environment Variables** (left menu).
   * Click **Add Environment Variable** in the top right.
   * Enter **Key**: `CONVEX_URL`
   * Enter **Value**: (your Convex HTTP address, e.g. `https://your-deployment.convex.cloud`)
   * Click **Save**.

---

## 3. How to Update Your Project on Vercel
Once a project is created on Vercel, the drag-and-drop folder upload box disappears from the web interface. To push new updates:

### Method A: Vercel CLI (Fastest)
Run this command from your project folder:
```bash
vercel --prod
```

### Method B: GitHub Integration (Automatic)
Link your Vercel project to a GitHub repository. Every time you commit and push changes, Vercel will automatically redeploy the site.

---

## 4. Resetting and Testing Data

If you want to clear your data to test the scraper from scratch:

### A. Clear the Convex Database
1. Open the Convex dashboard using the command:
   ```bash
   npx convex dashboard
   ```
2. Navigate to the **Data** tab on the left.
3. Select the `events` table, and delete all records.

### B. Clear Your Browser's `localStorage` (Checkboxes Cache)
Your browser caches seen/hidden checkbox clicks. To reset them:
1. Open the website, press **F12** to open Developer Tools, and select the **Console** tab.
2. Run the command:
   ```javascript
   localStorage.clear()
   ```
3. Refresh the page.

---

## 5. Resolving Vercel Deploy Dependency Errors
If Vercel fails to resolve dependencies during build time:
* **The Error**: Python library version conflicts (e.g. `no version of convex==1.18.0`).
* **The Fix**: The Python `convex` library has different version numbers than the JS/TS npm packages. Ensure your `requirements.txt` includes only:
  ```text
  Flask==3.0.2
  beautifulsoup4==4.12.3
  convex
  python-dotenv==1.0.1
  ```

---

## 6. Understanding Vercel Links
Vercel generates multiple URLs for your project:
* **Production URL (`wweppv.vercel.app`)**: The main address showing the latest live production code.
* **Deployment/Preview URL (`wwe-nigd3un3j...vercel.app`)**: A unique, permanent URL created for every single upload. Useful for testing drafts before releasing them to the main website.
