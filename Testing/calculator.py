import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QGridLayout

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Calculator')
        self.setGeometry(100, 100, 300, 400)

        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)

        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setFixedHeight(50)
        self.vbox.addWidget(self.display)

        self.buttons = QGridLayout()
        self.vbox.addLayout(self.buttons)

        button_labels = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+'
        ]

        row = 0
        col = 0
        for label in button_labels:
            button = QPushButton(label)
            button.setFixedHeight(60)
            button.clicked.connect(self.on_button_click)
            self.buttons.addWidget(button, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

        self.current_expression = ""

    def on_button_click(self):
        button = self.sender()
        text = button.text()

        if text == "=":
            try:
                result = str(eval(self.current_expression))
                self.display.setText(result)
                self.current_expression = result
            except Exception as e:
                self.display.setText("Error")
                self.current_expression = ""
        else:
            self.current_expression += text
            self.display.setText(self.current_expression)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec_())
