from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QGridLayout, QWidget, QHBoxLayout, QFrame, QVBoxLayout
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QFont
import psutil
from functionlist import *


class HoverButton(QPushButton):
    left_clicked = pyqtSignal()
    right_clicked = pyqtSignal()
    ctrl_left_clicked = pyqtSignal()
    ctrl_right_clicked = pyqtSignal()

    def __init__(self, text, initial_color, hover_color, hover_after_color):
        super().__init__(text)
        self.initial_color = initial_color
        self.hover_color = hover_color
        self.hover_after_color = hover_after_color
        self.setStyleSheet(self.initial_color)

    def enterEvent(self, event):
        self.setStyleSheet(self.hover_color)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet(self.hover_after_color)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.ctrl_left_clicked.emit()
            else:
                self.left_clicked.emit()
        elif event.buttons() & Qt.MouseButton.RightButton:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.ctrl_right_clicked.emit()
            else:
                self.right_clicked.emit()
        super().mousePressEvent(event)

def close_window():
    app.quit()







app = QApplication([])


font = QFont("JetBrainsMono NFP", 12)
app.setFont(font)

# Create main window
window = QWidget()
window.setWindowTitle("Grid Layout Example")
#! window.resize(1920, 40)
window.setFixedWidth(1920)
window.setFixedHeight(40)
window.setStyleSheet("background-color: #78cdff;")
window.setWindowFlag(Qt.WindowType.FramelessWindowHint)


main_layout = QHBoxLayout()
main_layout.setContentsMargins(0, 0, 0, 0)  # Set margins to 0


frame1 = QFrame()
frame1.setFixedHeight(40)
frame1.setStyleSheet("background-color: #b14545;")
frame1_layout = QGridLayout()
frame1_layout.setContentsMargins(0, 0, 0, 0)  # Set margins to 0
# frame1_layout.setVerticalSpacing(0)  # Set vertical spacing to 0




# Add buttons to layout
close_win = HoverButton("\uf530",
                      initial_color="font-size: 20px; color:#477566; margin:4px 0px;border-radius: 5px; background-color: aqua;", 
                      hover_color="font-size: 20px; color:#000000; margin:4px 0px;", 
                      hover_after_color="font-size: 20px; color:#bcffe9; margin:4px 0px;"
                      )
button2 = HoverButton("Button 2",
                      initial_color="font-size: 20px; color:#ffffff; margin:4px 0px;", 
                      hover_color="font-size: 20px; color:#000000; margin:4px 0px;", 
                      hover_after_color="font-size: 20px; color:#ffffff; margin:4px 0px;"
                      )
button3 = HoverButton("Button 3",
                      initial_color="font-size: 20px; color:#ffffff; margin:4px 0px;", 
                      hover_color="font-size: 20px; color:#000000; margin:4px 0px;", 
                      hover_after_color="font-size: 20px; color:#ffffff; margin:4px 0px;"
                      )

# Add buttons to specific positions in the grid
frame1_layout.addWidget(close_win, 0, 0)  # Button 1 at row 0, column 0
frame1_layout.addWidget(button2, 0, 1)  # Button 2 at row 0, column 1
frame1_layout.addWidget(button3, 0, 3, 1, 2)  # Button 3 spans from row 1, column 0 to row 1, column 1
frame1.setLayout(frame1_layout)


# Connect button signals to functions
def open_backup():
    print("Open backup")

def edit_backup():
    print("Edit backup")

close_win.left_clicked.connect(close_window)
close_win.right_clicked.connect(launch_LockBox)
close_win.ctrl_left_clicked.connect(lambda: print("Ctrl + Left Mouse Button clicked on Button 1"))
close_win.ctrl_right_clicked.connect(lambda: print("Ctrl + Right Mouse Button clicked on Button 1"))

button2.left_clicked.connect(launch_LockBox)
button2.right_clicked.connect(launch_LockBox)
button2.ctrl_left_clicked.connect(lambda: print("Ctrl + Left Mouse Button clicked on Button 2"))
button2.ctrl_right_clicked.connect(lambda: print("Ctrl + Right Mouse Button clicked on Button 2"))

button3.left_clicked.connect(launch_LockBox)
button3.right_clicked.connect(launch_LockBox)
button3.ctrl_left_clicked.connect(lambda: print("Ctrl + Left Mouse Button clicked on Button 3"))
button3.ctrl_right_clicked.connect(lambda: print("Ctrl + Right Mouse Button clicked on Button 3"))




frame2 = QFrame()
frame2.setStyleSheet("background-color: #bb9a06;")
frame2_layout = QHBoxLayout()
frame2_layout.setContentsMargins(0, 0, 0, 0)  # Set margins to 0

# Add buttons to second frame layout
button4 = HoverButton("Button 4", initial_color="font-size: 20px; color:#bcffe9; margin:4px 0px;", 
                      hover_color="font-size: 20px; color:#000000; margin:4px 0px;", 
                      hover_after_color="font-size: 20px; color:#bcffe9; margin:4px 0px;")
button5 = HoverButton("Button 5", initial_color="font-size: 20px; color:#ffffff; margin:4px 0px;", 
                      hover_color="font-size: 20px; color:#000000; margin:4px 0px;", 
                      hover_after_color="font-size: 20px; color:#ffffff; margin:4px 0px;")
button6 = HoverButton("Button 6",
                      initial_color="font-size: 20px; color:#ffffff; margin:4px 0px;", 
                      hover_color="font-size: 20px; color:#000000; margin:4px 0px;", 
                      hover_after_color="font-size: 20px; color:#ffffff; margin:4px 0px;"
                      )
frame2_layout.addWidget(button4)
frame2_layout.addWidget(button5)
frame2_layout.addWidget(button6)
frame2.setLayout(frame2_layout)


frame3 = QFrame()
frame3.setStyleSheet("background-color: #a0997a;")
frame3_layout = QVBoxLayout()
frame3_layout
# Add CPU label to second frame layout
_cpu_label = QLabel("CPU: -%")
frame3_layout.addWidget(_cpu_label)

# Update CPU label text and style using QTimer
def update_cpu_label():
    cpu_usage = psutil.cpu_percent()
    _cpu_label.setText(f"CPU: {cpu_usage}%")
    _cpu_label.setStyleSheet(determine_color(cpu_usage))
    _cpu_label.setAlignment(Qt.AlignmentFlag.AlignCenter)


# Function to determine color based on CPU usage
def determine_color(usage):
    if usage == 0:
        return "background-color: #03415f; color: #cefc58; border-radius: 5px;"  # Black background, green text
    elif usage < 25:
        return "background-color: #03415f; color: #cefc58; border-radius: 5px;"  # Black background, green text
    elif 10 <= usage < 50:
        return "background-color: #ff9282; color: #000000; border-radius: 5px;"  # Red background, black text
    elif 50 <= usage < 80:
        return "background-color: #ff6b54; color: #000000; border-radius: 5px;"  # Orange background, black text
    else:
        return "background-color: #ff3010; color: #FFFFFF; border-radius: 5px;"  # Yellow background, white text

# Set up QTimer to update CPU label every second
timer = QTimer()
timer.timeout.connect(update_cpu_label)
timer.start(1000)
frame3.setLayout(frame3_layout)












main_layout.addWidget(frame1)
main_layout.addWidget(frame2)
main_layout.addWidget(frame3)


window.setLayout(main_layout)
window.show()
app.exec()
