#!/usr/bin/env python3
"""
SVG to Href Data URI Converter - GUI Version
Converts SVG files to data URI format for use in href attributes
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import base64
import urllib.parse
import re
from pathlib import Path

class SVGConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SVG to Href Converter")
        self.root.geometry("800x700")
        
        # Variables
        self.format_var = tk.StringVar(value="base64")
        self.minify_var = tk.BooleanVar(value=True)
        self.html_wrap_var = tk.BooleanVar(value=False)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # File selection
        ttk.Label(main_frame, text="SVG File:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(0, weight=1)
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=50)
        self.file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(file_frame, text="Browse", command=self.browse_file).grid(row=0, column=1)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Format selection
        ttk.Label(options_frame, text="Format:").grid(row=0, column=0, sticky=tk.W)
        format_frame = ttk.Frame(options_frame)
        format_frame.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Radiobutton(format_frame, text="Base64", variable=self.format_var, 
                       value="base64").grid(row=0, column=0, padx=(0, 10))
        ttk.Radiobutton(format_frame, text="URL-encoded", variable=self.format_var, 
                       value="url").grid(row=0, column=1, padx=(0, 10))
        ttk.Radiobutton(format_frame, text="Both", variable=self.format_var, 
                       value="both").grid(row=0, column=2)
        
        # Checkboxes
        ttk.Checkbutton(options_frame, text="Minify SVG (remove extra whitespace)", 
                       variable=self.minify_var).grid(row=1, column=0, columnspan=2, 
                                                     sticky=tk.W, pady=(10, 0))
        ttk.Checkbutton(options_frame, text="Wrap in HTML anchor tag", 
                       variable=self.html_wrap_var).grid(row=2, column=0, columnspan=2, 
                                                        sticky=tk.W, pady=(5, 0))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        ttk.Button(button_frame, text="Convert", command=self.convert_svg).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Clear", command=self.clear_output).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(button_frame, text="Copy to Clipboard", command=self.copy_to_clipboard).grid(row=0, column=2)
        
        # Output area
        ttk.Label(main_frame, text="Output:").grid(row=3, column=0, sticky=(tk.W, tk.N), pady=(0, 5))
        
        # Text area with scrollbar
        self.output_text = scrolledtext.ScrolledText(main_frame, height=20, width=80, wrap=tk.WORD)
        self.output_text.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def browse_file(self):
        """Open file dialog to select SVG file"""
        file_path = filedialog.askopenfilename(
            title="Select SVG File",
            filetypes=[("SVG files", "*.svg"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def minify_svg(self, svg_content):
        """Basic SVG minification"""
        # Remove comments
        svg_content = re.sub(r'<!--.*?-->', '', svg_content, flags=re.DOTALL)
        # Remove extra whitespace between tags
        svg_content = re.sub(r'>\s+<', '><', svg_content)
        # Remove leading/trailing whitespace
        svg_content = svg_content.strip()
        return svg_content
    
    def svg_to_base64_href(self, svg_content):
        """Convert SVG content to Base64 data URI"""
        encoded = base64.b64encode(svg_content.encode('utf-8')).decode('ascii')
        return f'data:image/svg+xml;base64,{encoded}'
    
    def svg_to_url_encoded_href(self, svg_content):
        """Convert SVG content to URL-encoded data URI"""
        encoded = urllib.parse.quote(svg_content, safe='')
        return f'data:image/svg+xml,{encoded}'
    
    def convert_svg(self):
        """Convert the selected SVG file"""
        file_path = self.file_path_var.get().strip()
        
        if not file_path:
            messagebox.showerror("Error", "Please select an SVG file")
            return
        
        try:
            # Read SVG file
            svg_path = Path(file_path)
            if not svg_path.exists():
                messagebox.showerror("Error", f"File '{file_path}' not found")
                return
            
            svg_content = svg_path.read_text(encoding='utf-8')
            
            # Minify if requested
            if self.minify_var.get():
                svg_content = self.minify_svg(svg_content)
            
            # Generate output
            output_lines = []
            format_choice = self.format_var.get()
            
            if format_choice in ['base64', 'both']:
                base64_uri = self.svg_to_base64_href(svg_content)
                if self.html_wrap_var.get():
                    base64_result = f'<a href="{base64_uri}">Link</a>'
                else:
                    base64_result = base64_uri
                
                if format_choice == 'both':
                    output_lines.append("Base64 format:")
                output_lines.append(base64_result)
                if format_choice == 'both':
                    output_lines.append("")
            
            if format_choice in ['url', 'both']:
                url_uri = self.svg_to_url_encoded_href(svg_content)
                if self.html_wrap_var.get():
                    url_result = f'<a href="{url_uri}">Link</a>'
                else:
                    url_result = url_uri
                
                if format_choice == 'both':
                    output_lines.append("URL-encoded format:")
                output_lines.append(url_result)
            
            # Display output
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(1.0, '\n'.join(output_lines))
            
            # Update status
            file_size = len(svg_content)
            output_size = len('\n'.join(output_lines))
            self.status_var.set(f"Converted successfully | Original: {file_size} chars | Output: {output_size} chars")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert file: {str(e)}")
            self.status_var.set("Error occurred")
    
    def clear_output(self):
        """Clear the output text area"""
        self.output_text.delete(1.0, tk.END)
        self.status_var.set("Output cleared")
    
    def copy_to_clipboard(self):
        """Copy output to clipboard"""
        try:
            output_content = self.output_text.get(1.0, tk.END).strip()
            if not output_content:
                messagebox.showwarning("Warning", "No output to copy")
                return
            
            self.root.clipboard_clear()
            self.root.clipboard_append(output_content)
            self.status_var.set("Copied to clipboard")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard: {str(e)}")

def main():
    root = tk.Tk()
    app = SVGConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()