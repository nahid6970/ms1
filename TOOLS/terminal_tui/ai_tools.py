import os
import platform
import sys
import datetime
import json
import requests

def execute_tool(tool_name, arguments, tavily_api_key=None):
    """Executes a local tool and returns the result as a string."""
    try:
        if tool_name == "read_file":
            filepath = arguments.get('filepath') or arguments.get('path')
            if not filepath:
                return "Error: filepath argument is required."
            if not os.path.exists(filepath):
                return f"Error: File not found: {filepath}"
            if os.path.isdir(filepath):
                return f"Error: {filepath} is a directory. Use list_directory instead."
            
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                if len(content) > 8000:
                    return content[:8000] + "\n\n... (Content truncated)"
                return content

        elif tool_name == "write_file":
            filepath = arguments.get('filepath') or arguments.get('path')
            content = arguments.get('content', '')
            if not filepath:
                return "Error: filepath argument is required."
            
            dirname = os.path.dirname(filepath)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
                
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote to {filepath}."

        elif tool_name == "delete_file":
            filepath = arguments.get('filepath') or arguments.get('path')
            if not filepath:
                return "Error: filepath argument is required."
            if not os.path.exists(filepath):
                return f"Error: File not found: {filepath}"
            
            if os.path.isdir(filepath):
                import shutil
                shutil.rmtree(filepath)
                return f"Deleted directory: {filepath}"
            else:
                os.remove(filepath)
                return f"Deleted file: {filepath}"
                
        elif tool_name == "list_directory":
            path = arguments.get('path', '.')
            if not os.path.exists(path):
                return f"Error: Directory not found: {path}"
            
            files = os.listdir(path)
            return "\n".join(files) if files else "Directory is empty."
            
        elif tool_name == "get_system_info":
            info = [
                f"OS: {platform.system()} {platform.release()}",
                f"Python: {sys.version}",
                f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"CWD: {os.getcwd()}"
            ]
            return "\n".join(info)

        elif tool_name == "web_search":
            query = arguments.get('query')
            if not query or not tavily_api_key:
                return "Error: Query or Tavily API Key missing."
            
            url = "https://api.tavily.com/search"
            payload = {"api_key": tavily_api_key, "query": query, "max_results": 5}
            res = requests.post(url, json=payload, timeout=15)
            results = res.json().get('results', [])
            return "\n".join([f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content']}\n" for r in results]) or "No results."

        elif tool_name == "run_shell_command":
            command = arguments.get('command')
            if not command: return "Error: No command."
            import subprocess
            try:
                res = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
                out = (res.stdout or "") + (res.stderr or "")
                return out[:8000] if out.strip() else f"Done (Code {res.returncode})"
            except subprocess.TimeoutExpired:
                return "Error: Timeout."

        elif tool_name == "request_follow_up":
            return f"Follow-up turn granted: {arguments.get('reason', 'Processing...')}"
            
    except Exception as e:
        return f"Error: {str(e)}"
    return f"Unknown tool: {tool_name}"

OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Reads a local file.",
            "parameters": {"type": "object", "properties": {"filepath": {"type": "string"}}, "required": ["filepath"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Writes/Overwrites a local file.",
            "parameters": {"type": "object", "properties": {"filepath": {"type": "string"}, "content": {"type": "string"}}, "required": ["filepath", "content"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "Deletes a file/folder.",
            "parameters": {"type": "object", "properties": {"filepath": {"type": "string"}}, "required": ["filepath"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "Lists directory contents.",
            "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_info",
            "description": "Gets OS and environment info.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Searches the web.",
            "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell_command",
            "description": "Runs a Windows shell command.",
            "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "request_follow_up",
            "description": "Requests an extra turn to continue multi-step work.",
            "parameters": {"type": "object", "properties": {"reason": {"type": "string"}}}
        }
    }
]

GEMINI_TOOLS = [{"functionDeclarations": [
    {
        "name": "read_file",
        "description": "Reads a local file.",
        "parameters": {"type": "OBJECT", "properties": {"filepath": {"type": "STRING"}}, "required": ["filepath"]}
    },
    {
        "name": "write_file",
        "description": "Writes content to a file.",
        "parameters": {"type": "OBJECT", "properties": {"filepath": {"type": "STRING"}, "content": {"type": "STRING"}}, "required": ["filepath", "content"]}
    },
    {
        "name": "delete_file",
        "description": "Deletes a file or folder.",
        "parameters": {"type": "OBJECT", "properties": {"filepath": {"type": "STRING"}}, "required": ["filepath"]}
    },
    {
        "name": "list_directory",
        "description": "Lists directory contents.",
        "parameters": {"type": "OBJECT", "properties": {"path": {"type": "STRING"}}, "required": ["path"]}
    },
    {
        "name": "get_system_info",
        "description": "Gets system environment info.",
        "parameters": {"type": "OBJECT", "properties": {}}
    },
    {
        "name": "web_search",
        "description": "Search the internet via Tavily.",
        "parameters": {"type": "OBJECT", "properties": {"query": {"type": "STRING"}}, "required": ["query"]}
    },
    {
        "name": "run_shell_command",
        "description": "Runs a shell command on the host.",
        "parameters": {"type": "OBJECT", "properties": {"command": {"type": "STRING"}}, "required": ["command"]}
    },
    {
        "name": "request_follow_up",
        "description": "Triggers another loop turn for complex tasks.",
        "parameters": {"type": "OBJECT", "properties": {"reason": {"type": "STRING"}}}
    }
]}]

def get_enabled_openai_tools(enabled_list):
    tools = [t for t in OPENAI_TOOLS if t['function']['name'] in enabled_list]
    return tools if tools else None

def get_enabled_gemini_tools(enabled_list):
    declarations = [d for d in GEMINI_TOOLS[0]['functionDeclarations'] if d['name'] in enabled_list]
    if not declarations: return None
    return [{"functionDeclarations": declarations}]
