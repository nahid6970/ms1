import re
import os

# --- Function to handle imports in the form of <!-- import path/to/file -->
def process_imports(content, base_dir='.'):
    # Match <!-- import path/to/file -->
    import_pattern = re.compile(r'<!--\s*import\s+([^\s]+)\s*-->')
    
    def replacer(match):
        # Get file path from the import statement
        file_path = os.path.join(base_dir, match.group(1))
        
        try:
            # Read the content of the imported file
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f'<!-- File not found: {file_path} -->'

    # Replace import tags with the actual file contents
    return import_pattern.sub(replacer, content)

# --- Function to convert custom [[Caption]-[Link]-[Image]] into proper HTML
def convert_custom_img_links(text):
    pattern = re.compile(
        r'\[\[([^\]]+)\]-\[(https?://[^\]]+)\]-\[(\S+)(?:\s+width=(\d+),?\s*height=(\d+))?\]\]'
    )
    
    def replacer(match):
        caption = match.group(1)
        href = match.group(2)
        img_src = match.group(3)
        width = match.group(4)
        height = match.group(5)

        img_tag = f'<img src="{img_src}" alt="{caption}"'
        if width:
            img_tag += f' width="{width}"'
        if height:
            img_tag += f' height="{height}"'
        img_tag += '>'

        return f'<a href="{href}" title="{caption}">{img_tag}</a>'

    return pattern.sub(replacer, text)

# --- Main function to process the file
def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    base_dir = os.path.dirname(file_path)

    # First process imports (if any)
    content = process_imports(content, base_dir)
    
    # Then convert custom img links to HTML
    content = convert_custom_img_links(content)

    return content

# --- Example usage
if __name__ == "__main__":
    input_file = "C:\\ms2\\myhome_input.html"  # Or any Org or HTML file
    output_file = "C:\\ms2\\myhome.html"



    result = process_file(input_file)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result)

    print(f"Saved processed output to {output_file}")
