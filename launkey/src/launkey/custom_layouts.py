from PySide6.QtWidgets import QGridLayout, QWidget, QPushButton
from PySide6.QtCore import Qt

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

        if obj is self.parentWidget() and event.type() == QEvent.Resize:  # type: ignore
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
        for widget, rowSpan, colSpan, _ in self.items:
            widget.setFixedHeight(
                item_width * self.min_row_height // self.min_col_width
            )
            super().addWidget(widget, row, col, rowSpan, colSpan)
            col += 1
            if col >= self.num_cols:
                col = 0
                row += 1


class CenterGridLayout(QGridLayout):
    def __init__(self, mainWidget: QWidget, parent=None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)
        self.setObjectName("gridLayout")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.rows = 3
        self.cols = 3
        self.mainWidget = mainWidget
        self.mainWidgetLocation = (1, 1)  # default on 3x3
        super().addWidget(self.mainWidget, *self.mainWidgetLocation, Qt.AlignmentFlag.AlignBaseline)

        self.otherWidgets: list[tuple[QWidget, tuple[int, int]]] = []  # (widget, (x, y))
        self.plusButtonWidgets: list[tuple[QWidget, tuple[int, int]]] = []  # (button, (x, y))
        self.updateLayout()

    def getAllWidgets(self) -> list[tuple[QWidget, tuple[int, int]]]:
        # Plus buttons are automatically generated so only main and other widgets are included
        return [(self.mainWidget, self.mainWidgetLocation)] + self.otherWidgets

    def addWidget(
        self,
        widget: QWidget,
        x: int,
        y: int,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignBaseline,
        addToList: list[tuple[QWidget, tuple[int, int]]] | None = None,
    ):
        if (x, y) == self.mainWidgetLocation:
            raise ValueError("Cannot add widget at the main widget location.")
        if addToList is None:
            addToList = self.otherWidgets
        if not self.checkIfEmpty(x, y):
            raise ValueError("Cannot add widget at occupied position.")

        if self.checkIfOutOfBounds(x, y):
            outOfBoundsDirection = self.outOfBoundsDirection(x, y)
            print(
                f"Widget {widget} is out of bounds at ({x}, {y}). Direction: {outOfBoundsDirection}"
            )
            # ADD MORE LOGIC HERE
            # ONLY HERE USE super().addWidget
        else:
            super().addWidget(widget, x, y, alignment=alignment)
            if addToList is not None:
                addToList.append((widget, (x, y)))

    def updateLayout(self):
        self.stretchToFill()
        self.autoAddPlusButtons()

    def autoAddPlusButtons(self):
        widgetsList = self.getAllWidgets()
        for _, (x, y) in widgetsList:
            # add buttons to 8 places around widget
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    plusButton = PlusButton()
                    plusButton.clicked.connect(
                        lambda _, btn=plusButton: self._plusButtonAction(btn)
                    )
                    try:
                        self.addWidget(
                            plusButton,
                            x + dx,
                            y + dy,
                            Qt.AlignmentFlag.AlignCenter,
                            self.plusButtonWidgets,
                        )
                    except ValueError:
                        continue

    def _plusButtonAction(self, button: QPushButton):
        btnNumber = len(self.otherWidgets) + 1
        newActionButton = SquareButton(f"Action{btnNumber}")
        newActionButton.setObjectName(f"newActionButton{btnNumber}")
        newActionButton.setText(f"Action{btnNumber}")
        self.replaceWidget(
            button, newActionButton, self.plusButtonWidgets, self.otherWidgets
        )
        self.updateLayout()

    def replaceWidget(
        self,
        from_: QWidget,
        to: QWidget,
        fromList: list[tuple[QWidget, tuple[int, int]]],
        toList: list[tuple[QWidget, tuple[int, int]]],
    ) -> bool:
        oldWidgetLocation = self.getPositionOfWidget(from_)
        if oldWidgetLocation:
            from_.deleteLater()
            fromList.remove((from_, oldWidgetLocation))
            self.addWidget(to, *oldWidgetLocation, addToList=toList)
            return True
        return False

    def getWidgetFromPosition(self, position: tuple[int, int]) -> QWidget | None:
        for w, pos in self.getAllWidgets() + self.plusButtonWidgets:
            if pos == position:
                return w
        return None

    def getPositionOfWidget(self, widget: QWidget) -> tuple[int, int] | None:
        for w, pos in self.getAllWidgets() + self.plusButtonWidgets:
            if w == widget:
                return pos
        return None

    def getRelativePosition(self, widget: QWidget) -> tuple[int, int] | None:
        widgetPos = self.getPositionOfWidget(widget)
        if widgetPos is None:
            return None
        return (
            widgetPos[0] - self.mainWidgetLocation[0],
            widgetPos[1] - self.mainWidgetLocation[1],
        )

    def checkIfOutOfBounds(self, x: int, y: int) -> bool:
        return x < 0 or y < 0 or x >= self.cols or y >= self.rows

    @staticmethod
    def outOfBoundsDirection(x: int, y: int) -> tuple[int, int]:
        # Determine the direction of the out-of-bounds position
        # Input: (-5, 2) -> (-1, 1)
        return (x < 0) * -1, (y < 0) * -1

    def checkIfEmpty(self, x: int, y: int) -> bool:
        for _, pos in self.getAllWidgets() + self.plusButtonWidgets:
            if pos[0] == x and pos[1] == y:
                return False
        return True

    def stretchToFill(self):
        for i in range(self.cols):
            self.setColumnStretch(i, 1)
        for i in range(self.rows):
            self.setRowStretch(i, 1)

    # REMOVE =========== OLD FUNCTIONS =================

    # def growGridIfMinus(self, direction: tuple[int, int]):
    #     # Grow the grid in the negative direction
    #     if direction[0] < 0:
    #         self.mainWidgetLocation = (self.mainWidgetLocation[0] + 1, self.mainWidgetLocation[1])
    #         self.otherWidgets = [(w, (wx + 1, wy)) for w, (wx, wy) in self.otherWidgets]
    #     elif direction[1] < 0:
    #         self.mainWidgetLocation = (self.mainWidgetLocation[0], self.mainWidgetLocation[1] + 1)
    #         self.otherWidgets = [(w, (wx, wy + 1)) for w, (wx, wy) in self.otherWidgets]

    #     self.update_layout()
