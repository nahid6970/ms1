#!/usr/bin/env python3
"""
SVG to Href Data URI Converter
Converts SVG files to data URI format for use in href attributes
"""

import base64
import urllib.parse
import argparse
import sys
from pathlib import Path

def svg_to_base64_href(svg_content):
    """Convert SVG content to Base64 data URI"""
    encoded = base64.b64encode(svg_content.encode('utf-8')).decode('ascii')
    return f'data:image/svg+xml;base64,{encoded}'

def svg_to_url_encoded_href(svg_content):
    """Convert SVG content to URL-encoded data URI"""
    encoded = urllib.parse.quote(svg_content, safe='')
    return f'data:image/svg+xml,{encoded}'

def minify_svg(svg_content):
    """Basic SVG minification - removes extra whitespace"""
    import re
    # Remove comments
    svg_content = re.sub(r'<!--.*?-->', '', svg_content, flags=re.DOTALL)
    # Remove extra whitespace between tags
    svg_content = re.sub(r'>\s+<', '><', svg_content)
    # Remove leading/trailing whitespace
    svg_content = svg_content.strip()
    return svg_content

def main():
    parser = argparse.ArgumentParser(description='Convert SVG files to href data URI format')
    parser.add_argument('input_file', help='Input SVG file path')
    parser.add_argument('-o', '--output', help='Output file (optional, prints to console by default)')
    parser.add_argument('-f', '--format', choices=['base64', 'url', 'both'], 
                       default='base64', help='Output format (default: base64)')
    parser.add_argument('-m', '--minify', action='store_true', 
                       help='Minify SVG before encoding')
    parser.add_argument('--html', action='store_true', 
                       help='Wrap in HTML anchor tag')
    
    args = parser.parse_args()
    
    # Read SVG file
    try:
        svg_path = Path(args.input_file)
        if not svg_path.exists():
            print(f"Error: File '{args.input_file}' not found", file=sys.stderr)
            sys.exit(1)
        
        svg_content = svg_path.read_text(encoding='utf-8')
        
        # Minify if requested
        if args.minify:
            svg_content = minify_svg(svg_content)
        
        # Generate data URIs
        results = []
        
        if args.format in ['base64', 'both']:
            base64_uri = svg_to_base64_href(svg_content)
            if args.html:
                base64_result = f'<a href="{base64_uri}">Link</a>'
            else:
                base64_result = base64_uri
            results.append(('Base64', base64_result))
        
        if args.format in ['url', 'both']:
            url_uri = svg_to_url_encoded_href(svg_content)
            if args.html:
                url_result = f'<a href="{url_uri}">Link</a>'
            else:
                url_result = url_uri
            results.append(('URL-encoded', url_result))
        
        # Output results
        output_text = ""
        for format_name, result in results:
            if len(results) > 1:
                output_text += f"# {format_name} format:\n"
            output_text += result + "\n"
            if len(results) > 1:
                output_text += "\n"
        
        # Write to file or print
        if args.output:
            Path(args.output).write_text(output_text.strip(), encoding='utf-8')
            print(f"Output saved to: {args.output}")
        else:
            print(output_text.strip())
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()