from PySide2.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget, QPushButton, QVBoxLayout, QScrollArea
from PySide2.QtGui import QPixmap, QFont, QPainter
from PySide2.QtCore import Qt
import ast
import sys

def parse_file(filepath):
    all_arrays = []
    with open(filepath, 'r') as file:
        for line in file:
            array_2d = ast.literal_eval(line.strip())
            all_arrays.append(array_2d)
    return all_arrays

def get_color_code(letter):
    return {
        'R': 'black',
        'P': 'green',
        'F': 'gray',
        'M': 'purple',
        'H': 'white'
    }.get(letter, 'purple')

class TileLabel(QLabel):
    def __init__(self, parent=None):
        super(TileLabel, self).__init__(parent)
        self.text_above_image = ""
        self.image = None  # Initialize with None, check before use
        self.special_mode = False

    def set_image(self, pixmap, special_mode=False):
        if pixmap is not None:  # Ensure pixmap is not None before setting
            self.image = pixmap
            self.special_mode = special_mode
            self.update()
        else:
            self.image = QPixmap()  # Set to an empty QPixmap if None is provided

    def set_text_above_image(self, text):
        self.text_above_image = text
        self.update()

    def paintEvent(self, event):
        super(TileLabel, self).paintEvent(event)
        painter = QPainter(self)
        if self.image and not self.image.isNull():  # Check if image is valid
            image_rect = self.image.rect()
            image_rect.moveCenter(self.rect().center())
            if self.special_mode:
                image_rect.moveTop(self.rect().center().y() / 2 - 35)
            else:
                image_rect.moveTop(self.rect().center().y() / 2 - 9)
            painter.drawPixmap(image_rect.topLeft(), self.image)
        if self.text_above_image:
            painter.setPen(Qt.red)
            painter.drawText(self.rect().adjusted(0, -40, 0, 0), Qt.AlignTop | Qt.AlignCenter, self.text_above_image)


class MainWindow(QMainWindow):
    def __init__(self, arrays):
        super(MainWindow, self).__init__()
        self.arrays = arrays
        self.current_index = 0  # Start at the first index
        self.tile_size = 50  # Size of each tile
        self.other_size = 110
        # Initialize images directly in the constructor before initUI
        self.treeImage = QPixmap("tree.png").scaled(self.tile_size, self.tile_size, Qt.KeepAspectRatio)
        self.factoryImage = QPixmap("factory.png").scaled(self.other_size, self.other_size, Qt.KeepAspectRatio)
        self.mallImage = QPixmap("mall.png").scaled(self.other_size, self.other_size, Qt.KeepAspectRatio)
        self.hyperloopImage = QPixmap("hyperloop.png").scaled(self.tile_size, self.tile_size, Qt.KeepAspectRatio)
        self.initUI()

    def initUI(self):
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        self.mainLayout = QVBoxLayout(centralWidget)
        self.saveButton = QPushButton("Save and Display Next Grid")
        self.saveButton.clicked.connect(self.saveAndDisplayNextGrid)
        self.mainLayout.addWidget(self.saveButton)
        self.gridLayout = QGridLayout()
        self.gridLayout.setSpacing(0)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridWidget = QWidget()
        self.gridWidget.setLayout(self.gridLayout)
        self.mainLayout.addWidget(self.gridWidget)
        # mainLayout = QVBoxLayout(self.centralWidget)

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.mainLayout.addWidget(self.scrollArea)
        self.scrollArea.setWidget(self.gridWidget)

        self.personImages = {
            'C': QPixmap("car.png").scaled(self.tile_size, self.tile_size, Qt.KeepAspectRatio),
            'B': QPixmap("bike.png").scaled(self.tile_size, self.tile_size, Qt.KeepAspectRatio),
            'P': QPixmap("person.png").scaled(self.tile_size, self.tile_size, Qt.KeepAspectRatio)
        }
        self.labels = [[TileLabel() for _ in range(100)] for _ in range(100)]
        for i in range(100):
            for j in range(100):
                label = self.labels[i][j]
                label.setFixedSize(self.tile_size, self.tile_size)
                label.setAutoFillBackground(True)
                self.gridLayout.addWidget(label, i, j)
        self.setWindowTitle('Tile-Based Grid Viewer')
        self.resize(self.tile_size * 100, self.tile_size * 100+1)

    def updateDisplay(self, index):
        array = self.arrays[index]
        for i, row in enumerate(array):
            for j, val in enumerate(row):
                label = self.labels[i][j]
                tile_color = get_color_code(val[0])
                label.setStyleSheet(f"background-color: {tile_color};")
                label.set_image(None)  # Clear any previous image
                label.set_text_above_image("")  # Clear any previous text
                if tile_color == 'green' and len(val) == 1:
                    label.set_image(self.treeImage)
                if tile_color == 'gray' and len(val) == 1:
                    label.set_image(self.factoryImage, special_mode=True)
                if tile_color == 'purple' and len(val) == 1:
                    label.set_image(self.mallImage, special_mode=True)
                if tile_color == 'white' and len(val) == 1:
                    label.set_image(self.hyperloopImage, special_mode=False)    
                elif len(val) > 1 and val[-1].isalpha():
                    person_id = val[1:-1]
                    person_type = val[-1]
                    person_image_path = "car.png" if person_type == 'C' else "bike.png" if person_type == 'B' else "person.png"
                    label.set_image(QPixmap(person_image_path).scaled(self.tile_size, self.tile_size, Qt.KeepAspectRatio))
                    label.set_text_above_image(person_id)


    def saveAndDisplayNextGrid(self):
        if self.current_index < len(self.arrays):
            self.updateDisplay(self.current_index)
            filepath = f'images/100x100_no_hyperloops/grid_snapshot_{self.current_index}.png'
            self.gridWidget.grab().save(filepath, 'PNG')
            print(f"Grid saved as {filepath}")
            self.current_index += 1  # Increment the index to display the next grid on the next button click
        else:
            print("No more grids to display.")
            self.current_index = 0  # Optionally reset to start again

if __name__ == "__main__":
    app = QApplication(sys.argv)
    arrays = parse_file('100x100_no_hyperloops.txt')
    mainWindow = MainWindow(arrays)
    mainWindow.show()
    sys.exit(app.exec_())
