from typing import Literal
from warnings import deprecated
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


class TemplateGridLayout(QGridLayout):
    def __init__(self, mainWidget: QWidget, parent=None, rows: int = 8, cols: int = 8):
        super().__init__(parent)
        self.setContentsMargins(5, 5, 5, 5)
        self.setSpacing(0)
        self.setObjectName("launcherGridLayout")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.rows = rows
        self.cols = cols
        self.mainWidget = mainWidget
        center = rows // 2, cols // 2
        self.mainWidgetLocation = center
        super().addWidget(self.mainWidget, *self.mainWidgetLocation, Qt.AlignmentFlag.AlignBaseline)
        self.otherWidgets: list[tuple[QWidget, tuple[int, int]]] = []  # (widget, (row, col))
        self.plusButtonWidgets: list[tuple[QWidget, tuple[int, int]]] = []  # (button, (row, col))
        self.updateLayout()

    def __str__(self) -> str:
        # Custom string representation for debugging
        layout_str = f"LauncherGridLayout({self.rows}x{self.cols})\n"
        # print table
        for row in range(self.rows):
            for col in range(self.cols):
                if (row, col) == self.mainWidgetLocation:
                    layout_str += "[M] "
                elif (row, col) in self.getOccupiedPositions():
                    layout_str += "[X] "
                else:
                    layout_str += "[ ] "
            layout_str += "\n"
        return layout_str

    def updateLayout(self):
        self.autoAddPlusButtons()
        self.stretchOccupied()

    def autoAddPlusButtons(self):
        for _, (row, col) in self.getAllWidgets():
            for addRow, addCol in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                if ((row + addRow, col + addCol) not in self.getOccupiedPositions() and (row + addRow, col + addCol) != self.mainWidgetLocation and row + addRow >= 0 and col + addCol >= 0 and row + addRow < self.rows and col + addCol < self.cols):
                    button = PlusButton()
                    button.clicked.connect(lambda _, r=row + addRow, c=col + addCol: self._plusButtonAction(r, c))
                    super().addWidget(button, row + addRow, col + addCol, Qt.AlignmentFlag.AlignCenter)
                    self.plusButtonWidgets.append((button, (row + addRow, col + addCol)))

    def _plusButtonAction(self, rowBtn: int, colBtn: int):
        newWidget = SquareButton(f"Action{rowBtn},{colBtn}")
        # remove widget on right click
        newWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        newWidget.customContextMenuRequested.connect(lambda pos: self._actionButtonRemove(rowBtn, colBtn))
        self.addWidget(newWidget, rowBtn, colBtn, alignment=Qt.AlignmentFlag.AlignBaseline)
        self.updateLayout()

    def _actionButtonRemove(self, rowBtn: int, colBtn: int):
        self.clearPlusButtons()
        for widget, pos in self.otherWidgets:
            if pos == (rowBtn, colBtn):
                widget.setStyleSheet("background-color: darkred;")
                break

        self.clearPlusButtons()
        for widget, pos in self.otherWidgets:
            if pos == (rowBtn, colBtn):
                self.removeWidget(widget)
                widget.deleteLater()
                self.otherWidgets.remove((widget, pos))
                break
        self.updateLayout()

    def clearPlusButtons(self):
        for button, pos in self.plusButtonWidgets:
            super().removeWidget(button)
            button.deleteLater()
        self.plusButtonWidgets.clear()

    def addWidget(
        self,
        widget: QWidget,
        row: int,
        col: int,
        rowSpan: int = 1,
        colSpan: int = 1,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter,
    ):
        self.clearPlusButtons()

        if (row, col) == self.mainWidgetLocation:
            return  # Cannot add widget at the main widget location.
        if (row, col) in self.getOccupiedPositions():
            return  # Cannot add widget at occupied position.

        super().addWidget(widget, row, col, rowSpan, colSpan, alignment)
        self.otherWidgets.append((widget, (row, col)))
        self.updateLayout()
        print(self.__str__())  # REMOVE

    def getAllWidgets(self):
        # Plus buttons are automatically generated so only main and other widgets are included
        return [(self.mainWidget, self.mainWidgetLocation)] + self.otherWidgets

    def getOccupiedPositions(self) -> set[tuple[int, int]]:
        return {self.mainWidgetLocation} | {pos for _, pos in self.otherWidgets} | {pos for _, pos in self.plusButtonWidgets}

    def stretchOccupied(self):
        # Set stretch 1 for occupied, 0 for not occupied
        occupied = self.getOccupiedPositions()
        for row in range(self.rows):
            self.setRowStretch(row, 1 if any(pos[0] == row for pos in occupied) else 0)
        for col in range(self.cols):
            self.setColumnStretch(col, 1 if any(pos[1] == col for pos in occupied) else 0)
        


@deprecated("Use LauncherGridLayout instead")
class CenterGridLayout(QGridLayout):
    def __init__(self, mainWidget: QWidget, parent=None, maxRows: int = 8, maxCols: int = 8):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(5)
        self.setObjectName("gridLayout")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.rows = 3
        self.cols = 3
        self.maxRows = maxRows
        self.maxCols = maxCols
        self.mainWidget = mainWidget
        self.mainWidgetLocation = (1, 1)  # default on 3x3
        super().addWidget(self.mainWidget, *self.mainWidgetLocation, Qt.AlignmentFlag.AlignBaseline)

        self.otherWidgets: list[tuple[QWidget, tuple[int, int]]] = []  # (widget, (x, y))
        self.plusButtonWidgets: list[tuple[QWidget, tuple[int, int]]] = []  # (button, (x, y))
        self.updateLayout()
        self.test_function()

    def test_function(self):
        print("Test function called")
        self.addWidget(QPushButton("Test Button"), 0, 0)
        self.addWidget(QPushButton("Test Button 2"), -1, 0)

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
            return # Cannot add widget at the main widget location.
        if addToList is None:
            addToList = self.otherWidgets
        if not self.checkIfEmpty(x, y):
            return # Cannot add widget at occupied position.

        if self.checkIfOutOfCurrentBounds(x, y):
            direction = self.getDirection(x, y)
            if self.checkIfOutOfTable(direction):
                return # Cannot add widget out of table bounds.
            if not self.canAddInDirection(direction):
                # Handle the case where the widget cannot be added in the desired direction
                print(f"Cannot add widget {widget} in direction {direction}.")
                direction = self.moveWidgets(direction) # direction to add column/row
                self.rows, self.cols = self.getNewRowColCounts(direction)
                return
            self.addRowOrColumnToList(direction)

        super().addWidget(widget, x, y, alignment=alignment)
        if addToList is not None:
            addToList.append((widget, (x, y)))
        #self.updateLayout()

    def getNewRowColCounts(self, direction: tuple[Literal[-1, 0, 1], Literal[-1, 0, 1]]) -> tuple[int, int]:
        if direction == (1, 0):
            return self.rows + 1, self.cols
        elif direction == (0, 1):
            return self.rows, self.cols + 1
        elif direction == (-1, 0):
            return self.rows - 1, self.cols
        elif direction == (0, -1):
            return self.rows, self.cols - 1
        raise ValueError("Unknown direction")

    def moveWidgets(self, direction: tuple[Literal[-1, 0, 1], Literal[-1, 0, 1]]) -> tuple[Literal[-1, 0, 1], Literal[-1, 0, 1]]:
        if direction[0] > 0 or direction[1] > 0 or direction == (0, 0):
            raise RuntimeError(f"Cannot move widgets in {direction} direction.")
        addedDirection = (0, 0)
        if direction[0] == -1:
            # move to widgets right
            addedDirection = (addedDirection[0] + 1, addedDirection[1])
        if direction[1] == -1:
            # move to widgets down
            addedDirection = (addedDirection[0], addedDirection[1] + 1)
        for i, (widget, pos) in enumerate(self.otherWidgets):
            pos = (pos[0] + addedDirection[0], pos[1] + addedDirection[1])
            self.otherWidgets[i] = (widget, pos)
        for i, (widget, pos) in enumerate(self.plusButtonWidgets):
            pos = (pos[0] + addedDirection[0], pos[1] + addedDirection[1])
            self.plusButtonWidgets[i] = (widget, pos)
        self.mainWidgetLocation = (
            self.mainWidgetLocation[0] + addedDirection[0],
            self.mainWidgetLocation[1] + addedDirection[1],
        )
        self.updateWidgetPositions()
        return addedDirection

    def updateWidgetPositions(self): # TODO use takeAt()
        for widget, pos in self.getAllWidgets() + self.plusButtonWidgets:
            pass


    def canAddInDirection(self, direction: tuple[Literal[-1, 0, 1], Literal[-1, 0, 1]]) -> bool:
        if direction == (0, 0):
            raise RuntimeError("Widget is out of bounds but direction is (0,0).")
        if direction[0] == -1 or direction[1] == -1:
            # Add row above, or column to the left
            return False
        elif direction[0] == 1 or direction[1] == 1:
            # Add row below, or column to the right
            return True
        raise ValueError("Unknown direction")

    def addRowOrColumnToList(self, direction: tuple[Literal[-1, 0, 1], Literal[-1, 0, 1]]):
        if direction in [(-1, 0), (0, -1), (-1, -1)]:
            raise RuntimeError("Invalid direction")
        self.rows += direction[0] # Update row count
        self.cols += direction[1] # Update column count

    def updateLayout(self):
        self.stretchToFill()
        # self.autoAddPlusButtons()
        # self.alignButtonsToWidgets()

    def autoAddPlusButtons(self):
        widgetsList = self.getAllWidgets()
        for _, (x, y) in widgetsList:
            # add buttons to 8 places around widget
            for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                plusButton = PlusButton()
                plusButton.clicked.connect(
                    lambda _, btn=plusButton: self._plusButtonAction(btn)
                )
                plusButton.setObjectName(f"plusButton_{x + dx}_{y + dy}")
                self.addWidget(
                    plusButton,
                    x + dx,
                    y + dy,
                    Qt.AlignmentFlag.AlignCenter,
                    self.plusButtonWidgets,
                )

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
            if w is widget:
                return pos
        return None

    def checkIfOutOfCurrentBounds(self, x: int, y: int) -> bool:
        return x < 0 or y < 0 or x >= self.rows or y >= self.cols
    
    def checkIfOutOfTable(self, direction: tuple[Literal[-1, 0, 1], Literal[-1, 0, 1]]) -> bool:
        # if rows are the same as maxRows and we are moving down or up
        if self.rows >= self.maxRows and direction[0] != 0:
            return True
        # if cols are the same as maxCols and we are moving right or left
        if self.cols >= self.maxCols and direction[1] != 0:
            return True
        return False

    def getDirection(self, x: int, y: int) -> tuple[Literal[-1, 0, 1], Literal[-1, 0, 1]]:
        # Determine the direction of the out-of-bounds position
        # Input: (-5, 2) -> (-1, 0)
        # Input: (2, -5) -> (0, -1)
        dx = -1 if x < 0 else (1 if x >= self.rows else 0)
        dy = -1 if y < 0 else (1 if y >= self.cols else 0)
        if dx == 0 and dy == 0:
            raise RuntimeError("Position is not out of bounds")
        return (dx, dy)

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

    def alignButtonsToWidgets(self):
        for widget, (x, y) in self.plusButtonWidgets:
            has_bottom = not self.checkIfEmpty(x - 1, y)
            has_top = not self.checkIfEmpty(x + 1, y)
            has_right = not self.checkIfEmpty(x, y - 1)
            has_left = not self.checkIfEmpty(x, y + 1)

            halign = Qt.AlignmentFlag.AlignHCenter
            valign = Qt.AlignmentFlag.AlignVCenter

            if has_left and not has_right:
                halign = Qt.AlignmentFlag.AlignRight
            elif has_right and not has_left:
                halign = Qt.AlignmentFlag.AlignLeft

            if has_top and not has_bottom:
                valign = Qt.AlignmentFlag.AlignBottom
            elif has_bottom and not has_top:
                valign = Qt.AlignmentFlag.AlignTop

            self.setAlignment(widget, halign | valign)

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
