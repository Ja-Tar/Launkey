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

        self.otherWidgets: list[tuple[QWidget, tuple[int, int]]] = []  # (widget, (x, y))
        self.plusButtonWidgets: list[tuple[QPushButton, tuple[int, int]]] = []  # (button, (x, y))
        self.autoAddPlusButtons()
    
    def heightForWidth(self, arg__1: int) -> int:
        height = arg__1
        return height

    def hasHeightForWidth(self) -> bool:
        return True

    def addWidget(self, widget: QWidget, x: int, y: int):
        if (x, y) == self.mainWidgetLocation:
            raise ValueError("Cannot add widget at the main widget location.")
        
        super().addWidget(widget, x, y)
        self.otherWidgets.append((widget, (x, y)))
        self.update_layout()

    def clear(self):
        self.otherWidgets = []
        self.clearPlusButtons()
        self.update_layout()

    def update_layout(self):
        if self.mainWidget is None:
            return

        self.setMinimumCellSize(self._minCellSize())
        self.moveAllWidgets()
        self.autoAddPlusButtons()

    def moveAllWidgets(self):
        for widget, (x, y) in self.otherWidgets + self.plusButtonWidgets + [(self.mainWidget, self.mainWidgetLocation)]:
            self.removeWidget(widget)
            super().addWidget(widget, x, y)

    def autoAddPlusButtons(self):
        widgetsList: list[tuple[QWidget, tuple[int, int]]] = [
            (self.mainWidget, self.mainWidgetLocation)
        ] + self.otherWidgets

        buttonsSizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        for widget, (x, y) in widgetsList:
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
                        plusButton.clicked.connect(lambda _, btn=plusButton: self._plusButtonAction(btn))
                        self.plusButtonWidgets.append((plusButton, (x + dx, y + dy)))
                        super().addWidget(plusButton, x + dx, y + dy, Qt.AlignmentFlag.AlignCenter)

    def clearPlusButtons(self):
        for button, _ in self.plusButtonWidgets:
            super().removeWidget(button)
            button.deleteLater()
        self.plusButtonWidgets = []

    def _plusButtonAction(self, button: QPushButton, ):
        # After clicking the button, add new element (big Button), and check if it's on edge
        # then grow the grid in the desired direction
        btnRelativePosition = self.getRelativePosition(button)
        btnNumber = len(self.otherWidgets) + 1

        newActionButton = QPushButton(self.parentWidget())
        newActionButton.setObjectName(f"newActionButton{btnNumber}")
        newActionButton.setText(f"Action{btnNumber}")
        newActionPolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        newActionButton.setSizePolicy(newActionPolicy)

        self.replaceWithWidget(button, newActionButton)
        self.growGridIfMinus(btnRelativePosition)

    def growGridIfMinus(self, direction: tuple[int, int]):
        # Grow the grid in the negative direction
        if direction[0] < 0:
            self.mainWidgetLocation = (self.mainWidgetLocation[0] + 1, self.mainWidgetLocation[1])
            self.otherWidgets = [(w, (wx + 1, wy)) for w, (wx, wy) in self.otherWidgets]
        elif direction[1] < 0:
            self.mainWidgetLocation = (self.mainWidgetLocation[0], self.mainWidgetLocation[1] + 1)
            self.otherWidgets = [(w, (wx, wy + 1)) for w, (wx, wy) in self.otherWidgets]

        self.update_layout()

    def replaceWithWidget(self, oldWidget: QWidget, newWidget: QWidget):
        oldWidgetPos = self.getPosition(oldWidget)
        self.otherWidgets = [w for w in self.otherWidgets if w[0] != oldWidget]
        self.plusButtonWidgets = [w for w in self.plusButtonWidgets if w[0] != oldWidget]
        oldWidget.deleteLater()
        self.addWidget(newWidget, *oldWidgetPos)

    def getPosition(self, widget: QWidget) -> tuple[int, int]:
        for w, pos in self.otherWidgets + [(self.mainWidget, self.mainWidgetLocation)] + self.plusButtonWidgets:
            if w == widget:
                return pos
        return (0, 0)

    def getRelativePosition(self, widget: QWidget) -> tuple[int, int]:
        # this is relative to the main widget
        if widget == self.mainWidget:
            return (0, 0)

        for w, (x, y) in self.otherWidgets + self.plusButtonWidgets:
            if w == widget:
                return (x - self.mainWidgetLocation[0], y - self.mainWidgetLocation[1])

        return (0, 0)

    def checkCellIfEmpty(self, x: int, y: int) -> bool:
        for widget, pos in self.otherWidgets + [(self.mainWidget, self.mainWidgetLocation)] + self.plusButtonWidgets:
            if pos[0] == x and pos[1] == y:
                return False
        return True

    def _minCellSize(self):
        currentSize = self.parentWidget().size() if self.parentWidget() else QSize(800, 600)
        squareSize = min(currentSize.width() // self.cols, currentSize.height() // self.rows)
        return QSize(squareSize, squareSize)
    
    def setMinimumCellSize(self, cellSize: QSize):
        for i in range(self.cols):
            self.setColumnMinimumWidth(i, cellSize.width())
        for i in range(self.rows):
            self.setRowMinimumHeight(i, cellSize.height())
