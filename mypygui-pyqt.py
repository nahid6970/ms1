from PyQt6.QtWidgets import QApplication, QPushButton, QGridLayout, QWidget, QHBoxLayout, QFrame, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
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

app = QApplication([])

# Create main window
window = QWidget()
window.setWindowTitle("Grid Layout Example")
window.resize(400, 300)
# window.setStyleSheet("background-color: #f0f0f0;")
window.setWindowFlag(Qt.WindowType.FramelessWindowHint)

main_layout = QHBoxLayout()
frame1 = QFrame()
frame1_layout = QGridLayout()

# Add buttons to layout
button1 = HoverButton("X", initial_color="font-size: 20px; color:#477566; margin:4px 0px;", 
                      hover_color="font-size: 20px; color:#000000; margin:4px 0px;", 
                      hover_after_color="font-size: 20px; color:#bcffe9; margin:4px 0px;")
button2 = HoverButton("Button 2", initial_color="font-size: 20px; color:#ffffff; margin:4px 0px;", 
                      hover_color="font-size: 20px; color:#000000; margin:4px 0px;", 
                      hover_after_color="font-size: 20px; color:#ffffff; margin:4px 0px;")
button3 = HoverButton("Button 3", initial_color="font-size: 20px; color:#ffffff; margin:4px 0px;", 
                      hover_color="font-size: 20px; color:#000000; margin:4px 0px;", 
                      hover_after_color="font-size: 20px; color:#ffffff; margin:4px 0px;")

# Add buttons to specific positions in the grid
frame1_layout.addWidget(button1, 0, 0)  # Button 1 at row 0, column 0
frame1_layout.addWidget(button2, 0, 1)  # Button 2 at row 0, column 1
frame1_layout.addWidget(button3, 1, 0, 1, 2)  # Button 3 spans from row 1, column 0 to row 1, column 1
frame1.setLayout(frame1_layout)


# Connect button signals to functions
def open_backup():
    print("Open backup")

def edit_backup():
    print("Edit backup")

button1.left_clicked.connect(launch_LockBox)
button1.right_clicked.connect(launch_LockBox)

button2.left_clicked.connect(launch_LockBox)
button2.right_clicked.connect(launch_LockBox)

button3.left_clicked.connect(launch_LockBox)
button3.right_clicked.connect(launch_LockBox)

# Connect Ctrl + Left Mouse and Ctrl + Right Mouse events
button1.ctrl_left_clicked.connect(lambda: print("Ctrl + Left Mouse Button clicked on Button 1"))
button2.ctrl_left_clicked.connect(lambda: print("Ctrl + Left Mouse Button clicked on Button 2"))
button3.ctrl_left_clicked.connect(lambda: print("Ctrl + Left Mouse Button clicked on Button 3"))

button1.ctrl_right_clicked.connect(lambda: print("Ctrl + Right Mouse Button clicked on Button 1"))
button2.ctrl_right_clicked.connect(lambda: print("Ctrl + Right Mouse Button clicked on Button 2"))
button3.ctrl_right_clicked.connect(lambda: print("Ctrl + Right Mouse Button clicked on Button 3"))





frame2 = QFrame()
frame2_layout = QVBoxLayout()

# Add buttons to second frame layout
button4 = HoverButton("Button 4", initial_color="font-size: 20px; color:#bcffe9; margin:4px 0px;", 
                      hover_color="font-size: 20px; color:#000000; margin:4px 0px;", 
                      hover_after_color="font-size: 20px; color:#bcffe9; margin:4px 0px;")
button5 = HoverButton("Button 5", initial_color="font-size: 20px; color:#ffffff; margin:4px 0px;", 
                      hover_color="font-size: 20px; color:#000000; margin:4px 0px;", 
                      hover_after_color="font-size: 20px; color:#ffffff; margin:4px 0px;")
button6 = HoverButton("Button 6", initial_color="font-size: 20px; color:#ffffff; margin:4px 0px;", 
                      hover_color="font-size: 20px; color:#000000; margin:4px 0px;", 
                      hover_after_color="font-size: 20px; color:#ffffff; margin:4px 0px;")
frame2_layout.addWidget(button4)
frame2_layout.addWidget(button5)
frame2_layout.addWidget(button6)
frame2.setLayout(frame2_layout)


main_layout.addWidget(frame1)
main_layout.addWidget(frame2)


window.setLayout(main_layout)


# Show the window
window.show()

# Run the application event loop
app.exec()
