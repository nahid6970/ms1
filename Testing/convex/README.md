# Convex HTML Counter Example

A simple counter app using Convex backend and vanilla HTML/JavaScript frontend.

## Setup Steps

### 1. Install Dependencies
```bash
npm install
```

### 2. Set Up Convex
```bash
npx convex dev
```
This will:
- Prompt you to create a Convex account (free)
- Create a new project
- Give you a deployment URL (looks like: `https://your-project.convex.cloud`)

### 3. Update HTML
Open `index.html` and replace `YOUR_CONVEX_URL_HERE` with your deployment URL from step 2.

### 4. Test Locally
Open `index.html` in your browser. The counter should work!

### 5. Deploy to GitHub Pages
1. Create a new GitHub repository
2. Push this code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```
3. Go to repository Settings → Pages
4. Set Source to "main" branch, root folder
5. Your site will be live at `https://YOUR_USERNAME.github.io/REPO_NAME/`

## How It Works
- **Convex backend**: Runs on Convex's servers (free tier available)
- **HTML frontend**: Hosted on GitHub Pages
- They communicate via HTTPS API calls

## Important Notes
- Keep `npx convex dev` running during development
- For production, run `npx convex deploy` to get a permanent deployment URL
- The HTML file uses CDN imports, so no build step needed
