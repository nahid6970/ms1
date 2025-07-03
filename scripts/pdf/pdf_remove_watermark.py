import PyPDF2
import fitz  # PyMuPDF
import os
from PIL import Image
import io

def remove_watermark_pypdf2(input_path, output_path, watermark_text=None):
    """
    Remove text-based watermarks using PyPDF2
    """
    try:
        with open(input_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            writer = PyPDF2.PdfWriter()
            
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                
                # Try to remove watermark text if specified
                if watermark_text:
                    # Get page content
                    content = page.extract_text()
                    if watermark_text.lower() in content.lower():
                        print(f"Found watermark text on page {page_num + 1}")
                
                # Remove annotations that might contain watermarks
                if '/Annots' in page:
                    del page['/Annots']
                
                writer.add_page(page)
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
        
        print(f"Successfully processed PDF: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error with PyPDF2 method: {e}")
        return False

def remove_watermark_pymupdf(input_path, output_path, watermark_text=None):
    """
    Remove watermarks using PyMuPDF (more advanced)
    """
    try:
        doc = fitz.open(input_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Get all text instances
            text_instances = page.get_text("dict")
            
            # Remove watermark text if specified
            if watermark_text:
                blocks_to_remove = []
                for block in text_instances["blocks"]:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                if watermark_text.lower() in span["text"].lower():
                                    blocks_to_remove.append(block)
                                    break
                
                # Remove identified watermark blocks
                for block in blocks_to_remove:
                    bbox = fitz.Rect(block["bbox"])
                    page.add_redact_annot(bbox, fill=(1, 1, 1))  # White fill
                
                page.apply_redactions()
            
            # Remove annotations
            annots = page.annots()
            for annot in annots:
                page.delete_annot(annot)
            
            # Remove stamps and forms
            page.clean_contents()
        
        doc.save(output_path)
        doc.close()
        
        print(f"Successfully processed PDF with PyMuPDF: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error with PyMuPDF method: {e}")
        return False

def remove_image_watermarks(input_path, output_path):
    """
    Advanced method to remove image-based watermarks
    """
    try:
        doc = fitz.open(input_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Get all images on the page
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                # Get image data
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Convert to PIL Image
                image = Image.open(io.BytesIO(image_bytes))
                
                # Basic watermark detection (you may need to adjust this)
                # This is a simple approach - you might need more sophisticated detection
                width, height = image.size
                
                # Check if image is likely a watermark (small, transparent, etc.)
                if width < 200 and height < 200:
                    # Get image rectangle
                    img_rect = page.get_image_rects(img)[0]
                    
                    # Remove the image by covering it with white rectangle
                    page.add_redact_annot(img_rect, fill=(1, 1, 1))
                    
            page.apply_redactions()
        
        doc.save(output_path)
        doc.close()
        
        print(f"Successfully removed image watermarks: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error removing image watermarks: {e}")
        return False

def main():
    print("PDF Watermark Remover")
    print("=" * 30)
    
    # Get input file from user
    while True:
        input_file = input("\nEnter the path to your PDF file: ").strip()
        
        # Remove quotes if user added them
        input_file = input_file.strip('"').strip("'")
        
        if os.path.exists(input_file):
            if input_file.lower().endswith('.pdf'):
                break
            else:
                print("Error: File must be a PDF file (.pdf extension)")
        else:
            print("Error: File not found. Please check the path and try again.")
    
    # Generate output filename automatically
    name, ext = os.path.splitext(input_file)
    output_file = f"{name}_watermark_removed{ext}"
    
    # Ask for watermark text (optional)
    watermark_text = input("\nEnter watermark text to remove (or press Enter to skip): ").strip()
    if not watermark_text:
        watermark_text = None
    
    # Ask for method
    print("\nChoose removal method:")
    print("1. Try all methods (recommended)")
    print("2. PyPDF2 only")
    print("3. PyMuPDF only")
    print("4. Image watermarks only")
    
    while True:
        choice = input("Enter your choice (1-4): ").strip()
        if choice == '1':
            method = 'all'
            break
        elif choice == '2':
            method = 'pypdf2'
            break
        elif choice == '3':
            method = 'pymupdf'
            break
        elif choice == '4':
            method = 'images'
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")
    
    print(f"\nProcessing: {input_file}")
    print(f"Output will be saved as: {output_file}")
    print("-" * 50)
    
    success = False
    
    if method in ['pypdf2', 'all']:
        print("Trying PyPDF2 method...")
        success = remove_watermark_pypdf2(input_file, output_file, watermark_text) or success
    
    if method in ['pymupdf', 'all']:
        print("Trying PyMuPDF method...")
        temp_output = output_file.replace('.pdf', '_temp.pdf')
        success = remove_watermark_pymupdf(input_file, temp_output, watermark_text) or success
        if success and os.path.exists(temp_output):
            os.replace(temp_output, output_file)
    
    if method in ['images', 'all']:
        print("Trying image watermark removal...")
        success = remove_image_watermarks(input_file, output_file) or success
    
    print("-" * 50)
    if success:
        print("✓ Watermark removal completed!")
        print(f"✓ Output saved to: {output_file}")
    else:
        print("✗ Watermark removal failed.")
        print("The watermark might be embedded in a way that requires manual editing.")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()