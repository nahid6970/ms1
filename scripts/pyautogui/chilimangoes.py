# chilimangoes.py

from ctypes import windll, c_char_p, c_buffer
from struct import calcsize, pack
from PIL import Image
from functools import partial

# This will make ImageGrab.grab capture all monitors, not just the primary
from PIL import ImageGrab
ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

gdi32 = windll.gdi32

# Win32 constants
NULL = 0
HORZRES = 8
VERTRES = 10
SRCCOPY = 13369376
HGDI_ERROR = 4294967295
ERROR_INVALID_PARAMETER = 87
SM_XVIRTUALSCREEN = 76
SM_YVIRTUALSCREEN = 77
SM_CXVIRTUALSCREEN = 78
SM_CYVIRTUALSCREEN = 79

screen_size = (10000, 10000)  # Fallback until measured

def grab_screen(region=None):
    bitmap = None
    try:
        screen = gdi32.CreateDCA(b'DISPLAY', None, None, None)
        screen_copy = gdi32.CreateCompatibleDC(screen)

        if region:
            left, top, width, height = region
        else:
            left = windll.user32.GetSystemMetrics(SM_XVIRTUALSCREEN)
            top = windll.user32.GetSystemMetrics(SM_YVIRTUALSCREEN)
            width = windll.user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)
            height = windll.user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)

        bitmap = gdi32.CreateCompatibleBitmap(screen, width, height)
        if bitmap == NULL:
            return

        hobj = gdi32.SelectObject(screen_copy, bitmap)
        if hobj == NULL or hobj == HGDI_ERROR:
            return

        if gdi32.BitBlt(screen_copy, 0, 0, width, height, screen, left, top, SRCCOPY) == NULL:
            return

        bmp_header = pack('LHHHH', calcsize('LHHHH'), width, height, 1, 24)
        bmp_buffer = c_buffer(bmp_header)
        bmp_bits = c_buffer(b' ' * (height * ((width * 3 + 3) & -4)))

        got_bits = gdi32.GetDIBits(screen_copy, bitmap, 0, height, bmp_bits, bmp_buffer, 0)
        if got_bits == NULL or got_bits == ERROR_INVALID_PARAMETER:
            return

        image = Image.frombuffer('RGB', (width, height), bmp_bits, 'raw', 'BGR', (width * 3 + 3) & -4, -1)

        if not region:
            global screen_size
            screen_size = image.size
        return image
    finally:
        if bitmap:
            gdi32.DeleteObject(bitmap)
        gdi32.DeleteDC(screen_copy)
        gdi32.DeleteDC(screen)
