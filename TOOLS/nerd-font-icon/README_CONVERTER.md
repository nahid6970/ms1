# 🎨 NerdFont Icon Converter

Convert Nerd Font icons to PNG/ICO/BMP/JPG with multiple dimensions in one click!

## 🚀 Features

- **Batch conversion** to multiple sizes (16x16, 32x32, 64x64, etc.)
- **Simple output**: All images saved directly in the `img/` directory
- **Multiple formats**: PNG, ICO, BMP, JPG
- **Customizable colors**: Icon color and background (including transparent)
- **Config persistence**: Save your settings for next time
- **Cyberpunk UI**: Styled with the theme from THEME_GUIDE.md

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 🎯 Usage

1. **Run the script:**
   ```bash
   python nerdfont_icon_converter.py
   ```

2. **Download a Nerd Font** (if you don't have one):
   - Visit: https://www.nerdfonts.com/font-downloads
   - Download any font (e.g., "FiraCode Nerd Font")
   - Extract the .ttf file

3. **In the GUI:**
   - Browse and select your Nerd Font .ttf file
   - Enter an icon character (copy from https://www.nerdfonts.com/cheat-sheet)
   - Or enter Unicode like `U+F015`
   - Modify dimensions list (one per line)
   - Click **⚡ CONVERT ICON ⚡**

4. **Output structure:**
   ```
   img/
   ├── icon_16x16.png
   ├── icon_32x32.png
   ├── icon_64x64.png
   ├── icon_128x128.png
   └── icon_256x256.png
   ```

## ⚙️ Configuration

Modify dimensions in the GUI text area:
```
16
24
32
40
48
64
128
256
```

Settings are auto-saved to `nerdfont_converter_config.json`

## 🎨 Customization

- **Icon Color**: Hex color (e.g., `#FFFFFF`) or `transparent`
- **Background**: Hex color (e.g., `#000000`) or `transparent`
- **Output Format**: PNG (recommended), ICO, BMP, JPG

## 📝 Example

Input: `` (home icon from Nerd Font)
Output: All sizes directly in `img/` folder
