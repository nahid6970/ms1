# New Project Planning: Markdown-First Single-Column Sheet System

## 1. Vision & Architecture
This project involves a complete overhaul of the `5018_cell` application, transitioning from a multi-column spreadsheet to a vertically-optimized, Markdown-native content curator.

### Core Architectural Shift:
- **Vertical Orientation**: Each sheet contains exactly **one column** and multiple rows (blocks). This removes the complexity of horizontal scrolling and refocuses on vertical content flow.
- **Unified Markdown Interface**: Removal of the "Raw Mode" toggle. The application will operate exclusively in a **Live Preview / Hybrid Mode**.
    - **Editing**: Users edit raw Markdown syntax directly. Highlighting and basic formatting (bold, color) are applied to the syntax tokens *while* editing.
    - **Viewing**: When not focused, the content is rendered into its final polished form (Large headers, math symbols, etc.).
- **Persistence Layer**: Data remains synchronized with `data.json` via the Flask backend, but the JSON schema will be flattened to prioritize a continuous row-based list for each sheet.

---

## 2. Comprehensive Feature Index (To be Ported)

### A. The "Omni-Markdown" Parsing Engine & Custom Color Core
The new system will prioritize a highly flexible, user-extensible coloring system.

1.  **Primary Coloring: The Custom Syntax Engine**:
    *   **Core Logic**: Instead of hardcoded regex for every color, the application will rely on a dynamic **Custom Syntax Registry** (seeded by `custom_syntaxes.json`).
    *   **User-Defined Markers**: Users can define any marker (e.g., `++`, `%%`, `¿¿`) and pair them with `bgColor`, `fgColor`, `isBold`, etc.
    *   **Flexible Adaptation**: This system is the "source of truth" for coloring. If a user wants a new highlight color, they simply add a marker definition rather than modifying the parser code.

2.  **Highlight & Highlight Presets (The "Standard Library")**:
    *   **Core Presets**: Built-in support for standard markers (e.g., `==`, `!!`, `??`).
    *   **Full Customization**: These presets can be extended or modified within the Custom Syntax Registry to fit any design system.
    *   **Marker-First Philosophy**: All visual emphasis is achieved via short, memorable symbols, keeping the raw markdown readable and easy to type.

3.  **Text Formatting & Scripts**:
    *   Emphasis: Bold (`**`), Italic (`@@`), Underline (`__`), Strikethrough (`~~`).
    *   Sizing: Multi-level Headings (`##`), Variable sized markers (`#2#Text#/#`), and Small text (`..text..`).
    *   Scripts: Superscript (`^`) and Subscript (`~`).
3.  **Layout & Structure**:
    *   Lists: Multi-level indented bullets (`-`, `--`, `---`) and auto-numbered lists.
    *   Separators: Styled horizontal lines with color mapping (`R-----G`).
    *   Tables: Support for Pipe and Comma-delimited tables embedded *within* the single-column rows.
    *   Containers: Border boxes (`#B#Box Content#/#`) for emphasizing blocks of text.
4.  **Special Logic**:
    *   **KaTeX Math**: Full LaTeX support (`\( \)` ) with specialized "Smart Fraction" conversion for rapid entry.
    *   **Word Connectors**: Dynamic SVG/Canvas lines connecting terms marked with `[1]term`.
    *   **Interactive Content**: 
        *   Collapsible blocks `{{ hidden }}`.
        *   Correct Answer blocks `[[ answer ]]`.
        *   Checkbox states (Completion tracking).
    *   **Timeline/Flow**: Automated vertical flowcharts using `Timeline*` syntax.

### B. UI/UX & Navigation Systems
1.  **Sidebar (The Tree)**:
    *   Hierarchical organization: Categories > Sheets > Sub-sheets.
    *   Dynamic management: Rename, Move, and Delete via right-click or icons.
2.  **Productivity Shortcuts (F-Key System)**:
    *   **F1 (Vault)**: Global quick-switcher, command palette, and sheet creator.
    *   **F2 (History)**: Vertical list of recently edited or viewed sheets.
    *   **F3 (Quick Format - "Selection Power-Tool")**: 
        *   **Standard Formatting**: Buttons for Bold, Italic, Underline, Strikethrough, etc.
        *   **Dynamic Markers**: Instant access to `##` Headings, `#2#` Big Text, `..` Small text, and `_R_` Colored underlines.
        *   **Custom Syntax Shelf**: A dynamic section that automatically populates buttons for every marker defined in `custom_syntaxes.json` (e.g., `++`, `%%`, `¿¿`).
        *   **Math & Advanced Tools**: Buttons for `\(\sqrt{}\)`, smart fractions, Link creation, and Google Search.
        *   **Text Manipulation**: One-click Case conversion (UPPER, lower, Proper), List sorting, and Table alignment.
        *   **Selection Stats**: Live character, word, and line counting for the selected area.
        *   **Multi-Select (F3 + Click)**: Ability to "queue" multiple formats to apply them all at once to a selection.
    *   **F4 (Layout)**: Toggle UI chrome (Header/Sidebar) for "Zen Mode".
    *   **F8 (Smart Pick)**: Extract word from under mouse/cursor and auto-add to search/clipboard.
    *   **F9 (Swap)**: Instance-swap two terms separated by symbols in a selection.
3.  **Advanced Editing**:
    *   **Multi-Cursor**: Simulation of VS Code-style `Ctrl+D` and `Ctrl+Alt+Up/Down` for bulk editing within a cell.
    *   **Line Manipulation**: `Alt+Up/Down` to move content blocks vertically within a sheet.
    *   **Case Ops**: Instant `Uppercase`/`Lowercase` transformation.
    *   **Tab Handling**: Intelligent indentation within textareas.

### C. Data & Export Systems
*   **Real-Time Sync**: Auto-save to `data.json` on blur or save command (`Ctrl+S`).
*   **Dual-Nature Backend (Live & Static)**: 
    *   **Live App**: Full Flask functionality for editing and database sync.
    *   **Auto-Static Export**: Built-in Flask endpoint to generate a single-file, standalone HTML export (integrated `export_static.py` logic).
    *   **On-Demand Snapshots**: UI button to immediately download the current sheet/vault as a portable HTML file with all styles and assets embedded.
*   **PDF Generation**: Layout-aware PDF export for printing/sharing.
*   **Priority System**: Row-level Rank badges and Background Color history.

---

## 3. Rebuild Strategy (The "New Rule of 6")
To ensure consistency in the new architecture, every content-feature must be unified across:
1.  **Unified Parser**: A single, parameterized JS function handling both "Clean" view and "Hybrid" edit mode.
2.  **Detection**: Robust `checkHasMarkdown` logic for autosize and overlay triggers.
3.  **Search Transparency**: `stripMarkdown` ensures that rich formatting doesn't break multi-term searching.
4.  **Static Mirror**: Equivalent Python-based parsing in `export_static.py` for identical offline views.
5.  **Focus Logic**: Seamless transition between transparent editing and polished viewing with **zero cursor jumping**.
6.  **Style Tokens**: Centralized CSS variables for themes (Light/Dark/Cyberpunk) and custom syntaxes.

---

## 4. Immediate Planning Objectives
*   **Data Migration**: Convert existing multi-column `data.json` to a single-column array format.
*   **Overlay Elimination**: Refactor the preview logic to use a background-content strategy where the styled output sits directly behind the transparent input.
*   **Refresh Persistence**: Ensure the Flask backend captures "Last Sheet" and "Last Cursor" states for a truly seamless reload experience.
