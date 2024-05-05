import pyautogui
import keyboard

# Set the speed of mouse movement
pyautogui.FAILSAFE = False
MOUSE_SPEED = 10

def move_mouse_up_down():
    while keyboard.is_pressed('up'):
        pyautogui.move(0, -MOUSE_SPEED)
    while keyboard.is_pressed('down'):
        pyautogui.move(0, MOUSE_SPEED)

def move_mouse_left_right():
    while keyboard.is_pressed('left'):
        pyautogui.move(-MOUSE_SPEED, 0)
    while keyboard.is_pressed('right'):
        pyautogui.move(MOUSE_SPEED, 0)

def main():
    print("Use arrow keys to move the mouse.")
    try:
        while True:
            move_mouse_up_down()
            move_mouse_left_right()
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
