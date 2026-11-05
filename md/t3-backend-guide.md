# T3 Code Backend (Headless Server) Documentation

This guide covers the installation, launch (serving), updating, and removal of both the **Stable** and **Nightly** headless backend streams for T3 Code.

---

## 1. Stable Stream

### Installation

#### Method A: Global via NPM
Installs the package globally within your Node environment alongside your other tools.
```bash
npm install -g t3
```

#### Method B: Native Installer Script
Installs T3 Code as an optimized standalone system binary.
* **macOS / Linux:**
  ```bash
  curl -fsSL https://t3.codes/install.sh | sh
  ```
* **Windows (PowerShell):**
  ```powershell
  irm https://t3.codes/install.ps1 | iex
  ```

---

### Launching & Serving

#### Foreground (Instant Start)
Runs the backend directly in your active terminal context.
```bash
t3 serve
```
*(To boot it and target a specific local project folder directly, navigate to the folder and run `t3 .`)*

#### Managed Background Service
Registers the backend server as a persistent system daemon that manages itself.
```bash
t3 service install
t3 service start
```

---

### Uninstallation

#### If installed via NPM:
```bash
npm uninstall -g t3
```

#### If installed via Native Script:
* **macOS / Linux:**
  ```bash
  t3 service uninstall
  rm -rf ~/.t3
  ```
* **Windows (PowerShell):**
  ```powershell
  t3 service uninstall
  Remove-Item -Recurse -Force "$HOME\.t3"
  ```

---

## 2. Nightly Stream

The Nightly stream contains prerelease updates, featuring the newest orchestration engines and cross-provider terminal features.

### Installation

#### Method A: Global via NPM
```bash
npm install -g t3@nightly
```

#### Method B: Native Installer Script
Injects the `T3CODE_CHANNEL=nightly` variable into the installer routine to pull the latest cutting-edge binary.
* **macOS / Linux:**
  ```bash
  T3CODE_CHANNEL=nightly curl -fsSL https://t3.codes/install.sh | sh
  ```
* **Windows (PowerShell):**
  ```powershell
  $env:T3CODE_CHANNEL="nightly"; irm https://t3.codes/install.ps1 | iex
  ```

---

### Launching & Serving

#### Instant Execution (Zero-Install Runner)
Executes the nightly package on the fly without altering your global node modules.
```bash
npx t3@nightly serve
```
*(To initialize it within a specific codebase workspace directly, execute `npx t3@nightly .`)*

#### Standard Execution (After Global/Native Install)
If permanently installed, standard `t3` commands default to your active track environment.
```bash
t3 serve
```

#### Managed Background Service
```bash
t3 service install
t3 service start
```

---

### Updating Nightly
Since nightly packages receive multiple updates daily, push modifications down to your daemon manually using:
```bash
npx t3@nightly service update
```

---

### Uninstallation
Follow the exact same workflow as the Stable stream to detach the global package or destroy local configuration directories:

#### If installed via NPM:
```bash
npm uninstall -g t3
```

#### If installed via Native Script:
* **macOS / Linux:**
  ```bash
  t3 service uninstall
  rm -rf ~/.t3
  ```
* **Windows (PowerShell):**
  ```powershell
  t3 service uninstall
  Remove-Item -Recurse -Force "$HOME\.t3"
  ```

---

## 3. Maintenance & Process Managers (Optional)

### Cleaning NPX Cache
If your `npx` execution routines conflict or accidentally serve stale versions, reset your Node application workspace:
```bash
npx clear-npx-cache
```

### Alternative Process Management (PM2)
If you prefer managing your server instances via **PM2** instead of native system daemons:
```bash
# Install PM2 globally
npm install -g pm2

# Spin up the server engine 
pm2 start t3 --name "t3-backend" -- serve

# Control commands
pm2 status
pm2 logs t3-backend
pm2 stop t3-backend
pm2 delete t3-backend
```
