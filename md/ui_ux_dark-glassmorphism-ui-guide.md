# Dark Glassmorphism UI Design System

A reusable design reference for building premium dark-themed web interfaces with glassmorphism, animated backgrounds, color-coded button systems, and micro-animations.

---

## 1. Foundations

### Typography

Use [Inter](https://fonts.google.com/specimen/Inter) for UI text and [JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono) for monospaced/data displays.

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

```css
body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.data-display {
    font-family: 'JetBrains Mono', monospace;
}
```

### Base Page Setup

Dark background with centered content and no scroll bleed.

```css
*, *::before, *::after {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', sans-serif;
    background: #080a12;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow-x: hidden;
    position: relative;
}
```

---

## 2. Color Palette & CSS Variables

All colors are defined as CSS custom properties on `:root`. The palette uses low-opacity `rgba()` values over a dark base to create the glassmorphism effect.

```css
:root {
    /* ── Card / Container ─────────────────────── */
    --body-bg: linear-gradient(165deg, #1c1f2e 0%, #141622 50%, #0f1119 100%);
    --body-border: #2a2d3e;
    --body-shadow: 0 30px 80px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.03);

    /* ── Display / Content Panel ──────────────── */
    --display-bg: linear-gradient(180deg, #1e2235 0%, #171a2a 100%);
    --display-border: rgba(255,255,255,0.06);
    --display-text: #e8edf5;
    --display-text-dim: rgba(200,210,230,0.45);
    --display-glow: rgba(100,140,255,0.06);

    /* ── Status / Indicator Dots ──────────────── */
    --indicator-active: #60a5fa;
    --indicator-dim: rgba(150,160,180,0.2);

    /* ── Button Tokens ────────────────────────── */
    --btn-radius: 10px;
    --btn-gap: 8px;

    /* Primary (number/default) */
    --num-bg: rgba(255,255,255,0.05);
    --num-hover: rgba(255,255,255,0.1);
    --num-text: #e2e8f0;

    /* Accent (operators/actions) — Indigo */
    --op-bg: rgba(99,102,241,0.12);
    --op-hover: rgba(99,102,241,0.25);
    --op-text: #a5b4fc;

    /* Secondary (functions) — Sky Blue */
    --func-bg: rgba(56,189,248,0.08);
    --func-hover: rgba(56,189,248,0.18);
    --func-text: #7dd3fc;

    /* Toggle / Shift — Amber */
    --shift-bg: rgba(251,191,36,0.15);
    --shift-active-bg: rgba(251,191,36,0.3);
    --shift-text: #fbbf24;

    /* Mode — Purple */
    --mode-bg: rgba(167,139,250,0.1);
    --mode-text: #c4b5fd;

    /* Warning / Delete — Orange */
    --del-bg: rgba(251,146,60,0.1);
    --del-text: #fdba74;

    /* Danger / Clear — Red */
    --ac-bg: rgba(248,113,113,0.12);
    --ac-text: #fca5a5;

    /* CTA / Submit — Indigo Gradient */
    --eq-bg: linear-gradient(135deg, #4f46e5, #6366f1, #818cf8);
    --eq-hover: linear-gradient(135deg, #4338ca, #4f46e5, #6366f1);
    --eq-text: #ffffff;
    --eq-shadow: 0 4px 20px rgba(79,70,229,0.35);

    /* Success / Memory — Emerald */
    --mem-bg: rgba(52,211,153,0.08);
    --mem-text: #6ee7b7;
}
```

> [!TIP]
> The key to glassmorphism: use **low-opacity rgba backgrounds** (`0.05`–`0.15`) with a **1px semi-transparent border** and optionally `backdrop-filter: blur()`. This lets the dark background and floating orbs bleed through.

---

## 3. Animated Background (Floating Orbs)

Soft, blurred gradient orbs that drift slowly behind the UI. Creates depth and visual interest without being distracting.

### HTML

```html
<div class="bg-mesh">
    <div class="orb"></div>
    <div class="orb"></div>
    <div class="orb"></div>
</div>
```

### CSS

```css
.bg-mesh {
    position: fixed;
    inset: 0;
    z-index: 0;
    overflow: hidden;
    pointer-events: none;
}

.bg-mesh .orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(120px);
    opacity: 0.3;
}

/* Orb 1 — Top-left, indigo */
.bg-mesh .orb:nth-child(1) {
    width: 600px; height: 600px;
    background: radial-gradient(circle, #4f46e5, transparent 70%);
    top: -20%; left: -15%;
    animation: drift 25s ease-in-out infinite;
}

/* Orb 2 — Bottom-right, sky blue */
.bg-mesh .orb:nth-child(2) {
    width: 450px; height: 450px;
    background: radial-gradient(circle, #0ea5e9, transparent 70%);
    bottom: -15%; right: -10%;
    animation: drift 20s ease-in-out infinite reverse;
}

/* Orb 3 — Center-right, violet */
.bg-mesh .orb:nth-child(3) {
    width: 350px; height: 350px;
    background: radial-gradient(circle, #8b5cf6, transparent 70%);
    top: 40%; left: 55%;
    animation: drift 22s ease-in-out infinite 5s;
}

@keyframes drift {
    0%, 100% { transform: translate(0, 0) scale(1); }
    33%      { transform: translate(30px, -40px) scale(1.05); }
    66%      { transform: translate(-20px, 30px) scale(0.95); }
}
```

> [!NOTE]
> - Each orb uses a different **duration** and **delay** so they never sync up.
> - `filter: blur(120px)` creates the soft ambient glow.
> - The `reverse` keyword on the second orb creates counter-motion.
> - Adjust orb colors to match your project's accent palette.

---

## 4. Glass Card Container

The main container that holds your UI content. Uses the glassmorphism effect.

```css
.card {
    position: relative;
    z-index: 1;
    width: 400px;
    background: var(--body-bg);
    border: 1px solid var(--body-border);
    border-radius: 24px;
    padding: 20px;
    box-shadow: var(--body-shadow);
    animation: enterCard 0.7s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes enterCard {
    from { opacity: 0; transform: translateY(30px) scale(0.97); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}
```

> [!IMPORTANT]
> Use the `cubic-bezier(0.16, 1, 0.3, 1)` easing for all entry animations — it gives a satisfying spring-like overshoot that feels premium.

---

## 5. Display / Content Panel

A recessed panel inside the card for primary content (text, data, results, etc.).

```css
.display-panel {
    background: var(--display-bg);
    border: 1px solid var(--display-border);
    border-radius: 16px;
    padding: 0;
    margin-bottom: 16px;
    position: relative;
    overflow: hidden;
}

/* Subtle accent line at the top edge */
.display-panel::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,0.25), transparent);
}
```

### Status Bar Pattern

A row of small indicators at the top of the panel.

```css
.status-bar {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 16px 4px;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1px;
}

.status-item {
    color: var(--indicator-dim);
    transition: color 0.2s, text-shadow 0.2s;
}

.status-item.active {
    color: var(--indicator-active);
    text-shadow: 0 0 8px rgba(96,165,250,0.4);
}
```

### Auto-Scaling Text

For primary output text that needs to shrink when content gets long.

```css
.primary-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 36px;
    font-weight: 600;
    color: var(--display-text);
    word-break: break-all;
    text-align: right;
    width: 100%;
    line-height: 1.2;
    letter-spacing: -0.5px;
    transition: font-size 0.2s;
    text-shadow: 0 0 20px var(--display-glow);
}

.primary-text.small   { font-size: 26px; }
.primary-text.x-small { font-size: 20px; }
.primary-text.error   { color: #f87171; }
```

---

## 6. Button System

### Base Button

All buttons share a common base. Use variant classes to differentiate by role.

```css
.btn {
    position: relative;
    height: 52px;
    border: 1px solid rgba(255,255,255,0.04);
    border-radius: var(--btn-radius);
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    transition: all 0.15s ease;
    outline: none;
    -webkit-user-select: none;
    user-select: none;
    overflow: hidden;
    gap: 1px;
}

.btn:active {
    transform: scale(0.93);
}
```

### Button Variants

Each variant uses a **tinted rgba background** with matching **text color**. The pattern is consistent: low-opacity bg → higher-opacity bg on hover → border glow on hover.

| Variant | Class | Background | Text | Use Case |
|---------|-------|-----------|------|----------|
| **Primary** | `.btn-num` | `rgba(255,255,255,0.05)` | `#e2e8f0` | Default / neutral actions |
| **Accent** | `.btn-op` | `rgba(99,102,241,0.12)` | `#a5b4fc` | Key actions, operators |
| **Secondary** | `.btn-func` | `rgba(56,189,248,0.08)` | `#7dd3fc` | Functions, secondary features |
| **Toggle** | `.btn-shift` | `rgba(251,191,36,0.15)` | `#fbbf24` | Mode toggles, shift keys |
| **Mode** | `.btn-mode` | `rgba(167,139,250,0.1)` | `#c4b5fd` | Settings, modes |
| **Warning** | `.btn-del` | `rgba(251,146,60,0.1)` | `#fdba74` | Undo, delete, backtrack |
| **Danger** | `.btn-ac` | `rgba(248,113,113,0.12)` | `#fca5a5` | Destructive, clear, reset |
| **CTA** | `.btn-eq` | Indigo gradient | `#ffffff` | Primary submit / confirm |
| **Success** | `.btn-mem` | `rgba(52,211,153,0.08)` | `#6ee7b7` | Save, bookmark, positive |

#### Example — Accent Button

```css
.btn-op {
    background: var(--op-bg);
    color: var(--op-text);
    font-size: 18px;
    font-weight: 600;
}
.btn-op:hover {
    background: var(--op-hover);
    border-color: rgba(99,102,241,0.2);
}
```

#### Example — CTA / Gradient Button

```css
.btn-eq {
    background: var(--eq-bg);
    color: var(--eq-text);
    font-size: 20px;
    font-weight: 700;
    border: none;
    box-shadow: var(--eq-shadow);
}
.btn-eq:hover {
    background: var(--eq-hover);
    box-shadow: 0 6px 25px rgba(79,70,229,0.45);
    transform: translateY(-1px);
}
.btn-eq:active {
    transform: scale(0.93) translateY(0);
}
```

#### Example — Toggle Button with Active State

```css
.btn-shift {
    background: var(--shift-bg);
    color: var(--shift-text);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.btn-shift:hover {
    background: var(--shift-active-bg);
}
.btn-shift.active {
    background: var(--shift-active-bg);
    box-shadow: 0 0 15px rgba(251,191,36,0.2), inset 0 0 15px rgba(251,191,36,0.1);
    border-color: rgba(251,191,36,0.3);
}
```

### Button Sub-Labels

Small secondary text positioned above the main label (useful for alt-functions, shortcuts, or hover hints).

```html
<button class="btn btn-func">
    <span class="shift-label">ALT</span>
    <span class="main-label">Primary</span>
</button>
```

```css
.btn .shift-label {
    font-size: 8px;
    font-weight: 600;
    color: rgba(251,191,36,0.5);
    letter-spacing: 0.3px;
    line-height: 1;
    position: absolute;
    top: 3px;
    pointer-events: none;
}

.btn .main-label {
    font-size: inherit;
    line-height: 1;
}
```

### Grid Layout

Use CSS Grid for consistent button alignment. Adjust `repeat(N, 1fr)` to match your column count.

```css
.btn-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: var(--btn-gap);
}

/* Span 2 columns */
.btn-span2 {
    grid-column: span 2;
}
```

### Section Dividers

Subtle gradient lines to visually separate button groups within the grid.

```css
.section-divider {
    grid-column: 1 / -1;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);
    margin: 2px 0;
}
```

---

## 7. Micro-Animations

### Ripple Effect (Material-style)

Creates a circular ripple originating from the click point.

```css
.btn .ripple {
    position: absolute;
    border-radius: 50%;
    background: rgba(255,255,255,0.15);
    transform: scale(0);
    animation: ripple 0.45s ease-out;
    pointer-events: none;
}

@keyframes ripple {
    to { transform: scale(3); opacity: 0; }
}
```

```javascript
function createRipple(btn, event) {
    const ripple = document.createElement('span');
    ripple.classList.add('ripple');
    const rect = btn.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    ripple.style.width = ripple.style.height = size + 'px';

    if (event && event.clientX) {
        ripple.style.left = (event.clientX - rect.left - size / 2) + 'px';
        ripple.style.top  = (event.clientY - rect.top - size / 2) + 'px';
    } else {
        // Center ripple (for keyboard triggers)
        ripple.style.left = (rect.width / 2 - size / 2) + 'px';
        ripple.style.top  = (rect.height / 2 - size / 2) + 'px';
    }

    btn.appendChild(ripple);
    ripple.addEventListener('animationend', () => ripple.remove());
}
```

### Shake Animation (Error Feedback)

Apply this class briefly when an invalid action occurs.

```css
@keyframes shake {
    0%, 100% { transform: translateX(0); }
    20%      { transform: translateX(-6px); }
    40%      { transform: translateX(6px); }
    60%      { transform: translateX(-3px); }
    80%      { transform: translateX(3px); }
}

.shake {
    animation: shake 0.35s ease;
}
```

```javascript
function shakeElement(el) {
    el.classList.add('shake');
    setTimeout(() => el.classList.remove('shake'), 350);
}
```

### Entry Animation (Fade-In-Up)

Spring-loaded entrance for the main container.

```css
@keyframes enterCard {
    from { opacity: 0; transform: translateY(30px) scale(0.97); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}

.card {
    animation: enterCard 0.7s cubic-bezier(0.16, 1, 0.3, 1);
}
```

### Delayed Fade-In

For secondary elements that should appear after the main content.

```css
@keyframes fadeIn {
    to { opacity: 1; }
}

.hint-text {
    opacity: 0;
    animation: fadeIn 0.8s ease 1.2s forwards;
}
```

### Keyboard Press Feedback

Simulate a physical button press when triggered via keyboard.

```javascript
function simulatePress(btn) {
    createRipple(btn, null);
    btn.style.transform = 'scale(0.93)';
    setTimeout(() => { btn.style.transform = ''; }, 120);
}
```

---

## 8. Responsive Breakpoints

On small screens, the card fills the viewport and button sizes reduce.

```css
@media (max-width: 440px) {
    .card {
        width: 100%;
        border-radius: 0;
        min-height: 100vh;
        padding: 12px;
        display: flex;
        flex-direction: column;
    }

    .btn-grid {
        gap: 6px;
        flex: 1;
    }

    .btn {
        height: 46px;
        border-radius: 8px;
    }

    .btn-num, .btn-op {
        font-size: 16px;
    }

    .primary-text {
        font-size: 30px;
    }
}
```

---

## 9. Quick Start Template

A minimal HTML skeleton that puts it all together.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My App</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        /* Paste :root variables, base reset, bg-mesh, card, button styles here */
    </style>
</head>
<body>
    <!-- Animated background -->
    <div class="bg-mesh">
        <div class="orb"></div>
        <div class="orb"></div>
        <div class="orb"></div>
    </div>

    <!-- Main card -->
    <div class="card">
        <!-- Display panel -->
        <div class="display-panel">
            <div class="status-bar">
                <span class="status-item active">STATUS</span>
                <span style="flex:1"></span>
                <span class="status-item">INFO</span>
            </div>
            <div style="padding: 8px 16px 16px; text-align: right;">
                <div class="primary-text">Content</div>
            </div>
        </div>

        <!-- Button grid -->
        <div class="btn-grid">
            <button class="btn btn-func">Func</button>
            <button class="btn btn-num">1</button>
            <button class="btn btn-op">+</button>
            <button class="btn btn-del">DEL</button>
            <button class="btn btn-eq">=</button>
        </div>
    </div>

    <script>
        // Attach ripple to all buttons
        document.querySelectorAll('.btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                /* createRipple(btn, e); */
            });
        });
    </script>
</body>
</html>
```

---

## 10. Design Principles Recap

| Principle | How It's Applied |
|-----------|------------------|
| **Low-opacity rgba** | Every surface uses semi-transparent colors over dark base |
| **Color-coded semantics** | Each button role has a unique hue (indigo, sky, amber, red, etc.) |
| **Hover = intensify** | Hover doubles the background opacity and adds a subtle border glow |
| **Active = compress** | `transform: scale(0.93)` on press for tactile feedback |
| **Gradient CTAs** | The primary action button uses a multi-stop gradient + box-shadow |
| **Ambient motion** | Background orbs drift slowly with staggered timing |
| **Spring easing** | `cubic-bezier(0.16, 1, 0.3, 1)` for all entrance animations |
| **Accent lines** | `::before` pseudo-elements with gradient 1px lines for panel edges |
| **Auto-scaling text** | CSS class toggles (`.small`, `.x-small`) with `transition: font-size` |
| **Section dividers** | Subtle full-width gradient lines to group related controls |
