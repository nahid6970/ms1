# 🎯 How to Add Links - Quick Guide

## You Should Now See TWO Buttons:

### 1. Main Button (in content area)
- Large green button
- Says: **"+ Add New Link"**
- Located at the bottom of the links container

### 2. Floating Button (bottom-right corner)
- Green circle with **"+"** symbol
- Always visible, even when scrolling
- Positioned at bottom-right of screen

## Both buttons do the same thing - open the Add Link form!

---

## Step-by-Step: Adding Your First Link

### 1. Click Either Button
- Click the large "+ Add New Link" button, OR
- Click the floating "+" button in the corner

### 2. Fill Out the Form
A popup will appear. Fill in these fields:

**Required:**
- **URL**: The web address (e.g., https://google.com)

**Optional but Recommended:**
- **Name**: Internal name (e.g., "Google")
- **Group**: Category name (e.g., "Search Engines")
- **Text**: What displays on the button (e.g., "Google")

**Display Type:**
- Choose: Text, NerdFont Icon, Image, or SVG

**Styling (optional):**
- Colors, sizes, fonts, etc.

### 3. Click "Add"
- The form will close
- Your link appears immediately!

---

## Example: Adding Google

1. Click "+ Add New Link" button
2. Fill in:
   - URL: `https://google.com`
   - Name: `Google`
   - Text: `Google`
   - Group: `Search`
3. Click "Add"
4. Done! ✅

---

## Troubleshooting

### "I don't see any buttons"
- Refresh the page (Ctrl+R or Cmd+R)
- Check browser console (F12) for errors
- Make sure `npx convex dev` is running

### "Button doesn't do anything"
- Check browser console (F12) for errors
- Look for "Add Link button clicked!" message
- Make sure JavaScript is enabled

### "Form shows error when adding"
- Make sure URL field is filled
- Check that Convex is running: `npx convex dev`
- Look at the error message for details

---

## Quick Reference

**Start Convex:**
```bash
cd convex-myhome
npx convex dev
```

**Open App:**
- Open `index.html` in your browser

**Add Link:**
- Click green "+ Add New Link" button
- OR click floating "+" button

**Edit Mode (F1):**
- Press F1 to see edit/delete buttons on existing links
- Not required for adding new links!

---

**Status**: ✅ Two "Add Link" buttons now available!
