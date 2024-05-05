import pyautogui
import keyboard

# Set the speed of mouse movement
pyautogui.FAILSAFE = False
MOUSE_SPEED = 10

def move_mouse_up_down():
    while keyboard.is_pressed('w'):
        pyautogui.move(0, -MOUSE_SPEED)
    while keyboard.is_pressed('s'):
        pyautogui.move(0, MOUSE_SPEED)

def move_mouse_left_right():
    while keyboard.is_pressed('a'):
        pyautogui.move(-MOUSE_SPEED, 0)
    while keyboard.is_pressed('d'):
        pyautogui.move(MOUSE_SPEED, 0)

def main():
    print("Use WASD keys to move the mouse. Press Esc to exit.")
    # Block the default functionality of WASD keys
    keyboard.block_key('w')
    keyboard.block_key('a')
    keyboard.block_key('s')
    keyboard.block_key('d')
    try:
        while True:
            move_mouse_up_down()
            move_mouse_left_right()
            if keyboard.is_pressed('esc'):
                break
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
