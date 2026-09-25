
import subprocess

def run_command_and_search():
    command = input("Enter the command to run: ")

    try:
        # Run the command and capture its output
        process = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        output = process.stdout
        print("\n--- Command Output ---")
        print(output)
        print("--------------------\n")

        output_lines = output.splitlines()

        while True:
            search_query = input("Enter search term (or 'q' to quit, 'r' to re-run command): ")
            if search_query.lower() == 'q':
                break
            elif search_query.lower() == 'r':
                run_command_and_search() # Re-run the function to get a new command
                return # Exit the current function call after re-running

            if search_query:
                matching_lines = [line for line in output_lines if search_query.lower() in line.lower()]
                if matching_lines:
                    print(f"\n--- Lines matching '{search_query}' ---")
                    for line in matching_lines:
                        print(line)
                    print("------------------------------------\n")
                else:
                    print(f"No lines found matching '{search_query}'.")
            else:
                print("Please enter a search term.")

    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print(f"Stderr: {e.stderr}")
    except FileNotFoundError:
        print(f"Error: Command '{command.split()[0]}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    run_command_and_search()
