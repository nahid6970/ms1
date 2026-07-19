# Deploying Projects with Flask / Databases on Vercel

This guide explains how this project is structured, how to deploy it, and how to adapt projects (both Flask-based and Static) to work on Vercel.

---

## 1. Project Architecture Overview

This project consists of:
1. **Frontend**: Static files (`index.html`, `static/css/style.css`, `static/js/main.js`).
2. **Backend**: A Flask application (`app.py`) running a server locally.
3. **Database**: A local SQLite file (`wwe.db`).
4. **Scraper**: A script (`scraper.py`) that fetches WWE PPV event information and saves it to the SQLite database.

---

## 2. The Core Problem with Vercel & SQLite

When you upload a folder to Vercel, it defaults to hosting it as a **static website** (unless configured otherwise).
* **Static Hosting**: Only serves HTML, CSS, and JS. The Flask server (`app.py`) and SQLite database (`wwe.db`) do not run.
* **Serverless Functions**: Vercel allows running backend Python code, but it is **read-only and ephemeral**.
  * Any write operation to a local file (such as updating `wwe.db` or exporting `index.html`) will fail or be lost immediately on the next request.

---

## 3. How We Fixed This Project (Static Deployment with LocalStorage)

Since Vercel is serving your frontend as a static site, we updated the frontend JavaScript code (`static/js/main.js`) to:
1. Check if the page is running in **static mode** (when `window.STATIC_EVENTS` is present).
2. Save changes (like checking "Seen" or "Hidden") to the browser's **`localStorage`** instead of trying to send a POST request to the Flask server.
3. On page load, it merges the default events with the saved states from `localStorage`.

---

## 4. How to Deploy Flask/Backends on Vercel

If you want to run a Flask backend on Vercel instead of a static site, you must follow these steps:

### Step A: Structure the Flask App for Vercel
Vercel expects serverless backend entry points under the `/api` directory.
1. Move/rename your main Flask entry point (or create a file) at `api/index.py`:
   ```python
   # api/index.py
   from flask import Flask
   app = Flask(__name__)

   @app.route('/api/hello')
   def hello():
       return {"message": "Hello from Flask on Vercel!"}
   ```

### Step B: Create a `vercel.json` Configuration
Create a file named `vercel.json` in the root of your project:
```json
{
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/api/index.py"
    }
  ]
}
```

### Step C: Handle the Database (Crucial!)
Because Vercel serverless functions are stateless and read-only, **you cannot use SQLite**. Instead, you must:
1. Use a cloud-hosted database (e.g., PostgreSQL on **Supabase**, **Vercel Postgres**, or MongoDB on **Atlas**).
2. Connect to it via a connection string (e.g., `postgresql://...`) saved in Vercel's **Environment Variables** (`dotenv` locally, and the Vercel dashboard for production).

---

## 5. Summary: Which Setup to Choose?

| Goal | Hosting Approach | State/Database Strategy |
| :--- | :--- | :--- |
| **Simple Static Page** | Drag & Drop directory to Vercel | Use `localStorage` on the frontend. |
| **Dynamic Backend** | Configure `vercel.json` + Python Serverless | Use a cloud database (Postgres/Supabase). |
