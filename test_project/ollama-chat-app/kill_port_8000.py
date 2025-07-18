import os
import subprocess
import sys

def kill_and_start_server(port):
    """
    Finds and terminates any process listening on the specified port,
    then starts the server.py script from a specific directory.
    """

    # --- Kill Process Section ---
    try:
        command = f"netstat -ano | findstr LISTENING | findstr :{port}"
        result = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.PIPE)
        
        lines = result.strip().split('\n')
        for line in lines:
            if not line:
                continue
            parts = line.strip().split()
            pid = parts[-1]
            print(f"Found process (PID: {pid}) listening on port {port}. Terminating it.")

            kill_command = f"taskkill /PID {pid} /F"
            kill_result = subprocess.check_output(kill_command, shell=True, text=True)
            print(kill_result.strip())

    except subprocess.CalledProcessError:
        print(f"No process found listening on port {port}.")
    except Exception as e:
        print(f"An error occurred while checking for the process: {e}")

    # --- Start Server Section ---
    try:
        server_path = os.path.join("C:/ms1/test_project/ollama-chat-app/app", "server.py")
        
        if not os.path.exists(server_path):
            raise FileNotFoundError(f"server.py not found at: {server_path}")

        print("\nStarting server.py...")
        subprocess.Popen(
            [sys.executable, server_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("server.py has been started in a new process.")
        print(f"You should be able to access it at http://localhost:{port}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred while starting server.py: {e}")

if __name__ == "__main__":
    kill_and_start_server(8000)
