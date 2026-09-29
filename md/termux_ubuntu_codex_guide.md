# Guide: Setting Up Ubuntu & Fixing Codex in Termux (ARM64)

This guide documents the steps taken to install and set up an Ubuntu container inside Termux on an ARM64 Android device, and how to resolve the Codex CLI sandbox prerequisite issue (`bubblewrap`).

---

## 1. Installing Ubuntu via `proot-distro`

Since standard Arch Linux container images are targeted for `x86_64` (AMD64) architectures, we used Ubuntu (`aarch64`) as our proot distribution.

### Commands Run:
```bash
# 1. Install the Ubuntu distribution container
proot-distro install ubuntu

# 2. Log into the Ubuntu container shell
proot-distro login ubuntu
```

---

## 2. Setting up the Ubuntu Environment

Once logged into the container, we updated the package lists and installed development essentials:

### Commands Run:
```bash
apt update && apt upgrade -y
apt install -y curl wget git build-essential python3 python3-pip nano
```

---

## 3. Fixing the Codex CLI / Bubblewrap Issue

### The Problem:
When launching `codex` inside the Ubuntu container, the app server daemon failed with the following error:
> `ERROR codex_app_server: Codex could not find bubblewrap on PATH. Install bubblewrap with your OS package manager.`

### The Solution:
Codex requires `bubblewrap` for sandboxing. We resolved this by installing `bubblewrap` using Ubuntu's package manager (`apt`).

### Commands Run:
```bash
apt update
apt install -y bubblewrap
```

After installing `bubblewrap`, launching `codex` or running with `--no-daemon` works successfully:
```bash
codex
# Or without background daemon if needed:
codex --no-daemon
```
