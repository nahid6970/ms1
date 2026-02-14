#!/usr/bin/env python3
"""Create simple icons for the extension"""

from PIL import Image, ImageDraw, ImageFont

def create_icon(size):
    img = Image.new('RGB', (size, size), color='#1a1a1a')
    draw = ImageDraw.Draw(img)
    
    # Draw border
    draw.rectangle([2, 2, size-3, size-3], outline='#00ff00', width=2)
    
    # Draw play symbol
    triangle = [
        (size//3, size//4),
        (size//3, 3*size//4),
        (3*size//4, size//2)
    ]
    draw.polygon(triangle, fill='#00ff00')
    
    img.save(f'icons/icon{size}.png')
    print(f"Created icon{size}.png")

if __name__ == '__main__':
    for size in [16, 48, 128]:
        create_icon(size)
    print("\nIcons created successfully!")
