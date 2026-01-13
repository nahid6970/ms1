# Coding Guidelines

## File Paths & Portability
- Use relative paths from the script's location so it works when launched from any directory
- Get script directory dynamically (e.g., `os.path.dirname(os.path.abspath(__file__))` in Python)
- Never hardcode absolute paths

## Data Storage
- Use external files (JSON, YAML, TOML) for configurable data instead of hardcoding
- Ask user on first run if data/config doesn't exist, then save for future use
- Keep config files in the same directory as the script or a dedicated `config/` subfolder

## User Experience
- Provide clear error messages when files are missing or invalid
- Include sensible defaults when config is absent
- Add `--help` or usage info for CLI scripts

## Code Structure
- Keep functions small and single-purpose
- Add comments for non-obvious logic
- Use meaningful variable/function names

## Error Handling
- Wrap file operations in try/except blocks
- Validate user input before processing
- Fail gracefully with helpful messages

## Dependencies
- List required packages in a `requirements.txt` if using external libraries
- Prefer standard library when possible to reduce dependencies

## UI/Theming (when applicable)

### Default: Cyberpunk
- Neon colors: cyan `#00FFFF`, magenta `#FF00FF`, electric blue `#0080FF`
- Dark backgrounds: `#0a0a0f`, `#1a1a2e`
- Glow effects, sharp edges, tech fonts

### Alternative Styles (pick one if cyberpunk doesn't fit)

**Nord / Arctic**
- Cool blues and grays: `#2E3440`, `#3B4252`, `#88C0D0`, `#81A1C1`
- Clean, minimal, easy on the eyes

**Dracula**
- Purple-heavy dark theme: `#282a36`, `#bd93f9`, `#ff79c6`, `#50fa7b`
- Popular dev aesthetic, good contrast

**Gruvbox**
- Warm retro feel: `#282828`, `#ebdbb2`, `#fb4934`, `#b8bb26`, `#fabd2f`
- Earthy tones, vintage terminal vibe

**Synthwave / Retrowave**
- 80s neon: `#241b2f`, `#ff7edb`, `#72f1b8`, `#fede5d`
- Similar to cyberpunk but more purple/pink sunset vibes

**Monokai**
- Classic dark: `#272822`, `#f92672`, `#a6e22e`, `#fd971f`
- Timeless, high contrast

### General Theming Rules
- For CLI: use `colorama` or `rich` library for colored output
- For GUI: dark theme with accent colors, minimal chrome
- Keep it readable - contrast matters over style
