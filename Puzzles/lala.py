import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QPushButton

class MenuProgram(QWidget):
    def show_completed_message(self):
        msg = QMessageBox()
        msg.setWindowTitle("Поздравляю")
        msg.setText("Пазл собран! Ваше время: 10:02")
        button1 = QPushButton('Выйти в главное меню')
        button2 = QPushButton('начать заново')
        msg.addButton(button1, QMessageBox.AcceptRole)
        msg.addButton(button2, QMessageBox.AcceptRole)
        msg.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    menu = MenuProgram()
    menu.show_completed_message()
    sys.exit(app.exec_())