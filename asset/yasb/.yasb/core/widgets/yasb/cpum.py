import psutil
import tkinter as tk

def get_cpu_core_usage():
    # Get CPU usage for each core
    cpu_usage_per_core = psutil.cpu_percent(interval=None, percpu=True)
    return cpu_usage_per_core

def update_cpu_core_bars():
    # Get CPU usage for each core
    cpu_core_usage = get_cpu_core_usage()
    # Update the bars for each CPU core
    for i, usage in enumerate(cpu_core_usage):
        core_bar = cpu_core_bars[i]
        # Calculate the height of the bar based on usage percentage
        bar_height = int((usage / 100) * BAR_HEIGHT)
        # Determine the color based on usage percentage
        bar_color = determine_color(usage)
        # Clear the previous bar
        core_bar.delete("all")
        # Draw the bar with the determined color
        core_bar.create_rectangle(0, BAR_HEIGHT - bar_height, BAR_WIDTH, BAR_HEIGHT, fill=bar_color)
    # Schedule the next update
    root.after(1000, update_cpu_core_bars)

def determine_color(usage):
    if usage >= 90:
        return "#8B0000"  # Dark red for usage >= 90%
    elif usage >= 80:
        return "#f12c2f"  # Red for usage >= 80%
    elif usage >= 50:
        return "#ff9282"  # Light red for usage >= 50%
    else:
        return "#14bcff"  # Default color

BAR_WIDTH = 8
BAR_HEIGHT = 25

# Create tkinter root window
root = tk.Tk()
root.title("CPU Core Usage")

# Create frame for CPU core bars
cpu_core_frame = tk.Frame(root, bg="#1d2027", highlightthickness=1, highlightbackground="#717d99", relief="solid")
cpu_core_frame.pack(side="right", anchor="nw", padx=0, pady=1)

# Create canvas widgets for CPU core bars
cpu_core_bars = []
for i in range(psutil.cpu_count()):
    frame = tk.Frame(cpu_core_frame, bg="#1d2027")
    frame.pack(side="left", padx=(0, 0), pady=0)
    core_bar = tk.Canvas(frame, bg="#1d2027", width=BAR_WIDTH, height=BAR_HEIGHT, highlightthickness=0)
    core_bar.pack(side="top")
    cpu_core_bars.append(core_bar)

# Start updating CPU core bars
update_cpu_core_bars()

# Run the tkinter event loop
root.mainloop()
