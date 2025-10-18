from typing import Literal
from PySide6.QtWidgets import QGridLayout, QWidget
from PySide6.QtCore import Qt, QTimer

from .custom_widgets import PlusButton, ToggleButton
from .template_options_widgets import TemplateOptionsList
from .templates import Template, TemplateItem

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

    def removeWidget(self, widget):
        self.items = [item for item in self.items if item[0] != widget]
        super().removeWidget(widget)
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
    def __init__(self, mainWidget: ToggleButton, optionsList: TemplateOptionsList, parent=None, rows: int = 8, cols: int = 8, template: list[Template | TemplateItem] | None = None):
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
        self.mainWidget.clicked.connect(lambda _: self._actionButtonClick(self.mainWidget.getButtonID()))
        super().addWidget(self.mainWidget, *self.mainWidgetLocation, Qt.AlignmentFlag.AlignBaseline)

        self.otherWidgets: list[tuple[ToggleButton, tuple[int, int]]] = []  # (widget, (row, col))
        self.plusButtonWidgets: list[tuple[QWidget, tuple[int, int]]] = []  # (button, (row, col))

        self.optionsList = optionsList

        if template:
            self.widgetsFromTemplate(center, template)

        self.updateLayout()
        self._checkToggleOtherButtons(self.mainWidget.getButtonID())

    def widgetsFromTemplate(self, center, template):
        for item in template:
            if isinstance(item, TemplateItem):
                if item.location in [(0, 0), center]:
                    continue  # Skip main button location
                newWidget = ToggleButton(item.name, item.buttonID)
                newWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                # Convert relative position to main widget to absolute position
                newWidgetLocation = (item.location[0] + self.mainWidgetLocation[0], item.location[1] + self.mainWidgetLocation[1])
                newWidget.customContextMenuRequested.connect(lambda _, r=newWidgetLocation[0], c=newWidgetLocation[1]: self._actionButtonRemove(r, c))
                newWidget.clicked.connect(lambda _, bID=item.buttonID: self._actionButtonClick(bID))
                self.addWidget(newWidget, newWidgetLocation[0], newWidgetLocation[1], alignment=Qt.AlignmentFlag.AlignBaseline)
                self.optionsList.addChild(item.buttonID, item.location, name=item.name)

    def __str__(self) -> str:
        # Custom string representation for debugging
        layout_str = f"LauncherGridLayout({self.rows}x{self.cols})\n"
        # print table
        for row in range(self.rows):
            for col in range(self.cols):
                if (row, col) == self.mainWidgetLocation:
                    layout_str += "[M] "
                elif (row, col) in self.getWidgetsPositions():
                    layout_str += "[W] "
                elif (row, col) in self.getPlusButtonsPositions():
                    layout_str += "[+] "
                else:
                    layout_str += "[ ] "
            layout_str += "\n"
        return layout_str

    def setupOptionsListConnection(self):
        self.optionsList.gridLayout = self
        self.optionsList.addChild(self.mainWidget.getButtonID(), self.getWidgetPositionRelativeToMain(self.mainWidget), main=True, name=self.mainWidget.text())  # Add initial child
        self.optionsList.selectChild(self.mainWidget.getButtonID())

    def updateLayout(self):
        self.autoAddPlusButtons()
        self.stretchOccupied()

    def autoAddPlusButtons(self):
        for _, (row, col) in self.getAllWidgets():
            for addRow, addCol in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                # 4 directions around the widget
                #   x
                # x W x
                #   x
                # ----------------------------------------------------
                # Old: [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
                # 8 directions around the widget
                if ((row + addRow, col + addCol) not in self.getOccupiedPositions() and (row + addRow, col + addCol) != self.mainWidgetLocation and row + addRow >= 0 and col + addCol >= 0 and row + addRow < self.rows and col + addCol < self.cols):
                    button = PlusButton()
                    button.clicked.connect(lambda _, r=row + addRow, c=col + addCol: self._plusButtonClick(r, c))
                    super().addWidget(button, row + addRow, col + addCol, Qt.AlignmentFlag.AlignCenter)
                    self.plusButtonWidgets.append((button, (row + addRow, col + addCol)))

    def _plusButtonClick(self, rowBtn: int, colBtn: int):
        relativePos = (rowBtn - self.mainWidgetLocation[0], colBtn - self.mainWidgetLocation[1])
        newWidget = ToggleButton(f"Button {len(self.otherWidgets) + 2}", f"Btn{rowBtn}{colBtn}")

        newWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        newWidget.customContextMenuRequested.connect(lambda _: self._actionButtonRemove(rowBtn, colBtn))
        newWidget.clicked.connect(lambda _: self._actionButtonClick(newWidget.getButtonID()))

        self.addWidget(newWidget, rowBtn, colBtn, alignment=Qt.AlignmentFlag.AlignBaseline)
        self.updateLayout()
        self.optionsList.addChild(newWidget.getButtonID(), relativePos)

    def _actionButtonClick(self, buttonID: str):
        self._checkToggleOtherButtons(buttonID)
        self.optionsList.selectChild(buttonID)

    def _checkToggleOtherButtons(self, buttonID: str):
        for button, _ in self.getAllWidgets():
            if isinstance(button, ToggleButton):
                button.checkToggle(buttonID)

    def _actionButtonRemove(self, rowBtn: int, colBtn: int):
        adjacentPositions = [(rowBtn - 1, colBtn), (rowBtn + 1, colBtn), (rowBtn, colBtn - 1), (rowBtn, colBtn + 1)]
        adjacentWidgets = self.getWidgetsForPositions(adjacentPositions, allWidgets=True)

        for widget in adjacentWidgets:
            if self.buttonIsolated(widget, (rowBtn, colBtn)):
                self._errorRemoveButton(widget)
                return

        self.clearPlusButtons()

        for widget, pos in self.otherWidgets:
            if pos == (rowBtn, colBtn):
                self._checkToggleOtherButtons(self.mainWidget.getButtonID())
                self.optionsList.deleteChild(widget.getButtonID())
                self.removeWidget(widget)
                widget.deleteLater()
                self.otherWidgets.remove((widget, pos))
                break
        self.updateLayout()
        self.optionsList.selectChild(self.mainWidget.getButtonID())

    def buttonIsolated(self, widget: QWidget, removeLoc: tuple[int, int]) -> bool:
        # Check if the widget has no widgets connecting it to main widget
        widgetPos = self.getWidgetPosition(widget)
        visited = set()
        toVisit = [widgetPos]
        while toVisit:
            current = toVisit.pop()
            if current == self.mainWidgetLocation:
                return False  # Found a path to main widget
            visited.add(current)
            for delta in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (current[0] + delta[0], current[1] + delta[1])
                if (
                    0 <= neighbor[0] < self.rows
                    and 0 <= neighbor[1] < self.cols
                    and neighbor != removeLoc
                    and neighbor not in visited
                    and neighbor in self.getWidgetsPositions()
                ):
                    toVisit.append(neighbor)
        return True  # No path to main widget found

    def clearPlusButtons(self):
        for button, _ in self.plusButtonWidgets:
            super().removeWidget(button)
            button.deleteLater()
        self.plusButtonWidgets.clear()

    def getWidgetsForPositions(self, positions: list[tuple[int, int]], /, allWidgets=False) -> list[ToggleButton]:
        foundWidgets = []
        for pos in positions:
            widget = self.getSingleWidgetPosition(pos, allWidgets=allWidgets)
            if widget:
                foundWidgets.append(widget)
        return foundWidgets

    def getSingleWidgetPosition(self, pos: tuple[int, int], /, allWidgets=False) -> QWidget | None:
        widgetList = self.getAllWidgets() if allWidgets else self.otherWidgets
        for widget, wPos in widgetList:
            if wPos == pos:
                return widget
        return None

    def _errorRemoveButton(self, widget: QWidget):
        # Flash the border of the button at pos to indicate error
        originalStyle = "border-color: darkgray; border-width: 1px;"
        widget.setStyleSheet("border: 2px solid red;")
        QTimer.singleShot(500, lambda: widget.setStyleSheet(originalStyle))

    def addWidget(
        self,
        widget: ToggleButton,
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

    def getAllWidgets(self):
        # Plus buttons are automatically generated so only main and other widgets are included
        return [(self.mainWidget, self.mainWidgetLocation)] + self.otherWidgets

    def getOccupiedPositions(self) -> set[tuple[int, int]]:
        return {self.mainWidgetLocation} | {pos for _, pos in self.otherWidgets} | {pos for _, pos in self.plusButtonWidgets}

    def getWidgetsPositions(self) -> set[tuple[int, int]]:
        return {pos for _, pos in self.otherWidgets} | {self.mainWidgetLocation}

    def getPlusButtonsPositions(self) -> set[tuple[int, int]]:
        return {pos for _, pos in self.plusButtonWidgets}

    def getWidgetPositionRelativeToMain(self, widget: QWidget) -> tuple[int, int]:
        absPos = self.getWidgetPosition(widget)
        return (absPos[0] - self.mainWidgetLocation[0], absPos[1] - self.mainWidgetLocation[1])

    def getWidgetPosition(self, widget: QWidget) -> tuple[int, int]:
        for w, pos in self.getAllWidgets():
            if w == widget:
                return pos
        raise ValueError("Widget not found in layout")

    def updateButtonText(self, buttonID: str, newText: str):
        for widget, _ in self.getAllWidgets():
            if isinstance(widget, ToggleButton) and widget.getButtonID() == buttonID:
                widget.setText(newText)
                break

    def stretchOccupied(self):
        # Set stretch 1 for occupied, 0 for not occupied
        occupied = self.getOccupiedPositions()
        for row in range(self.rows):
            self.setRowStretch(row, 1 if any(pos[0] == row for pos in occupied) else 0)
        for col in range(self.cols):
            self.setColumnStretch(col, 1 if any(pos[1] == col for pos in occupied) else 0)