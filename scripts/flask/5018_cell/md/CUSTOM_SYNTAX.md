# Custom Color Syntax

Users can define their own custom highlighting rules through the Settings menu. This allows for personalized styling of text using unique markers.

## Usage
**Syntax:** `{marker}text{marker}`
**Example:** If marker is `++`, syntax is `++text++`.

## Settings Interface
The Custom Syntax settings have been completely redesigned for better usability:

### Management Table
- **Marker**: The characters used to wrap your text (max 4 chars).
- **Colors**: Set distinct Background (BG) and Foreground (FG) colors.
- **Format**: Toggle **Bold**, *Italic*, or <u>Underline</u> styles.
- **Preview**: See exactly how your syntax will look in real-time.

### Color Picker
The integrated color picker features a split-pane design:
1.  **Preset Grid**: A quick-select grid of standard harmonious colors on the left.
2.  **Advanced Controls**: A right-side panel containing:
    - **🎲 Random**: Instantly generates a harmonious pair of random colors.
    - **Custom Hex**: Input any hex code (e.g., `#FF0055`) for precise styling.

## Storage
Custom syntaxes are saved to the server (`/api/custom-syntaxes`) and persist across sessions.
