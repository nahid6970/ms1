import ctypes

# Define RECT structure
class RECT(ctypes.Structure):
    _fields_ = [
        ('left', ctypes.c_long),
        ('top', ctypes.c_long),
        ('right', ctypes.c_long),
        ('bottom', ctypes.c_long)
    ]

# Function to reset the work area to the full screen
def reset_work_area():
    rect = RECT()
    SPI_GETWORKAREA = 0x0030
    ctypes.windll.user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)

    # Reset work area to original dimensions (full screen)
    original_rect = RECT(0, 0, ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))
    SPI_SETWORKAREA = 0x002F
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETWORKAREA, 0, ctypes.byref(original_rect), 0)

# Reset the work area
reset_work_area()
