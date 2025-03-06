from PyPDF2 import PdfReader, PdfWriter, PdfMerger
import os
from tkinter import Tk, filedialog

def parse_page_input(page_input):
    pages = set()
    parts = page_input.split(',')
    for part in parts:
        if '-' in part:
            start, end = map(int, part.split('-'))
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))
    return sorted(pages)

def get_unique_filename(directory, base_name, extension):
    counter = 1
    output_file = os.path.join(directory, f"{base_name}{extension}")
    while os.path.exists(output_file):
        output_file = os.path.join(directory, f"{base_name}_{counter}{extension}")
        counter += 1
    return output_file

def extract_pages(input_pdf, page_input):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    total_pages = len(reader.pages)
    pages = parse_page_input(page_input)
    
    for page_num in pages:
        if 1 <= page_num <= total_pages:
            writer.add_page(reader.pages[page_num - 1])
        else:
            print(f"Warning: Page {page_num} is out of range and will be skipped.")
    
    output_dir = os.path.dirname(input_pdf)
    page_str = page_input.replace(',', '_').replace('-', 'to')
    output_pdf = get_unique_filename(output_dir, f"extracted_{page_str}", ".pdf")
    
    with open(output_pdf, "wb") as out_file:
        writer.write(out_file)
    
    print(f"Extracted pages saved to {output_pdf}")

def merge_pdfs():
    Tk().withdraw()
    pdf_files = filedialog.askopenfilenames(title="Select PDF Files to Merge", filetypes=[("PDF Files", "*.pdf")])
    
    if not pdf_files:
        print("No files selected. Exiting.")
        return
    
    merger = PdfMerger()
    for pdf in pdf_files:
        merger.append(pdf)
    
    output_dir = os.path.dirname(pdf_files[0])
    output_pdf = get_unique_filename(output_dir, "merged_output", ".pdf")
    
    with open(output_pdf, "wb") as out_file:
        merger.write(out_file)
    merger.close()
    0
    print(f"Merged PDF saved to {output_pdf}")

if __name__ == "__main__":
    Tk().withdraw()  # Hide the root window
    while True:
        choice = input("Choose an option: (1) Extract Pages, (2) Merge PDFs, (q) Quit: ")
        if choice == '1':
            input_pdf = filedialog.askopenfilename(title="Select PDF File", filetypes=[("PDF Files", "*.pdf")])
            if not input_pdf:
                print("No file selected. Try again.")
                continue
            while True:
                page_input = input("Enter page numbers to extract (e.g., 5,10,11 or 5-10, or 'b' to go back): ")
                if page_input.lower() == 'b':
                    break
                extract_pages(input_pdf, page_input)
        elif choice == '2':
            merge_pdfs()
        elif choice.lower() == 'q':
            print("Exiting program.")
            break
        else:
            print("Invalid option. Please enter 1, 2, or q.")
