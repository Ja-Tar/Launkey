from PySide6.QtWidgets import QGridLayout, QWidget, QPushButton, QSizePolicy
from PySide6.QtCore import Qt, QSize

# From https://github.com/chinmaykrishnroy/PyQt5DynamicFlowLayout
class DynamicGridLayout(QGridLayout):
    def __init__(self, parent=None, min_col_width=360, min_row_height=116):
        super().__init__(parent)
        self.min_col_width = min_col_width
        self.min_row_height = min_row_height
        self.items = []
        self.num_cols = 0
        # Dodaj filtr zdarzeń do rodzica, jeśli istnieje
        if parent is not None:
            parent.installEventFilter(self)

    def eventFilter(self, obj, event):
        from PySide6.QtCore import QEvent
        if obj is self.parentWidget() and event.type() == QEvent.Resize: # type: ignore
            self.update_layout()
        return super().eventFilter(obj, event)

    def addWidget(self, widget, rowSpan=1, colSpan=1, alignment=None):
        item = (widget, rowSpan, colSpan, alignment)
        self.items.append(item)
        super().addWidget(widget, 0, 0, rowSpan, colSpan)
        self.update_layout()

    def update_layout(self):
        if not self.parentWidget():
            return

        width = self.parentWidget().width()
        new_num_cols = max(1, width // self.min_col_width)
        item_width = width // new_num_cols

        if new_num_cols != self.num_cols:
            self.num_cols = new_num_cols

        row = col = 0
        for widget, rowSpan, colSpan, alignment in self.items:
            widget.setFixedHeight(item_width * self.min_row_height // self.min_col_width)
            super().addWidget(widget, row, col, rowSpan, colSpan)
            col += 1
            if col >= self.num_cols:
                col = 0
                row += 1

class CenterGridLayout(QGridLayout):
    def __init__(self, mainWidget: QWidget, parent = None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)

        self.rows = 3
        self.cols = 3
        self.mainWidget = mainWidget
        self.mainWidgetLocation = (1, 1) # default on 3x3
        super().addWidget(self.mainWidget, *self.mainWidgetLocation)
        self.setMinimumCellSize(self._minCellSize())

        self.otherWidgets: list[tuple[QWidget, int, int]] = []  # (widget, x, y)
        self.plusButtonWidgets: list[tuple[QPushButton, int, int]] = []  # (widget, x, y)
        self.autoAddPlusButtons()
    
    def heightForWidth(self, arg__1: int) -> int:
        height = arg__1
        return height

    def hasHeightForWidth(self) -> bool:
        return True

    def addWidget(self, widget: QWidget, x: int, y: int):
        if (x, y) == self.mainWidgetLocation:
            raise ValueError("Cannot add widget at the main widget location.")
        
        self.otherWidgets.append((widget, x, y))
        self.update_layout()

    def clear(self):
        self.otherWidgets = []
        self.plusButtonWidgets = []
        self.update_layout()

    def update_layout(self):
        if self.mainWidget is None and not self.otherWidgets:
            return

        self.setMinimumCellSize(self._minCellSize())

    def autoAddPlusButtons(self):
        widgetsList: list[tuple[QWidget, int, int]] = [
            (self.mainWidget, *self.mainWidgetLocation)
        ] + self.otherWidgets

        buttonsSizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        for widget, x, y in widgetsList:
            # add buttons to 8 places around widget
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    if self.checkCellIfEmpty(x + dx, y + dy):
                        plusButton = QPushButton("+", self.parentWidget())
                        plusButton.setSizePolicy(buttonsSizePolicy)
                        dynamicSize = self._minCellSize()
                        plusButton.setMinimumSize(QSize(50, 50))
                        plusButton.setMaximumSize(dynamicSize.width() // 4, dynamicSize.height() // 4)
                        self.plusButtonWidgets.append((plusButton, x + dx, y + dy))
                        super().addWidget(plusButton, x + dx, y + dy, Qt.AlignmentFlag.AlignCenter)

    def checkCellIfEmpty(self, x: int, y: int) -> bool:
        for widget, posX, posY in self.otherWidgets + [(self.mainWidget, *self.mainWidgetLocation)] + self.plusButtonWidgets:
            if posX == x and posY == y:
                return False
        return True

    def _minCellSize(self):
        currentSize = self.parentWidget().size() if self.parentWidget() else QSize(800, 600)
        squareSize = min(currentSize.width() // self.cols, currentSize.height() // self.rows)
        return QSize(squareSize, squareSize)
    
    def setMinimumCellSize(self, cellSize: QSize):
        print("minimum cell size:", cellSize)
        for i in range(self.cols):
            self.setColumnMinimumWidth(i, cellSize.width())
        for i in range(self.rows):
            self.setRowMinimumHeight(i, cellSize.height())
