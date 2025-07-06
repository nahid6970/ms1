import json
import os

def create_static_html():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(base_dir, 'templates')
    myhome_dir = os.path.join(base_dir, 'myhome')
    data_file = os.path.join(base_dir, 'data.json')

    # Read HTML template
    with open(os.path.join(templates_dir, 'myhome_input.html'), 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Read CSS
    with open(os.path.join(myhome_dir, 'myhome.css'), 'r', encoding='utf-8') as f:
        css_content = f.read()

    # Read links_handler.js
    with open(os.path.join(myhome_dir, 'links_handler.js'), 'r', encoding='utf-8') as f:
        links_handler_js_content = f.read()

    # Read script.js
    with open(os.path.join(myhome_dir, 'script.js'), 'r', encoding='utf-8') as f:
        script_js_content = f.read()

    # Read data.json
    with open(data_file, 'r', encoding='utf-8') as f:
        data_json_content = json.load(f)

    # Modify links_handler.js to use embedded data
    # Replace fetch('/api/links') with direct use of embedded data
    links_handler_js_content = links_handler_js_content.replace(
        "const response = await fetch('/api/links');\n      const links = await response.json();",
        "const links = window.EMBEDDED_LINKS_DATA;"
    )
    links_handler_js_content = links_handler_js_content.replace(
        "fetchAndDisplayLinks();",
        "fetchAndDisplayLinks(window.EMBEDDED_LINKS_DATA);"
    )

    # Embed CSS
    html_content = html_content.replace(
        '<link rel="stylesheet" href="myhome/myhome.css" ;>',
        f'<style>{css_content}</style>'
    )

    # Embed JavaScript and JSON data
    # The order matters: data first, then links_handler.js, then script.js
    js_embedding = f'''
    <script>
        window.EMBEDDED_LINKS_DATA = {json.dumps(data_json_content, indent=2)};
    </script>
    <script>
        {links_handler_js_content}
    </script>
    <script>
        {script_js_content}
    </script>
    '''
    html_content = html_content.replace(
        '<script src="myhome/links_handler.js"></script>',
        js_embedding
    )
    html_content = html_content.replace(
        '<script src="myhome/script.js"></script>',
        '' # Remove the original script.js tag as it's now embedded
    )


    # Write the static HTML file
    with open(os.path.join(base_dir, 'static_myhome.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("Static HTML file 'static_myhome.html' created successfully.")

if __name__ == '__main__':
    create_static_html()
