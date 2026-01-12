from PIL import Image, ImageDraw

def create_icon(size, filename):
    img = Image.new('RGB', (size, size), color = (20, 20, 20))
    d = ImageDraw.Draw(img)
    # Draw a red circle
    d.ellipse([size*0.2, size*0.2, size*0.8, size*0.8], fill=(255, 50, 50))
    img.save(filename)

create_icon(16, 'icons/icon16.png')
create_icon(48, 'icons/icon48.png')
create_icon(128, 'icons/icon128.png')
