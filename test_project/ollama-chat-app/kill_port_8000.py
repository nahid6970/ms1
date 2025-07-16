

import os
import subprocess

def kill_process_on_port(port):
    try:
        command = f"netstat -ano | findstr :{port}"
        result = subprocess.check_output(command, shell=True, text=True)
        if not result:
            print(f"No process found using port {port}.")
            return

        lines = result.strip().split('\n')
        for line in lines:
            parts = line.strip().split()
            if len(parts) > 0 and parts[0].upper() == 'TCP' and parts[1].endswith(f":{port}"):
                pid = parts[-1]
                print(f"Process using port {port} found with PID: {pid}")

                kill_command = f"taskkill /PID {pid} /F"
                kill_result = subprocess.check_output(kill_command, shell=True, text=True)
                print(kill_result)
                return

        print(f"Could not determine the process using port {port} from netstat output.")

    except subprocess.CalledProcessError:
        print(f"No process found using port {port}.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    kill_process_on_port(8000)

