import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QScrollArea, QHBoxLayout, QFrame, \
    QTabWidget, QPushButton, QMessageBox, QFileDialog
from PyQt5.QtGui import QPixmap, QPainter, QColor, QDrag, QImage, QFont
from PyQt5.QtCore import Qt, QMimeData, QRect, QTimer
from random import shuffle


class PuzzlePiece(QLabel):
    def __init__(self, pixmap, piece_number, parent=None):
        super().__init__(parent)
        self.setPixmap(pixmap)
        self.piece_number = piece_number
        self.setScaledContents(True)
        self.setFixedSize(100, 80)
        self.setAcceptDrops(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            mime_data = QMimeData()
            mime_data.setText(str(self.piece_number))
            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.setPixmap(self.pixmap())
            drag.setHotSpot(event.pos())
            drag.exec_(Qt.MoveAction)


class PuzzleArea(QFrame):
    def __init__(self, puzzle_game, check_solution_callback, parent=None):
        super().__init__(parent)
        self.puzzle_game = puzzle_game
        self.check_solution_callback = check_solution_callback
        self.setAcceptDrops(True)
        self.grid_size = 3
        self.piece_positions = {}

        # Установка стиля и размеров
        self.setStyleSheet("background-color: #f0f0f0;")  # Light gray background
        self.setMinimumSize(600, 600)

    def paintEvent(self, event):
        painter = QPainter(self)
        self.draw_piece_outlines(painter)

    def draw_piece_outlines(self, painter):
        piece_width = self.width() // self.grid_size
        piece_height = self.height() // self.grid_size
        painter.setPen(QColor(155, 0, 0))
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                rect = QRect(i * piece_width, j * piece_height, piece_width, piece_height)
                painter.drawRect(rect)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            piece_widget = event.source()
            if piece_widget and isinstance(piece_widget, PuzzlePiece):
                grid_size = self.grid_size
                piece_width = self.width() // grid_size
                piece_height = self.height() // grid_size
                drop_position = event.pos()
                cell_column = min(drop_position.x() // piece_width, grid_size - 1)
                cell_row = min(drop_position.y() // piece_height, grid_size - 1)

                if (cell_column, cell_row) not in self.piece_positions:
                    new_x = cell_column * piece_width
                    new_y = cell_row * piece_height
                    piece_widget.setFixedSize(piece_width, piece_height)
                    piece_widget.setParent(self)
                    piece_widget.move(new_x, new_y)
                    piece_widget.show()
                    self.piece_positions[(cell_column, cell_row)] = piece_widget.piece_number

                    event.acceptProposedAction()
                    self.check_solution_callback()

    def check_puzzle_completion(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                piece_number = i * self.grid_size + j
                if self.piece_positions.get((i, j)) != piece_number:
                    return False
        return True

    def reset(self):
        self.piece_positions.clear()
        self.update()


class PuzzleGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1000, 850)
        self.elapsed_time = 0
        self.original_image = QImage('hen.png')
        self.original_pixmap = QPixmap.fromImage(self.original_image)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.time_elapsed = 0
        self.timer_label = QLabel("00:00")
        self.start_timer()
        self.start_time = None
        self.is_running = False
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Puzzle Game")
        self.setStyleSheet("background-color: #ffffff;")  # White background for the main window

        self.layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget(self)
        self.layout.addWidget(self.tab_widget)

        # Таймер
        self.timer_label.setFont(QFont("Arial", 16))
        self.timer_label.setStyleSheet("padding: 10px;")  # Padding for aesthetics
        self.layout.addWidget(self.timer_label)

        # Кнопки управления
        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)

        exit_button = QPushButton("Выход")
        exit_button.setStyleSheet("background-color: #e74c3c; color: white;")  # Red color
        exit_button.clicked.connect(self.close_application)

        menu_button = QPushButton("Меню")
        menu_button.setStyleSheet("background-color: #3498db; color: white;")  # Blue color
        menu_button.clicked.connect(self.switch_to_initial_tab)

        restart_button = QPushButton("Перезапустить")
        restart_button.setStyleSheet("background-color: #f39c12; color: white;")  # Orange color
        restart_button.clicked.connect(self.reset_game)

        # Добавляем кнопки в компоновку
        self.button_layout.addWidget(exit_button)
        self.button_layout.addWidget(menu_button)
        self.button_layout.addWidget(restart_button)

        # Инициализация кнопок
        play_button = QPushButton("Играть")
        play_button.setStyleSheet("background-color: #2ecc71; color: white;")  # Green color
        play_button.clicked.connect(self.start_game)

        select_image_button = QPushButton("Выбрать изображение")
        select_image_button.setStyleSheet("background-color: #9b59b6; color: white;")  # Purple color
        select_image_button.clicked.connect(self.select_image)

        # Добавление кнопок в начальный экран
        initial_layout = QVBoxLayout()
        initial_layout.addWidget(play_button)
        initial_layout.addWidget(select_image_button)

        initial_widget = QWidget()
        initial_widget.setLayout(initial_layout)
        self.tab_widget.addTab(initial_widget, "Начать игру")

        # Исходное изображение
        self.original_image = QImage('hen.png')
        self.original_pixmap = QPixmap.fromImage(self.original_image)

        self.puzzle_area = PuzzleArea(self, self.check_if_puzzle_solved)
        self.tab_widget.addTab(self.puzzle_area, "Пазлы")

        # Настройка области прокрутки
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)

        self.scroll_area_content = QWidget()
        self.scroll_area.setWidget(self.scroll_area_content)

        self.scroll_layout = QHBoxLayout(self.scroll_area_content)
        self.create_puzzle_pieces()
        self.scroll_area_content.setLayout(self.scroll_layout)

    def switch_to_puzzles_tab(self):
        self.tab_widget.setCurrentIndex(1)
        self.start_timer()

    def select_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "",
                                                   "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)", options=options)
        if file_name:
            self.original_image = QImage(file_name)
            self.original_pixmap = QPixmap.fromImage(self.original_image)
            self.puzzle_area.update()
            self.create_puzzle_pieces()

    def reset_game(self):
        self.start_time = None
        self.is_running = False
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        self.reset_timer()
        self.puzzle_area.reset()
        self.create_puzzle_pieces()
        self.start_timer()

    def close_application(self):
        sys.exit()

    def create_puzzle_pieces(self):
        while self.scroll_layout.count() > 0:
            item = self.scroll_layout.itemAt(0)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                self.scroll_layout.removeItem(item)

        grid_size = 3
        piece_width = self.original_pixmap.width() // grid_size
        piece_height = self.original_pixmap.height() // grid_size
        pieces = []
        for i in range(grid_size):
            for j in range(grid_size):
                rect = QRect(i * piece_width, j * piece_height, piece_width, piece_height)
                piece_image = self.original_image.copy(rect)
                piece_pixmap = QPixmap.fromImage(piece_image)
                piece = PuzzlePiece(piece_pixmap, i * grid_size + j, self)
                pieces.append(piece)
        shuffle(pieces)
        for piece in pieces:
            self.scroll_layout.addWidget(piece)

    def start_game(self):
        self.is_running = True
        self.switch_to_puzzles_tab()
        self.start_time = time.time()

    def start_timer(self):
        self.timer.start(1000)

    def update_timer(self):
        self.time_elapsed += 1
        minutes, seconds = divmod(self.time_elapsed, 60)
        self.timer_label.setText(f"{minutes:02}:{seconds:02}")

    def reset_timer(self):
        self.time_elapsed = 0
        self.timer_label.setText("00:00")

    def check_if_puzzle_solved(self):
        if self.puzzle_area.check_puzzle_completion():
            self.show_success_message()

    def show_success_message(self):
        self.timer.stop()
        elapsed_time = time.time() - self.start_time
        minutes, seconds = divmod(int(elapsed_time), 60)
        message = f"Пазл собран! Ваше время: {minutes:02}:{seconds:02}"

        success_message_box = QMessageBox()
        success_message_box.setWindowTitle("Успех!")
        success_message_box.setText(message)

        menu_button = success_message_box.addButton("Выход в меню", QMessageBox.ActionRole)
        restart_button = success_message_box.addButton("Перезапустить", QMessageBox.ActionRole)
        success_message_box.exec_()

        clicked_button = success_message_box.clickedButton()
        if clicked_button == menu_button:
            self.switch_to_initial_tab()
        elif clicked_button == restart_button:
            self.reset_game()

        self.reset_timer()

    def switch_to_initial_tab(self):
        self.tab_widget.setCurrentIndex(0)
        self.reset_game()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = PuzzleGame()
    game.show()
    sys.exit(app.exec_())
