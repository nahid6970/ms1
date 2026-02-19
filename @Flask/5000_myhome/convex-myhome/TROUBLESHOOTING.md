# Troubleshooting Guide

## Issue: "addLink error" when adding items

### Possible Causes:
1. Convex dev server not running
2. Convex deployment not initialized
3. Network connection issues
4. Schema not pushed to Convex

### Solutions:

#### Step 1: Check if Convex dev server is running
```bash
cd convex-myhome
npx convex dev
```

This should show:
```
✓ Convex functions ready!
✓ Watching for file changes...
```

#### Step 2: Verify Convex deployment
Open `test-connection.html` in your browser and click "Test Connection"
- If successful: Connection is working
- If failed: Check the error message

#### Step 3: Check browser console
1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for errors related to:
   - `ConvexHttpClient`
   - `api.functions`
   - Network errors

#### Step 4: Verify schema is pushed
```bash
npx convex dev
```
Should show schema being pushed. If not:
```bash
npx convex deploy
```

## Issue: No "Add Link" button visible

### Solution:
1. Click the "✏️ Edit" button in the top-right corner
2. OR press F1 key to toggle edit mode
3. The button should now appear at the bottom of the links container

## Issue: Sidebar buttons not showing

### Solution:
1. Enable edit mode (F1 or Edit button)
2. Look for the "+" button in the top bar
3. Click to add a sidebar button

## Common Errors:

### Error: "Cannot read property 'functions' of undefined"
**Cause:** API not loaded properly
**Solution:** 
1. Check if `convex/_generated/api.js` exists
2. Run `npx convex dev` to regenerate

### Error: "Failed to fetch"
**Cause:** Convex server not reachable
**Solution:**
1. Check internet connection
2. Verify CONVEX_URL in `.env.local`
3. Restart `npx convex dev`

### Error: "Mutation failed"
**Cause:** Schema mismatch or validation error
**Solution:**
1. Check browser console for detailed error
2. Verify all required fields are filled
3. Check schema.ts matches functions.ts

## Testing Steps:

1. **Test Connection:**
   - Open `test-connection.html`
   - Click "Test Connection"
   - Should see "Connection successful!"

2. **Test Add Link:**
   - Click "Test Add Link"
   - Should see "Link added successfully!"

3. **Test Get Links:**
   - Click "Test Get Links"
   - Should see list of all links

4. **Test Main App:**
   - Open `index.html`
   - Press F1 or click "Edit" button
   - Click "+ Add Link" at bottom
   - Fill in Name, Group, and URL
   - Click "Add"
   - Should see success notification

## Still Having Issues?

1. Check Convex dashboard: https://dashboard.convex.dev
2. Verify deployment is active
3. Check function logs in dashboard
4. Clear browser cache and reload
5. Try in incognito/private mode
