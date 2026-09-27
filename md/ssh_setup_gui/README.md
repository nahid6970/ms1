# SSH Setup Wizard

A Windows desktop wizard for setting up key-based SSH access from an Android Termux device to this PC. It detects the Windows account and LAN address, shows exactly what to run in Termux, accepts the copied public key, and can configure the Windows SSH service and firewall with an Administrator prompt.

The app keeps password login enabled while you test key access. After you confirm that key login works, the app can disable SSH password authentication. Your Android private key stays on the phone; only its public key is copied into Windows.

## Run

From PowerShell:

```powershell
cd C:\@delta\ms1\md\ssh_setup_gui
uv init --bare
uv add PyQt6
uv run python main.py
```

## Workflow

1. Copy the Android command shown in the app and run it in Termux.
2. Copy the complete `ssh-ed25519 ...` public key line printed by Termux and paste it into the app.
3. Choose **Install key + prepare PC** and approve the Windows Administrator prompt.
4. Copy and run the test command from Termux. Confirm key login works before selecting the confirmation checkbox.
5. Choose **Disable SSH password login** if you want SSH connections to use the key only.

The firewall rule created by the app is limited to the local subnet. The connection address can change when the PC reconnects to the network; use the address currently shown in the app.
