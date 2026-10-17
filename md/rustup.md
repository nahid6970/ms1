# Install Rust with the GNU toolchain on Windows

This setup uses Rust's GNU toolchain instead of MSVC. Choose it if you do not need to link Rust programs against libraries built with MSVC.

## What this setup installs

- **rustup** — installs and manages Rust toolchains.
- **MinGW-w64** (`mingw-msvcrt`) — provides the GNU linker and related tools needed by the Windows GNU toolchain.
- **Stable GNU Rust toolchain** — the stable Rust compiler targeting `x86_64-pc-windows-gnu`.

## Prerequisite

Install [Scoop](https://scoop.sh/) if it is not already available in PowerShell.

## Install

Run these commands in PowerShell, in order:

```powershell
scoop install rustup
scoop install mingw-msvcrt
rustup toolchain install stable-x86_64-pc-windows-gnu
rustup default stable-x86_64-pc-windows-gnu
```

The first two commands install the Rust manager and GNU linker tools. The last two install and select the stable GNU Rust toolchain as the default.

## Verify

```powershell
rustup show active-toolchain
rustc --version
cargo --version
```

The active toolchain should be `stable-x86_64-pc-windows-gnu`.

## Trade-off

This configuration avoids the Microsoft C++ Build Tools. Rust projects that need to link against libraries built with MSVC may not work with this toolchain. The GNU toolchain includes a GCC-based linker and is described as being under 400 MB; actual download size can vary.
