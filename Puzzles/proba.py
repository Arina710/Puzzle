import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QScrollArea, QGridLayout, QPushButton, \
    QLabel, QHBoxLayout
from PyQt5.QtCore import QTimer


class PuzzleGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Пазлы")
        self.setGeometry(100, 100, 900, 800)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Секундомер
        self.timer_label = QLabel("00:00")
        layout.addWidget(self.timer_label)

        # Кнопки '1', '2', '3'
        buttons_layout = QHBoxLayout()
        button_1 = QPushButton("Выйти в главное меню")
        button_2 = QPushButton("Перезапустить")
        button_3 = QPushButton("Выход")
        buttons_layout.addWidget(button_1)
        buttons_layout.addWidget(button_2)
        buttons_layout.addWidget(button_3)
        layout.addLayout(buttons_layout)

        # Скроллбар с сеткой делений
        scroll_area = QScrollArea()
        grid_layout = QGridLayout()
        for i in range(5):  # Пример сетки 5x5
            for j in range(5):
                puzzle_piece = QLabel(f"Piece {i * 5 + j + 1}")
                grid_layout.addWidget(puzzle_piece, i, j)
        scroll_content = QWidget()
        scroll_content.setLayout(grid_layout)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        timer = QTimer(self)
        timer.timeout.connect(self.update_timer)
        self.total_seconds = 0
        timer.start(1000)  # Запускаем таймер каждую секунду

    def update_timer(self):
        self.total_seconds += 1
        minutes = self.total_seconds // 60
        seconds = self.total_seconds % 60
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PuzzleGame()
    window.show()
    sys.exit(app.exec_())



