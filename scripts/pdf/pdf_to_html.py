import fitz  # PyMuPDF
import os
from tkinter import Tk, filedialog
from pathlib import Path

def pdf_to_html_converter(input_pdf_path):
    """
    Converts a PDF file to an HTML file, preserving text and formatting.
    The HTML output will contain the content of each PDF page.
    """
    input_pdf_path = Path(input_pdf_path)

    if not input_pdf_path.is_file():
        print(f"Error: PDF file '{input_pdf_path}' does not exist.")
        return

    output_html_path = input_pdf_path.parent / f"{input_pdf_path.stem}.html"

    try:
        doc = fitz.open(input_pdf_path)
        full_html_content = ""

        # Build HTML content using string concatenation to avoid triple-quote issues
        full_html_content += "<!DOCTYPE html>\n"
        full_html_content += "<html lang=\"en\">\n"
        full_html_content += "<head>\n"
        full_html_content += "    <meta charset=\"UTF-8\">\n"
        full_html_content += "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
        full_html_content += f"    <title>{input_pdf_path.stem} - Converted from PDF</title>\n"
        full_html_content += "    <style>\n"
        full_html_content += "        body {{ font-family: sans-serif; margin: 20px; }}\n"
        full_html_content += "        .page {{\n"
        full_html_content += "            margin-bottom: 20px;\n"
        full_html_content += "            border: 1px solid #ccc;\n"
        full_html_content += "            padding: 15px;\n"
        full_html_content += "            page-break-after: always; /* For printing/PDF export of the HTML */\n"
        full_html_content += "        }}\n"
        full_html_content += "        .page:last-child {{ page-break-after: avoid; }}\n"
        full_html_content += "        h1 {{ color: #333; }}\n"
        full_html_content += "        /* Add more styles here if fitz.utils.text_to_html doesn't provide enough */\n"
        full_html_content += "    </style>\n"
        full_html_content += "</head>\n"
        full_html_content += "<body>\n"
        full_html_content += f"    <h1>Converted Document: {input_pdf_path.name}</h1>\n"
        full_html_content += "    <p><i>Note: This HTML aims to preserve text and basic formatting. Complex layouts may not be perfectly replicated.</i></p>\n"
        full_html_content += "    <hr>\n"

        for page_num in range(len(doc)):
            page = doc[page_num]
            # get_text("html") tries to preserve formatting and layout
            page_html = page.get_text("html")
            
            # Wrap each page's content in a div for better separation
            full_html_content += f'<div class="page"><h2>Page {page_num + 1}</h2>\n'
            full_html_content += page_html
            full_html_content += '\n</div>\n'
            
            print(f"Processed page {page_num + 1}/{len(doc)}")

        full_html_content += "\n</body>\n"
        full_html_content += "</html>\n"
        
        with open(output_html_path, "w", encoding="utf-8") as html_file:
            html_file.write(full_html_content)

        doc.close()
        print(f"\nSuccessfully converted '{input_pdf_path.name}' to HTML.")
        print(f"Output saved to: {output_html_path}")

    except Exception as e:
        print(f"An error occurred during conversion: {e}")

if __name__ == "__main__":
    Tk().withdraw()  # Hide the root window
    pdf_file_path = filedialog.askopenfilename(
        title="Select PDF File to Convert to HTML",
        filetypes=[("PDF Files", "*.pdf")]
    )

    if pdf_file_path:
        pdf_to_html_converter(pdf_file_path)
    else:
        print("No PDF file selected. Exiting.")
