# Tailscale + nginx SSL Website Setup Guide

This guide documents how to set up a secure HTTPS website using Tailscale certificates and nginx on Windows.

## Prerequisites
- Tailscale installed and connected
- Windows machine
- HTML files to serve

## Step 1: Generate Tailscale SSL Certificate

1. Open command prompt/terminal
2. Generate certificate for your Tailscale domain:
   ```bash
   tailscale cert win6970.blowfish-owl.ts.net
   ```
   
   This creates two files:
   - `win6970.blowfish-owl.ts.net.crt` (public certificate)
   - `win6970.blowfish-owl.ts.net.key` (private key)

3. Move certificate files to a secure location (e.g., `C:\Users\nahid\`)

## Step 2: Download and Setup nginx

1. Download nginx for Windows from: https://nginx.org/en/download.html
2. Extract to: `D:\Downloads\nginx\`
3. Your nginx directory structure:
   ```
   D:\Downloads\nginx\
   ├── nginx.exe
   ├── conf\
   │   └── nginx.conf
   ├── html\
   └── logs\
   ```

## Step 3: Configure nginx

1. Edit `D:\Downloads\nginx\conf\nginx.conf`
2. Add this server block inside the `http { }` section:

```nginx
# Tailscale HTTPS server
server {
    listen       443 ssl;
    server_name  win6970.blowfish-owl.ts.net;
    
    ssl_certificate      C:/Users/nahid/win6970.blowfish-owl.ts.net.crt;
    ssl_certificate_key  C:/Users/nahid/win6970.blowfish-owl.ts.net.key;
    
    ssl_session_cache    shared:SSL:1m;
    ssl_session_timeout  5m;
    ssl_ciphers  HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers  on;
    
    location / {
        root   C:/Users/nahid/ms/db/5000_myhome;
        index  myhome.html;
    }
}
```

**Important notes:**
- Use forward slashes (`/`) in paths, even on Windows
- Update certificate paths to match where you stored them
- Update `root` path to your HTML files directory
- Update `index` to your main HTML file name

## Step 4: Test and Start nginx

1. Test configuration:
   ```cmd
   cd D:\Downloads\nginx
   nginx.exe -t
   ```

2. If test passes, start nginx:
   ```cmd
   nginx.exe
   ```

3. Verify nginx is running:
   ```cmd
   tasklist | findstr nginx
   ```

## Step 5: Access Your Site

From any device on your Tailnet, visit: `https://win6970.blowfish-owl.ts.net`

**Note:** You may see certificate warnings in browsers - this is normal for Tailscale certificates. Click "Advanced" → "Proceed" - the connection is still secure within your Tailnet.

## File Structure

```
Project Files:
C:\Users\nahid\ms\db\5000_myhome\
└── myhome.html

SSL Certificates:
C:\Users\nahid\
├── win6970.blowfish-owl.ts.net.crt
└── win6970.blowfish-owl.ts.net.key

nginx Installation:
D:\Downloads\nginx\
├── nginx.exe
├── conf\nginx.conf
└── html\
```

## nginx Management Commands

```cmd
# Start nginx
D:\Downloads\nginx\nginx.exe

# Stop nginx
D:\Downloads\nginx\nginx.exe -s stop

# Reload configuration (after changes)
D:\Downloads\nginx\nginx.exe -s reload

# Test configuration
D:\Downloads\nginx\nginx.exe -t

# Check if running
tasklist | findstr nginx
```

## Regenerating Certificates

If you need new certificates (they expire or you lose them):

1. Run the same command:
   ```bash
   tailscale cert win6970.blowfish-owl.ts.net
   ```

2. Update nginx configuration with new certificate paths
3. Reload nginx:
   ```cmd
   nginx.exe -s reload
   ```

## Important Notes

- **Site availability**: The website is only online when your PC is running
- **Security**: Never commit certificate files (`.crt`, `.key`) to version control
- **Firewall**: You may need to allow nginx through Windows Firewall
- **Tailnet access**: Only devices connected to your Tailnet can access the site

## Troubleshooting

**Site doesn't load:**
- Check if nginx is running: `tasklist | findstr nginx`
- Check Windows Firewall settings
- Verify Tailscale is connected on both devices

**Certificate errors:**
- Verify certificate files exist at specified paths
- Check file permissions
- Regenerate certificates if needed

**File not found errors:**
- Confirm HTML file exists at the specified path
- Check file permissions
- Verify `root` and `index` settings in nginx.conf

## Your Setup Details

- **Domain**: win6970.blowfish-owl.ts.net
- **nginx location**: D:\Downloads\nginx\
- **Website files**: C:\Users\nahid\ms\db\5000_myhome\
- **Main file**: myhome.html
- **Certificates**: C:\Users\nahid\