import PyPDF2
import os
from pathlib import Path


def split_pdf(input_pdf, pages_per_split):
    """
    Split a PDF into multiple PDFs with specified number of pages each.
    
    Args:
        input_pdf: Path to the input PDF file
        pages_per_split: Number of pages per split PDF
    """
    try:
        # Open the PDF file
        with open(input_pdf, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            
            print(f"Total pages in PDF: {total_pages}")
            
            # Get the base name without extension
            base_name = Path(input_pdf).stem
            output_dir = Path(input_pdf).parent / f"{base_name}_split"
            
            # Create output directory if it doesn't exist
            output_dir.mkdir(exist_ok=True)
            
            # Calculate number of splits needed
            num_splits = (total_pages + pages_per_split - 1) // pages_per_split
            
            print(f"Creating {num_splits} PDF files with {pages_per_split} pages each...")
            
            # Split the PDF
            for split_num in range(num_splits):
                pdf_writer = PyPDF2.PdfWriter()
                
                start_page = split_num * pages_per_split
                end_page = min(start_page + pages_per_split, total_pages)
                
                # Add pages to the writer
                for page_num in range(start_page, end_page):
                    pdf_writer.add_page(pdf_reader.pages[page_num])
                
                # Write to output file
                output_filename = output_dir / f"{base_name}_part_{split_num + 1}.pdf"
                with open(output_filename, 'wb') as output_file:
                    pdf_writer.write(output_file)
                
                print(f"Created: {output_filename} (pages {start_page + 1}-{end_page})")
            
            print(f"\nAll splits saved to: {output_dir}")
            
    except FileNotFoundError:
        print(f"Error: File '{input_pdf}' not found.")
    except Exception as e:
        print(f"Error: {e}")


def main():
    print("=== PDF Splitter ===\n")
    
    # Get input PDF path
    input_pdf = input("Enter the path to the PDF file: ").strip().strip('"')
    
    if not os.path.exists(input_pdf):
        print("Error: File does not exist.")
        return
    
    # Get pages per split
    try:
        pages_per_split = int(input("How many pages per split? ").strip())
        if pages_per_split <= 0:
            print("Error: Number of pages must be positive.")
            return
    except ValueError:
        print("Error: Invalid number.")
        return
    
    split_pdf(input_pdf, pages_per_split)


if __name__ == "__main__":
    main()
