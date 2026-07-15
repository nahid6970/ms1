import time
import os
from upload_files import show_upload_notification

def main():
    print("=" * 60)
    print("Notification System Visual Test")
    print("=" * 60)
    print("Triggering 50 notifications to demonstrate:")
    print("1. All notifications displaying inside a single card.")
    print("2. No gaps between items and the footer frame.")
    print("3. Mousewheel scrolling enabled with hidden scrollbar track.")
    print("4. Muted summary count indicating 'Total: 50 files' at the bottom-left.")
    print("5. Sleek dark aesthetics with a red 'Clear' text link button at the bottom-right.")
    print("-" * 60)
    
    # Send 50 test notifications
    for i in range(1, 51):
        filename = f"document_upload_report_{i:02d}.pdf"
        dummy_path = os.path.join(os.path.expanduser('~/Desktop'), "ShareFolder", filename)
        
        # Call notification helper
        show_upload_notification(filename, dummy_path)
        print(f"[{i:02d}/50] Dispatched: {filename}")
        time.sleep(0.03)  # Small delay for clean loading animation/display
        
    print("-" * 60)
    print("✅ All 50 test notifications dispatched!")
    print("Please check the bottom-right corner of your desktop screen.")
    print("Use your mouse wheel to scroll through all the notifications!")
    print("-" * 60)
    input("Press ENTER key to exit this test script...")

if __name__ == "__main__":
    main()
