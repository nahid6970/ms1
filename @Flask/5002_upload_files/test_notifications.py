import time
import os
from upload_files import show_upload_notification

def main():
    print("=" * 60)
    print("Notification System Visual Test")
    print("=" * 60)
    print("Triggering 50 notifications to demonstrate:")
    print("1. All notifications displaying inside a single card.")
    print("2. Newest files appearing instantly at the top of the list.")
    print("3. File info (size and arrival time) clean-aligned to the right side.")
    print("4. Dynamic bullet point colors based on file extension.")
    print("5. Mousewheel scrolling enabled with hidden scrollbar track.")
    print("6. Muted summary count indicating 'Total: 50 files' at the bottom-left.")
    print("7. Sleek dark aesthetics with a red 'Clear' text link button at the bottom-right.")
    print("-" * 60)
    print("Notice: Dispatched at 1 notification per second...")
    print("-" * 60)
    
    # Target directory for test files
    share_dir = os.path.join(os.path.expanduser('~/Desktop'), "ShareFolder")
    os.makedirs(share_dir, exist_ok=True)

    # Extension rotation list
    extensions = ['.txt', '.pdf', '.png', '.zip', '.mp4']

    # Send 50 test notifications (1 second delay)
    for i in range(1, 51):
        ext = extensions[i % len(extensions)]
        filename = f"report_file_{i:02d}{ext}"
        dummy_path = os.path.join(share_dir, filename)
        
        # Write dummy data to vary the size (from 10 KB to 500 KB)
        try:
            with open(dummy_path, "w") as f:
                f.write("x" * (i * 1024 * 10))
        except Exception:
            pass

        # Call notification helper
        show_upload_notification(filename, dummy_path)
        print(f"[{i:02d}/50] Dispatched: {filename} (Size: {i*10} KB, Ext: {ext})")
        time.sleep(1.0)  # 1 notification per second
        
    print("-" * 60)
    print("✅ All 50 test notifications dispatched!")
    print("Please check the bottom-right corner of your desktop screen.")
    print("Use your mouse wheel to scroll through all the notifications!")
    print("-" * 60)
    input("Press ENTER key to exit this test script and clean up dummy files...")
    
    # Cleanup test files
    for i in range(1, 51):
        ext = extensions[i % len(extensions)]
        filename = f"report_file_{i:02d}{ext}"
        dummy_path = os.path.join(share_dir, filename)
        try:
            if os.path.exists(dummy_path):
                os.remove(dummy_path)
        except Exception:
            pass
    print("Cleanup complete.")

if __name__ == "__main__":
    main()
