#!/usr/bin/env python3
"""
Create simple SVG icons and convert to PNG
"""

import os

# Create icons directory
os.makedirs('icons', exist_ok=True)

# Create a simple SVG icon
svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="128" height="128" xmlns="http://www.w3.org/2000/svg">
  <rect width="128" height="128" fill="#050a0e"/>
  <rect x="8" y="8" width="112" height="112" fill="none" stroke="#00ff9f" stroke-width="4"/>
  <text x="64" y="80" font-family="monospace" font-size="48" fill="#00f0ff" text-anchor="middle" font-weight="bold">YTC</text>
</svg>'''

# Save SVG
with open('icons/icon.svg', 'w') as f:
    f.write(svg_content)

print("✓ Created icon.svg")

# Try to convert to PNG using PIL
try:
    from PIL import Image
    import cairosvg
    
    for size in [16, 48, 128]:
        png_data = cairosvg.svg2png(bytestring=svg_content.encode(), output_width=size, output_height=size)
        with open(f'icons/icon{size}.png', 'wb') as f:
            f.write(png_data)
        print(f"✓ Created icon{size}.png")
except ImportError:
    print("\nNote: Install cairosvg and pillow to generate PNG icons:")
    print("  pip install pillow cairosvg")
    print("\nFor now, you can:")
    print("  1. Open icons/icon.svg in a browser")
    print("  2. Take screenshots at different sizes")
    print("  3. Save as icon16.png, icon48.png, icon128.png")
    print("\nOr use any 128x128 PNG image as icons.")
