# Rust GUI Frameworks: Choosing and Customizing a Desktop UI

This guide compares four practical routes for building a desktop GUI with Rust: **egui + eframe**, **Slint**, **iced**, and **Tauri**.

## Quick recommendation

- Start with **egui + eframe** for a Rust-first app with a highly custom visual style, quick iteration, and a canvas or dashboard feel.
- Choose **Slint** when you want to describe layouts declaratively and keep UI design separate from Rust application logic.
- Choose **iced** for a structured, message-driven Rust UI with a conventional widget hierarchy.
- Choose **Tauri** when CSS and web frontend tools are the best way to achieve the design you want, with Rust handling native functionality.

All four can be customized. The main difference is how you build and style the interface.

## Comparison

| Framework | How the UI is built | Theming and customization | Good fit |
|---|---|---|---|
| **egui + eframe** | Rust code describes the UI each frame (immediate mode). | Set global or local colors, widget states, spacing, rounding, fonts, and text styles. Draw custom shapes and make custom widgets for a distinctive look. | Tools, dashboards, editors, configuration apps, and experimental interfaces. |
| **Slint** | UI is described in `.slint` markup and connected to Rust logic. | Define component properties and styles in the UI language; reuse components and build a consistent design system. | Apps with deliberately designed screens and a clear split between UI and logic. |
| **iced** | Rust widgets and application state follow an Elm-style message/update/view pattern. | Pick built-in themes or define theme palettes and per-widget style functions; custom widgets are possible. | Structured, maintainable apps that use a conventional set of controls and screens. |
| **Tauri** | A web frontend runs in a system webview; Rust provides backend commands and native access. | Use CSS and the frontend ecosystem for broad control over layout, animation, effects, and responsive behavior. | Web-style interfaces, or when you already know HTML/CSS and a frontend framework. |

## How far can egui customization go?

Quite far. egui exposes style settings for colors, spacing, widget interaction states, corner radii, shadows, and text. You can load fonts, style individual UI regions, draw custom shapes, and implement widgets yourself. This makes it possible to create a coherent branded interface rather than just changing the default dark or light theme.

The trade-off is that egui is immediate mode: the UI is described during each frame, rather than being assembled as a persistent widget tree. That model is productive for tools and interactive visualizations, though it may feel unfamiliar if you expect a Qt-style designer or conventional retained-mode widgets.

## Practical choice guide

### Pick egui + eframe if

- You want to write the interface primarily in Rust.
- You care about custom graphics, controls, or a distinctive visual style.
- You want a fast path to a prototype or a desktop utility.

### Pick Slint if

- You prefer a declarative UI description separate from application logic.
- You want reusable visual components and a design-focused workflow.
- You want the option of editor tooling and live preview through Slint's tooling.

### Pick iced if

- You prefer explicit application state and message handling.
- You want a Rust widget toolkit with built-in themes plus custom styles.
- You like an architecture that keeps state updates and view construction organized.

### Pick Tauri if

- CSS gives you the most comfortable route to the exact look you want.
- You want to use a web frontend framework or existing web UI skills.
- You are comfortable maintaining a frontend and Rust backend together.

## Tauri on Windows with the GNU toolchain

The Rust setup guide in `C:\@delta\ms1\md\rustup.md` selects **GNU**. Tauri's current Windows documentation recommends **MSVC**, requires Microsoft's C++ Build Tools, and uses Edge WebView2. Tauri's Windows installer guide says it officially supports the MSVC Windows target. A GNU configuration may work for some projects, but it is outside Tauri's documented support path and can fail during linking or resource/installer generation.

### Common problems

| Symptom | Likely cause | Basic strategy |
|---|---|---|
| `icons/icon.ico` not found | The app icon file is missing from the project. This is a project asset issue, not proof of a GNU linker problem. | Add a valid Windows `.ico` at the configured path, then retry the build. |
| `link.exe` missing, MSVC linker errors, or Windows SDK libraries not found | The MSVC C++ build tools or Windows SDK are missing. | Install Visual Studio Build Tools with **Desktop development with C++** and the Windows SDK, then open a fresh terminal. |
| `rustup show active-toolchain` reports `...windows-gnu` inside the Tauri project | Cargo is using the GNU toolchain. | Use a project-local MSVC toolchain override (steps below), then confirm the active toolchain again. |
| Missing resource compiler (`rc.exe`/`windres`) or resource compilation fails | The selected toolchain cannot find a compatible Windows resource compiler. | Prefer the MSVC toolchain and Windows SDK. There is an experimental MinGW binutils workaround below, but it is not a supported general fix. |
| Linker errors mention missing `.lib` files, unresolved symbols, or incompatible libraries | A dependency may provide binaries for a different toolchain or ABI. | Rebuild native dependencies for the same target/toolchain as the app, or use MSVC consistently. Avoid mixing MSVC-built and GNU-built native libraries. |
| The app builds but does not start because WebView2 is unavailable | The Edge WebView2 runtime is missing or damaged. | Install or repair the WebView2 Evergreen Runtime. It is already present on most supported Windows 10 and Windows 11 systems. |
| The app builds but installer bundling fails | Packaging tools or Windows-specific requirements are missing. | First verify `tauri dev`/`tauri build`; then follow Tauri's Windows installer guide. MSI creation may also require the Windows VBScript optional feature. |

### Recommended strategy: keep GNU globally, use MSVC in Tauri projects

You can keep GNU as your normal Rust toolchain and add MSVC alongside it. In PowerShell, inside the Tauri project's folder, run these commands yourself:

```powershell
rustup toolchain install stable-x86_64-pc-windows-msvc
rustup override set stable-x86_64-pc-windows-msvc
rustup show active-toolchain
```

The override applies only to that project folder and its subfolders. It leaves your global default unchanged. Also install Microsoft's C++ Build Tools with **Desktop development with C++** and a Windows SDK. WebView2 is usually already installed on Windows 10/11; install its Evergreen Runtime if it is missing.

### Build Tools disk space

You do not need the full Visual Studio IDE. Microsoft's current Visual Studio Build Tools requirements list **2.3–60 GB**, depending on selected features; this is the range for Build Tools overall, not a fixed size for the C++ workload by itself. For a smaller install, select only the C++ workload, the MSVC x64/x86 toolset, and one Windows SDK, and leave optional tools unchecked. The Visual Studio Installer shows the specific disk-space estimate for your selection before installation.

To remove the project-local override later, run this from the same project folder:

```powershell
rustup override unset
```

### If you must experiment with GNU

A Tauri maintainer has documented a workaround for a default app that lacked a resource compiler: install MSYS2's MinGW64 binutils package and add its `mingw64\bin` directory to `PATH` for the build. That can provide tools such as `windres`, but it does not make GNU an officially supported Tauri Windows target. Other link, dependency, or packaging failures may remain. Treat it as a project-specific experiment and keep a working MSVC setup available for reliable development and releases.

### Which route fits this setup?

- For the existing GNU-only installation and a Rust-first custom GUI, keep using **egui + eframe** (or try Slint/iced).
- For Tauri, use the **project-local MSVC strategy** above. This avoids changing the global GNU default while matching Tauri's documented Windows setup.
- Use the GNU workaround only when you have a specific reason to keep every build tool on GNU and are willing to troubleshoot unsupported cases.

### Result from the RustBuildCheck demo

The simple Tauri demo in `C:\Users\nahid\Desktop\RustBuildCheck` was reported to build and launch successfully with the active `x86_64-pc-windows-gnu` toolchain. Its first build stopped because `icons/icon.ico` was missing; after adding the icon, the app ran. Since Tauri renders the HTML/CSS/JavaScript frontend in WebView2, this also confirms WebView2 worked for this demo on this machine.

This is useful evidence that a basic Tauri app can run in this GNU environment. It does not establish support for every Tauri plugin, native dependency, or installer workflow. Tauri's official Windows support guidance still specifies MSVC.

## Suggested learning order

1. Build a small **egui + eframe** window to confirm the Rust GUI workflow.
2. Add a custom theme: colors, typography, spacing, and widget states.
3. If you prefer markup-based layout, try the same screen in **Slint**.
4. Choose **Tauri** if CSS and web frontend tools feel more natural for the finished design.

The first build of a GUI project will download its Rust dependencies, so it needs network access. Use the build commands yourself when you are ready.

## Official references

- [egui documentation](https://docs.rs/egui/latest/egui/) — style, visuals, spacing, fonts, and widgets.
- [Slint documentation](https://docs.slint.dev/latest/docs/slint/) — declarative UI language, components, and Rust integration.
- [iced documentation](https://docs.iced.rs/iced/) — application patterns, themes, widget styling, and custom widgets.
- [Tauri overview](https://tauri.app/start/) — Rust backend with web frontend.
- [Tauri frontend configuration](https://tauri.app/start/frontend/) — supported frontend approaches.
- [Tauri prerequisites](https://v2.tauri.app/start/prerequisites/) — Windows dependencies and the recommended MSVC Rust toolchain.
- [Tauri Windows installer guide](https://v2.tauri.app/distribute/windows-installer/) — states the supported Windows target and installer notes.
- [Tauri GNU toolchain discussion](https://github.com/tauri-apps/tauri/issues/12716) — maintainer-described MinGW binutils workaround for a resource compiler issue.
- [Visual Studio Build Tools system requirements](https://learn.microsoft.com/en-us/visualstudio/releases/2026/vs-system-requirements) — current overall disk-space range for Build Tools.

