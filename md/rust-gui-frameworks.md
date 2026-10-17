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

## Note for this Windows Rust setup

The Rust installation guide in `C:\@delta\ms1\md\rustup.md` selects the **GNU** toolchain. The current Tauri Windows prerequisites guide recommends the **MSVC** Rust toolchain and requires Microsoft's C++ Build Tools and Edge WebView2. If you choose Tauri on Windows, plan to install/select the MSVC toolchain and required build tools too. The GNU-only setup is a better match for trying a small eframe app first.

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
- [Tauri prerequisites](https://v2.tauri.app/start/prerequisites/) — platform build requirements, including Windows/MSVC.

