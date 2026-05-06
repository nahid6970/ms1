import json
import sys

def validate_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("JSON is valid!")
        print(f"Contains {len(data)} top-level keys:")
        for key in sorted(data.keys()):
            if isinstance(data[key], list):
                print(f"  - {key}: list with {len(data[key])} items")
            elif isinstance(data[key], dict):
                print(f"  - {key}: dict with {len(data[key])} keys")
            else:
                print(f"  - {key}: {type(data[key]).__name__}")
        return True
    except json.JSONDecodeError as e:
        print(f"JSON syntax error: {e}")
        print(f"   Line {e.lineno}, Column {e.colno}")
        return False
    except Exception as e:
        print(f"Error reading file: {e}")
        return False

if __name__ == "__main__":
    file_path = r"C:\@delta\ms1\mypygui_config.json"
    validate_json(file_path)