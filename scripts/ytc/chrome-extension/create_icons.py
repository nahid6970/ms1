#!/usr/bin/env python3
"""
Create simple placeholder icons for the Chrome extension
Requires PIL/Pillow: pip install pillow
"""

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Please install Pillow: pip install pillow")
    exit(1)

import os

# Create icons directory
os.makedirs('icons', exist_ok=True)

# Colors from the cyberpunk theme
BG_COLOR = (5, 10, 14)  # #050a0e
ACCENT_GREEN = (0, 255, 159)  # #00ff9f
ACCENT_CYAN = (0, 240, 255)  # #00f0ff

def create_icon(size):
    """Create an icon with YTC text"""
    img = Image.new('RGB', (size, size), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Draw border
    border_width = max(2, size // 32)
    draw.rectangle(
        [border_width, border_width, size - border_width, size - border_width],
        outline=ACCENT_GREEN,
        width=border_width
    )
    
    # Draw text
    try:
        # Try to use a monospace font
        font_size = size // 3
        font = ImageFont.truetype("consola.ttf", font_size)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    text = "YTC"
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center text
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - bbox[1]
    
    # Draw text with glow effect
    for offset in range(3, 0, -1):
        alpha = 50 * (4 - offset)
        glow_color = tuple(int(c * alpha / 255) for c in ACCENT_CYAN)
        for dx in [-offset, 0, offset]:
            for dy in [-offset, 0, offset]:
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=glow_color)
    
    # Draw main text
    draw.text((x, y), text, font=font, fill=ACCENT_CYAN)
    
    return img

# Create icons in different sizes
sizes = [16, 48, 128]
for size in sizes:
    icon = create_icon(size)
    icon.save(f'icons/icon{size}.png')
    print(f"✓ Created icon{size}.png")

print("\nIcons created successfully!")
