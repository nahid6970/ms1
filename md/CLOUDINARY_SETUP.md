# Cloudinary Setup Guide

## What is Cloudinary?

Cloudinary is a cloud-based image and video management service. It provides:
- Free image storage (25GB)
- Free bandwidth (25GB/month)
- CDN delivery (fast image loading)
- Direct browser uploads (no backend needed)

## Setup Steps

### 1. Create Account
- Go to: https://cloudinary.com/users/register_free
- Sign up with email (free tier)
- Verify email

### 2. Get Cloud Name
- After login, you'll see the dashboard
- Your **Cloud Name** is at the top left (e.g., `dwc7hjiub`)
- Copy this - you'll need it in your code

### 3. Create Upload Preset
- Click **Settings** (gear icon) → **Upload** tab
- Scroll to **Upload presets** section
- Click **Add upload preset**
- Configure:
  - **Preset name**: `myGallery` (or any name)
  - **Signing Mode**: **Unsigned** (important!)
  - **Folder**: `myGallery` (optional, organizes uploads)
- Click **Save**

### 4. Update Your Code
Replace in your HTML:
```javascript
const CLOUDINARY_CLOUD_NAME = "dwc7hjiub";
const CLOUDINARY_UPLOAD_PRESET = "myGallery";
```

## How Unsigned Uploads Work

**Unsigned preset** = Public upload endpoint (no API key needed)

When you upload:
```javascript
formData.append('file', file);
formData.append('upload_preset', 'myGallery');
formData.append('folder', 'myGallery');

fetch('https://api.cloudinary.com/v1_1/dwc7hjiub/image/upload', {
  method: 'POST',
  body: formData
});
```

Cloudinary returns:
```json
{
  "secure_url": "https://res.cloudinary.com/dwc7hjiub/image/upload/v123/myGallery/image.jpg",
  "public_id": "myGallery/image",
  "format": "jpg"
}
```

## Security Settings (Optional)

In your upload preset, you can restrict:
- **File types**: Images only (png, jpg, gif)
- **File size**: Max 10MB
- **Folder**: Lock to specific folder
- **Transformations**: Auto-optimize, resize, etc.

## Free Tier Limits

- **Storage**: 25GB
- **Bandwidth**: 25GB/month
- **Transformations**: 25 credits/month
- **Images**: Unlimited uploads

## Folder Structure

Your Cloudinary media library will look like:
```
Media Library/
├── sample/          (default demo folder - can delete)
├── myGallery/       (your app's images)
│   ├── image1.jpg
│   ├── image2.png
│   └── ...
```

## Managing Images

**Via Dashboard:**
- Go to Media Library
- Browse folders
- Delete/rename images
- Get URLs

**Via Code:**
- Upload: POST to `/image/upload`
- Delete: Requires API key (signed request)
- List: Requires API key

## Why No API Key Needed?

**Unsigned uploads** allow public uploads without exposing secrets:
- ✅ Anyone can upload (controlled by preset rules)
- ✅ No API key in frontend code
- ✅ Cloudinary validates via preset settings
- ❌ Can't delete images (requires API key)

For deletions, we delete the URL from our database (Convex), not from Cloudinary.

## Troubleshooting

**Upload fails:**
- Check preset is "Unsigned"
- Verify cloud name is correct
- Check browser console for errors

**Images not showing:**
- Check the returned `secure_url`
- Verify image uploaded in Cloudinary dashboard
- Check CORS (Cloudinary allows all origins by default)

**Wrong folder:**
- Check `folder` parameter in upload code
- Or set default folder in preset settings

## Alternative: Signed Uploads (Advanced)

If you need more control (delete, admin operations):
1. Add API key/secret to backend
2. Generate signed upload URLs
3. Use those URLs in frontend

But for simple image sharing, unsigned uploads are perfect.
