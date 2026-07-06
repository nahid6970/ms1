# Building `caut` on Windows Without Visual Studio

If you do not want to install the heavy Microsoft Visual Studio / C++ Build Tools, you can build `caut` using a lightweight GNU toolchain via **Scoop** and **Rust's GNU target**.

Follow these steps:

### 1. Install Scoop (if not already installed)
Run the following in PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
```

### 2. Install MinGW (lightweight GNU compiler/linker)
Install MinGW using Scoop:
```powershell
scoop install mingw
```

### 3. Install and Set Nightly GNU Toolchain
Install the nightly GNU toolchain so that even Cargo's build scripts use the GNU linker (instead of falling back to MSVC's `link.exe`):
```powershell
rustup toolchain install nightly-x86_64-pc-windows-gnu
```

Set it as the override toolchain for the project directory:
```powershell
rustup override set nightly-x86_64-pc-windows-gnu
```

### 4. Build the Project
Run the cargo build command (it will automatically use the directory's toolchain override):
```powershell
cargo build --release
```

The compiled binary will be generated at:
`target\release\caut.exe`
