import sys
import os
import time
import json

def get_remaining_time():
    """Calculate and return the remaining time from the saved timer"""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    timer_file_path = os.path.join(script_dir, 'timer_end_time.txt')
    
    # Check if timer file exists
    if not os.path.exists(timer_file_path):
        print("No timer has been set. Please run set_timer.py first.")
        return None
    
    try:
        # Read end time from file
        with open(timer_file_path, 'r') as f:
            end_timestamp = float(f.read().strip())
        
        # Get current time
        current_timestamp = time.time()
        
        # Calculate remaining time
        remaining_seconds = int(end_timestamp - current_timestamp)
        
        if remaining_seconds <= 0:
            print("Timer has expired!")
            os.remove(timer_file_path)
            return None
        
        # Convert seconds to days, hours, minutes, seconds
        days = remaining_seconds // 86400
        hours = (remaining_seconds % 86400) // 3600
        minutes = (remaining_seconds % 3600) // 60
        seconds = remaining_seconds % 60
        
        # Return the time information as a dictionary
        return {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "total_seconds": remaining_seconds
        }
        
    except Exception as e:
        print(f"Error reading timer: {str(e)}")
        return None

def main():
    time_info = get_remaining_time()
    if time_info:
        # Format output similar to the existing script
        print(json.dumps(time_info))

if __name__ == "__main__":
    main()