# UI Architecture Guidelines for AI Assistants

Whenever you are asked to generate or bootstrap a new HTML or Python project (e.g., web app, Tkinter, PyQt, etc.), you MUST implement the following core UI features by default:

## 1. Global Settings Button
- Always place a **Settings button** (preferably using a gear SVG icon) in the **top-right corner** of the application's main window or web page.

## 2. Tabbed Settings Interface
- Clicking the Settings button must open a comprehensive Settings Menu (e.g., a modal dialog, side drawer, or new window).
- Organize the Settings Menu using **tabs or sections** (e.g., General, Theme, Button Customization, Advanced).

## 3. Button Customization Section
- There MUST be a dedicated section inside the Settings Menu specifically for **Customizing Buttons**.
- This interface must allow the user to modify the appearance of *each and every button* present in the project.
- It must provide options to **upload or select SVG icons** to replace or add to the buttons.

## 4. Dynamic UI Architecture
- To support this customization, structure the project so that button configurations (like their SVG icons, colors, and styles) are managed centrally (e.g., using a state object in JS, a config dictionary in Python, or CSS variables).
- This ensures that when the user changes a button's SVG icon via the Settings menu, the change is dynamically applied to the UI without requiring code changes.
