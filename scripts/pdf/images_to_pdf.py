import os
from PIL import Image
from pathlib import Path

def images_to_pdf(directory):
    """Convert all images in a directory to a single PDF file."""
    directory = Path(directory)
    
    if not directory.exists():
        print(f"Error: Directory '{directory}' does not exist.")
        return
    
    # Supported image formats
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}
    
    # Get all image files and sort them
    image_files = []
    for file in directory.iterdir():
        if file.suffix.lower() in image_extensions:
            image_files.append(file)
    
    if not image_files:
        print(f"No images found in '{directory}'")
        return
    
    # Sort files naturally (1.jpg, 2.jpg, ... 10.jpg, 11.jpg)
    image_files.sort(key=lambda x: int(''.join(filter(str.isdigit, x.stem))) if any(c.isdigit() for c in x.stem) else x.stem)
    
    print(f"Found {len(image_files)} images")
    
    # Convert images to RGB mode and collect them
    images = []
    for img_path in image_files:
        try:
            img = Image.open(img_path)
            # Convert to RGB (PDF requires RGB mode)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            images.append(img)
            print(f"Added: {img_path.name}")
        except Exception as e:
            print(f"Error processing {img_path.name}: {e}")
    
    if not images:
        print("No valid images to convert")
        return
    
    # Save as PDF
    output_path = directory / "combined_images.pdf"
    images[0].save(output_path, save_all=True, append_images=images[1:])
    
    print(f"\nPDF created successfully: {output_path}")
    print(f"Total pages: {len(images)}")

if __name__ == "__main__":
    directory = input("Enter the directory path containing images: ").strip()
    images_to_pdf(directory)
