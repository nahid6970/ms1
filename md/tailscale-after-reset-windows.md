# Tailscale after Windows reset

Use this checklist after resetting a Windows PC and reinstalling Tailscale.

## 1. Open PowerShell as Administrator

Tailscale on Windows needs its service running before CLI commands work.

```powershell
Get-Service Tailscale
Start-Service Tailscale
Set-Service Tailscale -StartupType Automatic
```

If `Get-Service Tailscale` says the service does not exist, reinstall Tailscale using the official Windows installer, then run the commands above again.

## 2. Log in again

If the tray button does not open a browser, use the CLI:

```powershell
tailscale logout
tailscale up --qr
```

If you do not want to use QR login, use an auth key instead:

```powershell
tailscale up --auth-key=tskey-auth-XXXXXXXXXXXXXXXX
```

Sign in with the same identity provider account used for the old tailnet.

## 2.1 Device key expiry

There is no local `tailscale` command that permanently disables device key expiry.

- Device key expiry is managed on the device record in the admin console or by the Tailscale API.
- For trusted long-lived devices, disable key expiry after the device joins.
- If the device is tagged, key expiry is disabled by default.

To disable device key expiry in the admin console:

1. Open the `Machines` page in the Tailscale admin console.
2. Find the device.
3. Click the three dots `...` on the device row.
4. Select `Disable key expiry` from the context menu.

If the device key is already expired, reconnect with:

```powershell
tailscale up --force-reauth
```

## 3. Check the machine IP and subnet

Find the LAN IP and subnet mask:

```powershell
ipconfig
```

If the PC IP is something like `192.168.0.101` and the mask is `255.255.255.0`, then the subnet is:

```powershell
192.168.0.0/24
```

## 4. Advertise the subnet route

Run this on the PC that will act as the subnet router:

```powershell
tailscale set --advertise-routes=192.168.0.0/24
```

Replace `192.168.0.0/24` if your LAN uses a different subnet.

## 5. Advertise the exit node

To let this PC act as an exit node:

```powershell
tailscale set --advertise-exit-node
```

## 6. Approve routes in the admin console

After the device appears in the Tailscale admin console:

1. Open the `Machines` page.
2. Select the device.
3. Open `Edit route settings`.
4. Approve the subnet route.
5. Enable `Use as exit node` if you want this PC to be an exit node.

## 7. Verify everything

Useful checks:

```powershell
tailscale status
tailscale ip -4
tailscale netcheck
```

## 8. Common commands

```powershell
tailscale up
tailscale down
tailscale logout
tailscale set --advertise-routes=192.168.0.0/24
tailscale set --advertise-exit-node
```

## Notes

- Subnet routing and exit-node use are separate features.
- Other devices in your tailnet must still choose the subnet route or exit node they want to use.
- If you reset Windows again, the old device entry may still exist in the admin console. Remove it there if you do not need it anymore.
