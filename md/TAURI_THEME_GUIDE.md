# Cyberpunk UI Theme Guide for Rust + Tauri

This guide adapts the Cyberpunk style from `THEME_GUIDE.md` for Tauri applications. Tauri uses a web frontend for its interface and Rust for native application logic, so apply the visual theme with CSS and keep native operations behind Tauri commands.

The examples target Tauri 2 and a vanilla HTML/CSS/TypeScript frontend. The same CSS works with React, Vue, Svelte, or other frontend frameworks.

## 1. Color Palette

Define the theme as CSS custom properties so every view and component can reuse the same colors.

```css
:root {
  color-scheme: dark;

  /* CYBERPUNK THEME PALETTE */
  --cp-bg: #050505;       /* Main window background */
  --cp-panel: #111111;    /* Panel/input background */
  --cp-yellow: #FCEE0A;   /* Accent: yellow */
  --cp-cyan: #00F0FF;     /* Accent: cyan */
  --cp-red: #FF003C;      /* Accent: red */
  --cp-green: #00ff21;    /* Accent: green */
  --cp-orange: #ff934b;   /* Accent: orange */
  --cp-dim: #3a3a3a;      /* Borders/inactive controls */
  --cp-text: #E0E0E0;     /* Primary text */
  --cp-subtext: #808080;  /* Secondary text */
}
```

## 2. Fonts

* **Primary font:** `Consolas`
* **Fallback:** `ui-monospace`, `SFMono-Regular`, `Menlo`, `monospace`

Consolas is installed on most Windows systems. The fallback list keeps the interface readable on macOS and Linux.

## 3. Global CSS

Add these rules to the app's main stylesheet, such as `src/styles.css` or `src/style.css`.

```css
* {
  box-sizing: border-box;
}

html,
body,
#app {
  width: 100%;
  min-width: 320px;
  min-height: 100%;
  margin: 0;
}

body {
  background: var(--cp-bg);
  color: var(--cp-text);
  font-family: Consolas, ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 14px;
}

button,
input,
select,
textarea {
  font: inherit;
}

::selection {
  color: var(--cp-bg);
  background: var(--cp-cyan);
}

:focus-visible {
  outline: 2px solid var(--cp-cyan);
  outline-offset: 2px;
}
```

## 4. Component Styles

### Panels and Sections

```css
.panel {
  background: var(--cp-panel);
  border: 1px solid var(--cp-dim);
  padding: 16px;
}

.panel__title {
  margin: 0 0 12px;
  color: var(--cp-yellow);
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
```

### Inputs

```css
input,
select,
textarea {
  width: 100%;
  padding: 8px 10px;
  color: var(--cp-cyan);
  background: var(--cp-panel);
  border: 1px solid var(--cp-dim);
  border-radius: 0;
}

input:focus,
select:focus,
textarea:focus {
  border-color: var(--cp-cyan);
  outline: none;
}

input::placeholder,
textarea::placeholder {
  color: var(--cp-subtext);
}
```

### Buttons

```css
.button {
  padding: 8px 14px;
  color: var(--cp-text);
  background: var(--cp-dim);
  border: 1px solid var(--cp-dim);
  border-radius: 0;
  font-weight: 700;
  cursor: pointer;
  transition: color 120ms ease, background-color 120ms ease, border-color 120ms ease;
}

.button:hover {
  color: var(--cp-yellow);
  background: #2a2a2a;
  border-color: var(--cp-yellow);
}

.button:active {
  color: var(--cp-bg);
  background: var(--cp-yellow);
}

.button--danger:hover {
  color: var(--cp-red);
  border-color: var(--cp-red);
}
```

### Checkbox

```css
.checkbox {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--cp-text);
  cursor: pointer;
}

.checkbox input {
  width: 14px;
  height: 14px;
  margin: 0;
  accent-color: var(--cp-yellow);
}
```

### Context Menu

```css
.context-menu {
  min-width: 180px;
  padding: 4px;
  color: var(--cp-text);
  background: var(--cp-panel);
  border: 1px solid var(--cp-cyan);
  box-shadow: 0 8px 24px #000a;
}

.context-menu button {
  display: block;
  width: 100%;
  padding: 8px 10px;
  text-align: left;
  color: inherit;
  background: transparent;
  border: 0;
  cursor: pointer;
}

.context-menu button:hover,
.context-menu button:focus-visible {
  color: var(--cp-bg);
  background: var(--cp-cyan);
}
```

### Scrollbars

```css
* {
  scrollbar-color: var(--cp-cyan) var(--cp-bg);
  scrollbar-width: thin;
}

::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

::-webkit-scrollbar-track {
  background: var(--cp-bg);
}

::-webkit-scrollbar-thumb {
  min-width: 20px;
  min-height: 20px;
  background: var(--cp-cyan);
  border: 2px solid var(--cp-bg);
  border-radius: 5px;
}
```

## 5. CyberButton Component

In a frontend framework, implement this as a reusable component with theme variants. For vanilla CSS, use custom properties to let each button choose its colors.

```css
.cyber-button {
  --button-bg: var(--cp-panel);
  --button-text: var(--cp-text);
  --button-hover-bg: #202020;
  --button-hover-text: var(--cp-yellow);
  --button-border: var(--cp-yellow);

  min-height: 56px;
  padding: 10px 14px;
  color: var(--button-text);
  background: var(--button-bg);
  border: 1px solid var(--button-border);
  border-radius: 0;
  font-weight: 700;
  text-align: left;
  cursor: pointer;
  transition: background-color 120ms ease, color 120ms ease;
}

.cyber-button:hover {
  color: var(--button-hover-text);
  background: var(--button-hover-bg);
}

.cyber-button--cyan {
  --button-border: var(--cp-cyan);
  --button-hover-text: var(--cp-cyan);
}
```

```html
<button class="cyber-button cyber-button--cyan">SYSTEM STATUS<br />ONLINE</button>
```

Use normal HTML text and CSS for layout. Avoid injecting user-provided text as HTML; use `textContent` or framework text interpolation.

## 6. Tauri Frontend-to-Rust Commands

Keep filesystem, process, and other native operations in Rust commands. The frontend calls registered commands through Tauri's API. Example for a TypeScript frontend:

```ts
import { invoke } from "@tauri-apps/api/core";

const status = await invoke<string>("get_status");
```

Expose the command from `src-tauri/src/lib.rs` (the library entry point used by common Tauri templates):

```rust
#[tauri::command]
fn get_status() -> String {
    "SYSTEM READY".to_string()
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![get_status])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

Keep command inputs and outputs small and typed. Return `Result<T, E>` when a command can fail so the frontend can display an error state. Do not grant broad filesystem or shell permissions just to support a visual component; configure only the capabilities and plugin permissions the app needs.

## 7. Boilerplate Starter UI

This is a small HTML/CSS/TypeScript frontend example. Put the markup in the frontend entry page and load `src/main.ts` from it. Tauri projects often use Vite, but the theme itself is framework-independent.

```html
<main class="app-shell">
  <header class="app-header">
    <h1>CYBERPUNK CONTROL</h1>
    <span id="status" class="status">CONNECTING...</span>
  </header>

  <section class="panel">
    <h2 class="panel__title">User Input</h2>
    <label for="username">Username</label>
    <input id="username" placeholder="Enter username" />
    <div class="actions">
      <button id="execute" class="button">EXECUTE</button>
      <button id="settings" class="button">⚙ SETTINGS</button>
    </div>
  </section>
</main>
```

```css
.app-shell {
  display: grid;
  gap: 16px;
  max-width: 900px;
  margin: 0 auto;
  padding: 24px;
}

.app-header,
.actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.app-header h1 {
  color: var(--cp-yellow);
  font-size: 1.1rem;
}

.status {
  color: var(--cp-green);
}

.actions {
  justify-content: flex-start;
  margin-top: 16px;
}
```

```ts
import { invoke } from "@tauri-apps/api/core";
import "./styles.css";

const status = document.querySelector<HTMLElement>("#status")!;
const execute = document.querySelector<HTMLButtonElement>("#execute")!;
const username = document.querySelector<HTMLInputElement>("#username")!;

status.textContent = "SYSTEM READY";

execute.addEventListener("click", async () => {
  execute.disabled = true;
  status.textContent = "PROCESSING...";

  try {
    status.textContent = await invoke<string>("greet", {
      name: username.value,
    });
  } catch (error) {
    status.textContent = `ERROR: ${String(error)}`;
  } finally {
    execute.disabled = false;
  }
});
```

Match the frontend command name and argument keys with the Rust command. For example, `invoke("greet", { name: value })` calls a `#[tauri::command] fn greet(name: String)` command.

## 8. Settings and Restart Behavior

* Keep a `⚙ SETTINGS` entry point if the application has user-configurable options. Store settings with the app's configured persistence solution, and use paths provided by Tauri's app path APIs rather than assuming the process working directory.
* During development, use the Vite/Tauri development workflow to pick up code changes. A production restart feature should be implemented as a deliberate Rust command or plugin capability and exposed only to the app windows that need it.
* A frontend-only refresh can reload the webview, but it does not restart the Rust process. Do not label a webview reload as a full application restart.

## 9. Tauri Project Notes

* Tauri is a native shell around a frontend webview. Window chrome and title-bar behavior are configured through Tauri window settings; CSS styles the content rendered inside the webview.
* Tauri serves built frontend assets in production. Configure the frontend build output and dev server in `src-tauri/tauri.conf.json` (or the project's supported configuration format).
* Use Tauri APIs or plugins for native features. Avoid assuming browser APIs like `window.close()` or filesystem access behave like a normal website or have unrestricted native access.
* Tauri 2 uses capabilities to grant frontend windows access to commands and plugin APIs. Keep permissions scoped to the features the app actually uses.

## References

* [Tauri frontend configuration](https://v2.tauri.app/start/frontend/)
* [Tauri project creation](https://v2.tauri.app/start/create-project/)
* [Tauri capabilities](https://v2.tauri.app/security/capabilities/)
* [Tauri configuration reference](https://v2.tauri.app/reference/config/)
