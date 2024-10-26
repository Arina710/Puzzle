import sys
import time
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QScrollArea, QHBoxLayout, QFrame, \
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


class PuzzleScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.scroll_area_content = QWidget(self)
        self.setWidget(self.scroll_area_content)
        self.scroll_layout = QHBoxLayout(self.scroll_area_content)
        self.scroll_area_content.setLayout(self.scroll_layout)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setFixedHeight(100)

    def add_piece(self, piece):
        self.scroll_layout.addWidget(piece)

    def reset(self):
        for piece in self.findChildren(PuzzlePiece):
            piece.setParent(None)
            piece.deleteLater()
        self.scroll_layout.update()


class PuzzleControls(QFrame):
    def __init__(self, puzzle_game, parent=None):
        super().__init__(parent)
        self.puzzle_game = puzzle_game
        self.initUI()

    def initUI(self):
        button_layout = QHBoxLayout(self)

        exit_button = QPushButton("Выход")
        exit_button.setStyleSheet("background-color: #e74c3c; color: white;")
        exit_button.clicked.connect(self.puzzle_game.close_application)

        menu_button = QPushButton("Меню")
        menu_button.setStyleSheet("background-color: #3498db; color: white;")
        menu_button.clicked.connect(self.puzzle_game.show_main_menu)

        restart_button = QPushButton("Перезапустить")
        restart_button.setStyleSheet("background-color: #f39c12; color: white;")
        restart_button.clicked.connect(self.puzzle_game.shuffle_puzzle_pieces)

        button_layout.addWidget(exit_button)
        button_layout.addWidget(menu_button)
        button_layout.addWidget(restart_button)

        self.setLayout(button_layout)


class MainMenu(QFrame):
    def __init__(self, puzzle_game, parent=None):
        super().__init__(parent)
        self.puzzle_game = puzzle_game
        self.initUI()

    def initUI(self):
        button_layout = QVBoxLayout(self)

        play_button = QPushButton("Играть")
        play_button.setStyleSheet("background-color: #2ecc71; color: white;")
        play_button.clicked.connect(self.puzzle_game.start_game)
        button_layout.addWidget(play_button)

        select_image_button = QPushButton("Выбрать изображение")
        select_image_button.setStyleSheet("background-color: #9b59b6; color: white;")
        select_image_button.clicked.connect(self.puzzle_game.select_image)
        button_layout.addWidget(select_image_button)

        self.setLayout(button_layout)


class PuzzleArea(QFrame):
    def __init__(self, puzzle_game, check_solution_callback, parent=None):
        super().__init__(parent)
        self.puzzle_game = puzzle_game
        self.check_solution_callback = check_solution_callback
        self.setAcceptDrops(True)
        self.grid_size = 3
        self.piece_positions = {}
        self.setStyleSheet("background-color: #f0f0f0;")
        self.setFixedSize(1000, 600)

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

                new_x = cell_column * piece_width
                new_y = cell_row * piece_height

                current_pos = self.get_piece_position(piece_widget)

                if (cell_column, cell_row) in self.piece_positions:
                    existing_piece_number = self.piece_positions[(cell_column, cell_row)]
                    existing_piece = self.find_piece_by_number(existing_piece_number)

                    if existing_piece and current_pos:
                        self.piece_positions[(cell_column, cell_row)] = piece_widget.piece_number
                        self.piece_positions[current_pos] = existing_piece.piece_number

                        existing_piece.setParent(self)
                        existing_piece.setFixedSize(piece_width, piece_height)
                        existing_piece.move(current_pos[0] * piece_width, current_pos[1] * piece_height)
                        existing_piece.show()

                else:
                    if current_pos:
                        self.piece_positions.pop(current_pos)
                    self.piece_positions[(cell_column, cell_row)] = piece_widget.piece_number

                piece_widget.setParent(self)
                piece_widget.setFixedSize(piece_width, piece_height)
                piece_widget.move(new_x, new_y)
                piece_widget.show()

                event.acceptProposedAction()

                if self.check_puzzle_completion() and len(self.piece_positions) == 9:
                    self.check_solution_callback()

    def get_piece_position(self, piece):
        for position, number in self.piece_positions.items():
            if number == piece.piece_number:
                return position
        return None

    def find_piece_by_number(self, piece_number):
        for piece in self.findChildren(PuzzlePiece):
            if piece.piece_number == piece_number:
                return piece
        return None

    def check_puzzle_completion(self):
        for (column, row), piece_number in self.piece_positions.items():
            expected_piece_number = row * self.grid_size + column
            if piece_number != expected_piece_number:
                return False
        return True

    def reset(self):
        self.piece_positions.clear()
        for piece in self.findChildren(PuzzlePiece):
            piece.setParent(None)
            piece.deleteLater()
        self.update()


class PuzzleGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon('puzzle.ico'))
        super().__init__()
        self.setFixedSize(900, 900)
        self.original_image = QImage('hen.png')
        self.original_pixmap = QPixmap.fromImage(self.original_image)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.time_elapsed = 0
        self.timer_label = QLabel("00:00")
        self.start_time = None
        self.is_running = False
        self.pieces_created = False
        self.puzzle_solved = False

        self.initUI()

    def initUI(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon('puzzle.ico'))
        self.setWindowTitle("Пазлы")
        self.setStyleSheet("background-color: #ffffff;")

        self.layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget(self)
        self.layout.addWidget(self.tab_widget)

        self.tab_widget.tabBar().setVisible(False)

        self.timer_label.setFont(QFont("Arial", 16))
        self.timer_label.setStyleSheet("padding: 10px;")
        self.layout.addWidget(self.timer_label)

        self.controls = PuzzleControls(self)
        self.layout.addWidget(self.controls)

        self.main_menu = MainMenu(self)
        self.tab_widget.addTab(self.main_menu, "Главное меню")

        self.puzzle_area = PuzzleArea(self, self.check_if_puzzle_solved)
        self.tab_widget.addTab(self.puzzle_area, "Пазлы")

        self.scroll_area = PuzzleScrollArea(self)
        self.scroll_area.setVisible(False)
        self.layout.addWidget(self.scroll_area)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close_application()

    def switch_to_puzzles_tab(self):
        self.tab_widget.setCurrentIndex(1)
        self.start_timer()
        self.scroll_area.setVisible(True)
        if not self.pieces_created:
            self.create_puzzle_pieces()

    def select_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "",
                                                   "Images (*.png *.jpg *.jpeg);;All Files (*)", options=options)
        if file_name:
            self.original_image.load(file_name)
            self.original_pixmap = QPixmap.fromImage(self.original_image)
            self.reset_game()

    def reset_game(self):
        self.puzzle_area.reset()
        self.scroll_area.reset()

        if self.is_running:
            self.timer.stop()
            self.is_running = False

        self.time_elapsed = 0
        self.timer_label.setText("00:00")

        self.create_puzzle_pieces()
        self.puzzle_solved = False
        self.start_timer()

    def shuffle_puzzle_pieces(self):
        self.puzzle_area.reset()
        self.scroll_area.reset()

        if self.is_running:
            self.timer.stop()
            self.is_running = False

        self.time_elapsed = 0
        self.timer_label.setText("00:00")

        self.create_puzzle_pieces()
        self.puzzle_solved = False
        self.start_timer()

    def create_puzzle_pieces(self):
        pieces = []
        for i in range(9):
            piece_number = i
            x = (i % 3) * (self.original_pixmap.width() // 3)
            y = (i // 3) * (self.original_pixmap.height() // 3)
            pixmap = self.original_pixmap.copy(x, y, self.original_pixmap.width() // 3,
                                               self.original_pixmap.height() // 3)
            piece = PuzzlePiece(pixmap, piece_number, self.scroll_area)
            pieces.append(piece)

        shuffle(pieces)
        for piece in pieces:
            self.scroll_area.add_piece(piece)

        self.pieces_created = True

    def start_game(self):
        self.main_menu.hide()
        self.puzzle_area.show()
        self.switch_to_puzzles_tab()
        self.layout.addWidget(self.scroll_area)
        self.scroll_area.setVisible(True)

        if self.is_running:
            self.timer.stop()
            self.is_running = False

        self.time_elapsed = 0
        self.timer_label.setText("00:00")
        self.puzzle_area.reset()
        self.scroll_area.reset()
        self.create_puzzle_pieces()
        self.puzzle_solved = False
        self.start_timer()

    def close_application(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon('remove.ico'))
        choice = QMessageBox.question(self, "Выход", "Вы действительно хотите выйти?", QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            sys.exit()

    def update_timer(self):
        self.time_elapsed += 1
        minutes = self.time_elapsed // 60
        seconds = self.time_elapsed % 60
        self.timer_label.setText(f"{minutes:02}:{seconds:02}")

    def start_timer(self):
        if not self.is_running:
            self.start_time = time.time()
            self.timer.start(1000)
            self.is_running = True

    def show_success_message(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon('check.ico'))
        elapsed_time = self.time_elapsed
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        time_string = f"{minutes:02}:{seconds:02}"

        success_message = QMessageBox(self)
        success_message.setWindowTitle("Успех!")
        success_message.setText(f"Паззл собран! Ваше время: {time_string}")
        success_message.setIcon(QMessageBox.Information)

        menu_button = success_message.addButton("Выход в меню", QMessageBox.ActionRole)
        restart_button = success_message.addButton("Перезапуск", QMessageBox.ActionRole)

        success_message.exec_()

        if success_message.clickedButton() == menu_button:
            self.show_main_menu()
        elif success_message.clickedButton() == restart_button:
            self.reset_game()

    def check_if_puzzle_solved(self):
        if self.puzzle_area.check_puzzle_completion() and len(self.puzzle_area.piece_positions) == 9:
            self.timer.stop()
            self.show_success_message()
            self.puzzle_solved = True

    def show_main_menu(self):
        self.timer.stop()
        self.time_elapsed = 0
        self.timer_label.setText("00:00")
        self.puzzle_area.hide()
        self.main_menu.show()
        self.scroll_area.setVisible(False)
        self.puzzle_area.piece_positions.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = PuzzleGame()
    game.show()
    sys.exit(app.exec_())
