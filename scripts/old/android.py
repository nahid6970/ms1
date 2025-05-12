import subprocess
import os

def run_script(script_content, script_type):
    # Determine the extension and filename for the test script
    if script_type == 'python':
        filename = 'test_script.py'
        command = ['python', filename]
    elif script_type == 'powershell':
        filename = 'test_script.ps1'
        command = ['powershell', '-ExecutionPolicy', 'Bypass', '-File', filename]
    else:
        print("Unsupported script type.")
        return

    # Write the script content to a temporary file
    with open(filename, 'w') as script_file:
        script_file.write(script_content)

    try:
        # Run the script and capture the output
        result = subprocess.run(command, capture_output=True, text=True)
        print(f"Output of {script_type} script:\n")
        print(result.stdout)
        if result.stderr:
            print(f"Errors:\n{result.stderr}")
    finally:
        # Clean up the temporary file
        os.remove(filename)

if __name__ == "__main__":
    # Example script content
    python_script = """
print("Hello from Python!")
"""

    powershell_script = """
Write-Host "Hello from PowerShell!"
"""

    # Test the Python script
    print("Testing Python script...")
    run_script(python_script, 'python')

    # Test the PowerShell script
    print("\nTesting PowerShell script...")
    run_script(powershell_script, 'powershell')
