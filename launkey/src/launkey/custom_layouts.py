from PySide6.QtWidgets import QGridLayout, QWidget, QPushButton, QSizePolicy, QSpacerItem
from PySide6.QtCore import Qt, QSize

from .custom_widgets import PlusButton, SquareButton

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
        self.setObjectName("gridLayout")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.rows = 3
        self.cols = 3
        self.mainWidget = mainWidget
        self.mainWidgetLocation = (1, 1) # default on 3x3
        super().addWidget(self.mainWidget, *self.mainWidgetLocation, Qt.AlignmentFlag.AlignCenter)

        self.otherWidgets: list[tuple[QWidget, tuple[int, int]]] = []  # (widget, (x, y))
        self.plusButtonWidgets: list[tuple[QPushButton, tuple[int, int]]] = []  # (button, (x, y))
        self.update_layout()

    def addWidget(self, widget: QWidget, x: int, y: int):
        if (x, y) == self.mainWidgetLocation:
            raise ValueError("Cannot add widget at the main widget location.")

        super().addWidget(widget, x, y, Qt.AlignmentFlag.AlignCenter)
        self.otherWidgets.append((widget, (x, y)))
        self.update_layout()

    def update_layout(self):
        if self.mainWidget is None:
            return
        self.stretchToFill()
        self.autoAddPlusButtons()

    def autoAddPlusButtons(self):
        widgetsList: list[tuple[QWidget, tuple[int, int]]] = [
            (self.mainWidget, self.mainWidgetLocation)
        ] + self.otherWidgets

        for widget, (x, y) in widgetsList:
            # add buttons to 8 places around widget
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    if self.checkIfOutOfBounds(x + dx, y + dy):
                        print(f"Out of bounds: {(x + dx, y + dy)}")
                        continue
                    if self.checkIfEmpty(x + dx, y + dy):
                        plusButton = PlusButton(self.parentWidget())
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

        newActionButton = SquareButton(f"Action{btnNumber}", self.parentWidget())
        newActionButton.setObjectName(f"newActionButton{btnNumber}")
        newActionButton.setText(f"Action{btnNumber}")

        self.replaceWithWidget(button, newActionButton)
        self.update_layout()
        #self.growGridIfMinus(btnRelativePosition)

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

    def checkIfOutOfBounds(self, x: int, y: int) -> bool:
        return x < 0 or y < 0 or x >= self.cols or y >= self.rows

    def checkIfEmpty(self, x: int, y: int) -> bool:
        for widget, pos in self.otherWidgets + [(self.mainWidget, self.mainWidgetLocation)] + self.plusButtonWidgets:
            if pos[0] == x and pos[1] == y:
                return False
        return True

    def stretchToFill(self):
        for i in range(self.cols):
            self.setColumnStretch(i, 1)
        for i in range(self.rows):
            self.setRowStretch(i, 1)