import tkinter as tk
import psutil
import asyncio
import threading

async def update_speed():
    while True:
        try:
            previous_disk_io = psutil.disk_io_counters(perdisk=True)[next(iter(psutil.disk_io_counters(perdisk=True).keys()))]
            await asyncio.sleep(1)  # Wait for 1 second
            current_disk_io = psutil.disk_io_counters(perdisk=True)[next(iter(psutil.disk_io_counters(perdisk=True).keys()))]

            read_speed = (current_disk_io.read_bytes - previous_disk_io.read_bytes) / 1024 / 1024
            write_speed = (current_disk_io.write_bytes - previous_disk_io.write_bytes) / 1024 / 1024

            read_label.config(text=f"Read Speed: {read_speed:.2f} MB/s")
            write_label.config(text=f"Write Speed: {write_speed:.2f} MB/s")
        except (psutil.NoSuchDevice, KeyError):
            read_label.config(text="Error: Disk not found")
            write_label.config(text="Error: Disk not found")

def start_monitoring():
    # Start a new thread for the asyncio event loop
    threading.Thread(target=start_asyncio_event_loop, daemon=True).start()

def start_asyncio_event_loop():
    # Create and run the asyncio event loop
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(update_speed())

# Create Tkinter window
root = tk.Tk()
root.title("Disk Speed Monitor")

# Create labels for read and write speed
read_label = tk.Label(root, text="Read Speed: 0.00 MB/s")
write_label = tk.Label(root, text="Write Speed: 0.00 MB/s")
read_label.pack()
write_label.pack()

# Start monitoring in a separate thread
start_monitoring()

# Run Tkinter event loop
root.mainloop()
