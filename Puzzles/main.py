import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QScrollArea, QHBoxLayout, QFrame, \
    QTabWidget, QPushButton
from PyQt5.QtGui import QPixmap, QPainter, QColor, QDrag, QImage
from PyQt5.QtCore import Qt, QMimeData, QRect

class PuzzlePiece(QLabel):
    def __init__(self, pixmap, piece_number, parent=None):
        super().__init__(parent)
        self.setPixmap(pixmap)
        self.piece_number = piece_number
        self.setScaledContents(True)
        self.setFixedSize(80, 80)  # Size of the puzzle piece
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

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            piece_number = int(event.mimeData().text())
            piece_widget = event.source()

            if piece_widget:
                if isinstance(piece_widget, PuzzlePiece):
                    if piece_widget.piece_number != self.piece_number:
                        pixmap = piece_widget.pixmap()
                        self.setPixmap(pixmap)
                        self.piece_number = piece_widget.piece_number
                        self.show()

class PuzzleArea(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: white;")
        self.setFixedHeight(600)  # Set the height of the assembly area
        self.setAcceptDrops(True)

    def paintEvent(self, event):
        painter = QPainter(self)
        self.draw_piece_outlines(painter)

    def draw_piece_outlines(self, painter):
        grid_size = 3
        piece_width = self.width() // grid_size
        piece_height = self.height() // grid_size

        painter.setPen(QColor(155, 0, 0))
        for i in range(grid_size):
            for j in range(grid_size):
                rect = QRect(i * piece_width, j * piece_height, piece_width, piece_height)
                painter.drawRect(rect)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            piece_number = int(event.mimeData().text())
            piece_widget = self.parent().findChild(PuzzlePiece, str(piece_number))
            if piece_widget:
                grid_size = 3
                piece_width = self.width() // grid_size
                piece_height = self.height() // grid_size

                # Определение ячейки сетки, куда был отпущен пазл
                drop_position = event.pos()
                cell_column = min(drop_position.x() // piece_width, grid_size - 1)
                cell_row = min(drop_position.y() // piece_height, grid_size - 1)

                # Перемещение пазла в соответствующую ячейку сетки
                piece_widget.setParent(self)
                piece_widget.move(cell_column * piece_width, cell_row * piece_height)
                piece_widget.show()

                self.parent().scroll_area_content.layout().removeWidget(piece_widget)
                piece_widget.hide()  # Скрытие пазла в области прокрутки


class PuzzleGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Puzzle Game")
        self.setGeometry(100, 100, 900, 800)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        # Create Initial Window Widget
        initial_widget = QWidget()
        initial_layout = QVBoxLayout(initial_widget)
        play_button = QPushButton("Play")
        play_button.clicked.connect(self.switch_to_puzzles_tab)
        initial_layout.addWidget(play_button)
        self.tab_widget.addTab(initial_widget, "Start Playing")

        self.original_image = QImage('hen.png')
        self.original_pixmap = QPixmap.fromImage(self.original_image)

        self.puzzle_area = PuzzleArea(self)
        self.tab_widget.addTab(self.puzzle_area, "Puzzles")

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)

        self.scroll_area_content = QWidget()
        self.scroll_area.setWidget(self.scroll_area_content)
        self.scroll_layout = QHBoxLayout(self.scroll_area_content)

        self.create_puzzle_pieces()

        self.scroll_area_content.setLayout(self.scroll_layout)

    def switch_to_puzzles_tab(self):
        self.tab_widget.setCurrentIndex(1)  # Switch to the Puzzles tab

    def create_puzzle_pieces(self):
        grid_size = 3  # Grid size (3x3)
        piece_width = self.original_pixmap.width() // grid_size
        piece_height = self.original_pixmap.height() // grid_size

        for i in range(grid_size):
            for j in range(grid_size):
                rect = QRect(i * piece_width, j * piece_height, piece_width, piece_height)
                piece_image = self.original_image.copy(rect)

                piece_pixmap = QPixmap.fromImage(piece_image)
                piece = PuzzlePiece(piece_pixmap, i * grid_size + j, self)
                self.scroll_layout.addWidget(piece)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PuzzleGame()
    window.show()
    sys.exit(app.exec_())