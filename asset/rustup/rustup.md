Even smaller? Switch to the GNU toolchain (no MSVC at all)
If you never need to link with MSVC-produced code you can skip
Microsoft’s tools completely:

from scoop install rustup only not gnu nor msvc

scoop install mingw-msvcrt
rustup toolchain install stable-x86_64-pc-windows-gnu
rustup default stable-x86_64-pc-windows-gnu

The GNU toolchain ships its own gcc-based linker; nothing else is
required and the whole toolchain is < 400 MB.
(You will lose the ability to link with libraries built by MSVC.)