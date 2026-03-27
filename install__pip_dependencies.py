import subprocess
import sys
import os
import importlib.metadata

def install_uv():
    print("--------------------------------------------------")
    print("Step 1: Installing/Upgrading 'uv' package manager...")
    print("--------------------------------------------------")
    try:
        # Upgrade pip, wheel, and setuptools first
        print("Upgrading pip, wheel, and setuptools...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "wheel", "setuptools"])
        
        # Install uv
        print("Installing uv...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "uv"])
        print("\n'uv' installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing uv: {e}")
        sys.exit(1)

def get_installed_packages():
    return {dist.metadata['Name'].lower() for dist in importlib.metadata.distributions()}

def install_packages_smartly(packages):
    print("\n--------------------------------------------------")
    print("Step 2: Checking and Installing packages...")
    print("--------------------------------------------------")
    
    if not packages:
        print("No packages specified.")
        return

    installed_set = get_installed_packages()
    
    pre_existing = []
    installed_with_uv = []
    failed = []

    # Filter packages that need installation
    to_install = []
    for pkg in packages:
        # Simple name check (ignores version specifiers for now for simplicity)
        pkg_name = pkg.split("==")[0].split(">=")[0].lower()
        
        if pkg_name in installed_set:
            pre_existing.append(pkg)
            print(f"[SKIP] {pkg} is already installed.")
        else:
            to_install.append(pkg)

    if to_install:
        print(f"\nInstalling missing packages with 'uv': {', '.join(to_install)}")
        # Install one by one or batch? Batch is faster with uv.
        # But if one fails, we might want to know.
        # Let's try batch first for speed.
        cmd = [sys.executable, "-m", "uv", "pip", "install", "--system"] + to_install
        try:
            print(f"Running: {' '.join(cmd)}")
            subprocess.check_call(cmd)
            installed_with_uv.extend(to_install)
        except subprocess.CalledProcessError:
            print("\nBatch install failed. Trying individually...")
            for pkg in to_install:
                try:
                    subprocess.check_call([sys.executable, "-m", "uv", "pip", "install", "--system", pkg])
                    installed_with_uv.append(pkg)
                except subprocess.CalledProcessError:
                    print(f"[FAIL] Failed to install {pkg}")
                    failed.append(pkg)
    
    # Summary
    print("\n" + "="*50)
    print("INSTALLATION SUMMARY")
    print("="*50)
    
    print(f"\nPre-existing packages (Skipped): {len(pre_existing)}")
    for p in pre_existing:
        print(f"  - {p}")
        
    print(f"\nNewly installed with 'uv': {len(installed_with_uv)}")
    for p in installed_with_uv:
        print(f"  - {p}")
        
    if failed:
        print(f"\nFAILED to install: {len(failed)}")
        for p in failed:
            print(f"  - {p}")

if __name__ == "__main__":
    # Extensive list of common/observed packages in your environment
    required_packages = [
        "aiofiles", "aiohttp", "beautifulsoup4", "black", "click", 
        "clipboard", "colorama", "customtkinter", "flask-cors", 
        "apscheduler", "darkdetect", "packaging", "pyperclip", 
        "winshell", "pypiwin32", "keyboard", "mouse", "screeninfo",
        "psutil", "requests", "pillow", "pywin32", "pandas",
        "numpy", "scipy", "scikit-learn", "torch", "transformers",
        "opencv-python", "selenium", "webdriver-manager",
        "pyautogui", "pydirectinput", "pygetwindow", "pywinauto",
        "pynput", "pygame", "sounddevice", "soundfile", "pyaudio",
        "speechrecognition", "gtts", "openai", "anthropic",
        "langchain", "tiktoken", "fastapi", "uvicorn", "flask",
        "sqlalchemy", "alembic", "rich", "tqdm", "typer",
        "watchdog", "python-dotenv", "pyyaml", "lxml",
        "openpyxl", "reportlab", "pdf2image", "pymupdf", 
        "pyqt6", "pyqt6-webengine", "pywebview", "flet",
        "annotated-types", "anyio", "attrs", "certifi", "cffi",
        "charset-normalizer", "distro", "dnspython", "h11",
        "httpcore", "httpx", "idna", "sniffio", "typing-extensions",
        "urllib3", "websockets", "wheel", "setuptools", "uv"
    ]

    print(f"Python Executable: {sys.executable}")
    
    install_uv()
    install_packages_smartly(required_packages)
    
    input("\nPress Enter to exit...")
