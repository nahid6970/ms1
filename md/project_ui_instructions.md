# UI Architecture Guidelines for AI Assistants

Whenever you are asked to generate or bootstrap a new HTML or Python project (e.g., web app, Tkinter, PyQt, etc.), you MUST implement the following core UI features by default:

## 1. Global Settings Button
- Always place a **Settings button** (preferably using a gear SVG icon) in the **top-right corner** of the application's main window or web page.

## 2. Tabbed Settings Interface (Modern Aesthetics)
- Clicking the Settings button must open a comprehensive Settings Menu (e.g., a modal dialog, side drawer, or new window).
- Organize the Settings Menu using **tabs or sections** (e.g., General, Theme, Button Customization, Advanced) for easy navigation.
- **Theme Controls:** In the "Theme" tab, include **sliders** so the user can finely tune global visual properties (e.g., adjust glassmorphism blur intensity, transparency/opacity levels, or primary theme color hue).
- **Premium Design Requirements:** The Settings UI must look modern and premium. Implement visual enhancements such as:
  - **Glassmorphism** (translucent backgrounds with background-blur).
  - **Sleek dark mode / light mode themes** with harmonious color palettes.
  - **Modern typography** (e.g., Inter, Roboto, or system UI fonts).
  - **Micro-animations and smooth transitions** on tabs, inputs, and hover states to make the interface feel responsive and alive.

## 3. Button Customization Section
- There MUST be a dedicated section inside the Settings Menu specifically for **Customizing Buttons**.
- This interface must allow the user to modify the appearance of *each and every button* present in the project. It should include the following controls for each button:
  - **Text & Naming**: Ability to change the button's label text.
  - **Colors**: Foreground (text/icon color) and Background color pickers.
  - **Typography**: Controls for Font Size, Bold, and Italic toggles.
  - **Shape, Padding & Borders**: Controls for Border Radius (adjusting squareness vs. roundness) and **Padding** (adjusting inner spacing).
  - **Icon (SVG)**: A text area to **paste raw SVG code** directly to replace or add icons (do not ask for file uploads).
- **IMPORTANT**: Do NOT add or generate any SVG icons for the buttons initially (except the gear icon for settings). Leave the buttons text-only or use simple defaults, as the user will paste their own SVGs later.
- **Theming & Layout**: Ensure the Settings UI itself and the buttons it controls maintain a premium, well-structured layout with beautiful theming and coloring as described in Section 2.

## 4. Dynamic UI Architecture
- To support this customization, structure the project so that button configurations (including their raw SVG markup, colors, and styles) are managed centrally (e.g., using a state object in JS, a config dictionary in Python, or dynamic DOM insertion).
- This ensures that when the user pastes new SVG code via the Settings menu, the raw SVG is injected and the change is dynamically applied to the UI without requiring code changes.

## 5. Professional Toast Notifications
- Integrate a sleek, professional notification system (like a toast or popup notification) to display status updates, successes, or errors to the user.
- These notifications should pop up gracefully (e.g., in the bottom-right or top-center of the screen) and disappear automatically after a few seconds.
- Provide a dismiss (X) button on the notification for immediate closure.
