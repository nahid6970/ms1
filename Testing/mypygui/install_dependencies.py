import subprocess
import sys
import os

def check_pip():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "--version"])
        return True
    except subprocess.CalledProcessError:
        return False

def install_uv():
    print("--------------------------------------------------")
    print("Step 1: Installing/Upgrading 'uv' package manager...")
    print("--------------------------------------------------")
    try:
        # Upgrade pip, wheel, and setuptools first to avoid build issues
        print("Upgrading pip, wheel, and setuptools...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "wheel", "setuptools"])
        
        # Install uv
        print("Installing uv...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "uv"])
        print("\n'uv' installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing uv: {e}")
        sys.exit(1)

def install_packages_globally(packages):
    print("\n--------------------------------------------------")
    print("Step 2: Installing packages globally using 'uv'...")
    print("--------------------------------------------------")
    
    if not packages:
        print("No packages specificed.")
        return

    cmd = [sys.executable, "-m", "uv", "pip", "install", "--system"] + packages
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("\n--------------------------------------------------")
        print("SUCCESS: All packages installed successfully.")
        print("--------------------------------------------------")
    except subprocess.CalledProcessError as e:
        print(f"\nError installing packages: {e}")
        print("Try running this script as Administrator if you encounter permission errors.")
        sys.exit(1)

if __name__ == "__main__":
    # List of packages to install
    # Add any other modules you need here
    required_packages = [
        "customtkinter",
        "psutil",
        "requests",
        "pillow",
        "pywin32"
    ]

    print(f"Python Executable: {sys.executable}")
    
    install_uv()
    install_packages_globally(required_packages)
    
    input("\nPress Enter to exit...")
