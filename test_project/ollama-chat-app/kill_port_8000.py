import os
import subprocess
import sys

def kill_and_start_server(port):
    """
    Finds and terminates any process listening on the specified port,
    then starts the server.py script.
    """
    # --- Kill Process Section ---
    try:
        # Command to find the process listening on the port
        command = f"netstat -ano | findstr LISTENING | findstr :{port}"
        result = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.PIPE)
        
        # If a process is found, the result will not be empty
        lines = result.strip().split('\n')
        for line in lines:
            if not line:
                continue
            parts = line.strip().split()
            pid = parts[-1]
            print(f"Found process (PID: {pid}) listening on port {port}. Terminating it.")
            
            # Terminate the process
            kill_command = f"taskkill /PID {pid} /F"
            kill_result = subprocess.check_output(kill_command, shell=True, text=True)
            print(kill_result.strip())

    except subprocess.CalledProcessError:
        # This is the expected outcome if no process is running on the port
        print(f"No process found listening on port {port}.")
    except Exception as e:
        print(f"An error occurred while checking for the process: {e}")

    # --- Start Server Section ---
    try:
        print("\nStarting server.py...")
        # Use Popen to run the server in a new, non-blocking process
        subprocess.Popen([sys.executable, "server.py"])
        print("server.py has been started in a new process.")
        print(f"You should be able to access it at http://localhost:{port}")
    except FileNotFoundError:
        print("Error: Could not find server.py in the current directory.")
    except Exception as e:
        print(f"An error occurred while starting server.py: {e}")

if __name__ == "__main__":
    kill_and_start_server(8000)