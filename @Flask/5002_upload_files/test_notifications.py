import time
import os
from upload_files import show_upload_notification, update_upload_progress

def main():
    print("=" * 60)
    print("Notification System Visual Test")
    print("=" * 60)
    print("Triggering 50 notifications with simulated progress updates:")
    print("1. Yellow bullet (•) and 'Uploading: X%' text for in-progress files.")
    print("2. Automatically switches to correct file color and metadata when completed.")
    print("3. Prevent clicking on notifications while they are uploading.")
    print("4. File size labels color-coded by range:")
    print("   - Muted Silver for < 1 MB")
    print("   - Bright Blue for 1 MB - 10 MB")
    print("   - Orange for 10 MB - 50 MB")
    print("   - Bright Red for > 50 MB")
    print("5. Dynamic bullet point colors based on file extension (once completed).")
    print("6. Filenames up to 28 characters displayed cleanly.")
    print("7. Perfect right-alignment of size and time details with dot leaders.")
    print("8. Mousewheel scrolling enabled with hidden scrollbar track.")
    print("9. Muted summary count indicating 'Total: 50 files' at the bottom-left.")
    print("10. Sleek dark aesthetics with a red 'Clear' text link button.")
    print("-" * 60)
    print("Notice: Simulating progress increments (0% -> 100% in 1s) per file...")
    print("-" * 60)
    
    # Target directory for test files
    share_dir = os.path.join(os.path.expanduser('~/Desktop'), "ShareFolder")
    os.makedirs(share_dir, exist_ok=True)

    # Extension rotation list
    extensions = ['.txt', '.pdf', '.png', '.zip', '.mp4']

    # Rotating sizes: 500 KB, 5 MB, 25 MB, 80 MB
    sizes_bytes = [
        500 * 1024,          # 500 KB -> Silver
        5 * 1024 * 1024,     # 5 MB   -> Blue
        25 * 1024 * 1024,    # 25 MB  -> Orange
        80 * 1024 * 1024     # 80 MB  -> Red
    ]

    # Send 50 test notifications (1 second delay total, with progress ticks)
    for i in range(1, 51):
        ext = extensions[i % len(extensions)]
        filename = f"report_file_{i:02d}{ext}"
        dummy_path = os.path.join(share_dir, filename)
        
        target_size = sizes_bytes[i % len(sizes_bytes)]

        # Create sparse file (fast, consumes zero disk write time)
        try:
            with open(dummy_path, "wb") as f:
                f.seek(target_size - 1)
                f.write(b"\0")
        except Exception:
            pass

        # Simulate upload progress steps (0% to 75%)
        for pct in [0, 25, 50, 75]:
            update_upload_progress(filename, pct, target_size)
            print(f"[{i:02d}/50] Progress: {filename} ({pct}%)")
            time.sleep(0.15)  # Quick transition steps
            
        # Dispatch the completed notification
        show_upload_notification(filename, dummy_path)
        print(f"[{i:02d}/50] Completed: {filename} ({target_size / (1024*1024):.1f} MB)")
        time.sleep(0.4)   # Short pause before starting next file
        
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
