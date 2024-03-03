import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 300, 220)
        self.setWindowTitle('MyApp')

        btn = QPushButton('Click me', self)
        btn.move(50, 50)
        btn.clicked.connect(self.on_click)

    def on_click(self):
        print('Button clicked')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())

