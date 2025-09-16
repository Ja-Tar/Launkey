from typing import Literal
from warnings import deprecated
from PySide6.QtWidgets import QGridLayout, QWidget
from PySide6.QtCore import Qt

from .custom_widgets import PlusButton, ToggleButton
from .template_options_widgets import TemplateOptionsList

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
    def __init__(self, mainWidget: ToggleButton, optionsList: TemplateOptionsList, parent=None, rows: int = 8, cols: int = 8):
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

        self.updateLayout()
        self._checkToggleOtherButtons(self.mainWidget.getButtonID())

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
                elif (row, col) in self.getAddButtonsPositions():
                    layout_str += "[+] "
                else:
                    layout_str += "[ ] "
            layout_str += "\n"
        return layout_str
    
    def setupOptionsListConnection(self):
        self.optionsList.gridLayout = self
        self.optionsList.addChild(self.mainWidget.getButtonID(), self.getWidgetPositionRelativeToMain(self.mainWidget), main=True)  # Add initial child
        self.optionsList.selectChild(self.mainWidget.getButtonID())

    def updateLayout(self):
        self.autoAddPlusButtons()
        self.stretchOccupied()

    def autoAddPlusButtons(self):
        for _, (row, col) in self.getAllWidgets():
            for addRow, addCol in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                if ((row + addRow, col + addCol) not in self.getOccupiedPositions() and (row + addRow, col + addCol) != self.mainWidgetLocation and row + addRow >= 0 and col + addCol >= 0 and row + addRow < self.rows and col + addCol < self.cols):
                    button = PlusButton()
                    button.clicked.connect(lambda _, r=row + addRow, c=col + addCol: self._plusButtonClick(r, c))
                    super().addWidget(button, row + addRow, col + addCol, Qt.AlignmentFlag.AlignCenter)
                    self.plusButtonWidgets.append((button, (row + addRow, col + addCol)))

    def _plusButtonClick(self, rowBtn: int, colBtn: int):
        newWidget = ToggleButton(f"Button {len(self.otherWidgets) + 2}", f"Btn{rowBtn}{colBtn}")

        newWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        newWidget.customContextMenuRequested.connect(lambda _: self._actionButtonRemove(rowBtn, colBtn))
        newWidget.clicked.connect(lambda _: self._actionButtonClick(newWidget.getButtonID()))
        
        self.addWidget(newWidget, rowBtn, colBtn, alignment=Qt.AlignmentFlag.AlignBaseline)
        self.updateLayout()
        self.optionsList.addChild(newWidget.getButtonID(), self.getWidgetPositionRelativeToMain(newWidget))

    def _actionButtonClick(self, buttonID: str):
        self._checkToggleOtherButtons(buttonID)
        self.optionsList.selectChild(buttonID)

    def _checkToggleOtherButtons(self, buttonID: str):
        for button, _ in self.getAllWidgets():
            if isinstance(button, ToggleButton):
                button.checkToggle(buttonID)

    def _actionButtonRemove(self, rowBtn: int, colBtn: int):
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

    def clearPlusButtons(self):
        for button, pos in self.plusButtonWidgets:
            super().removeWidget(button)
            button.deleteLater()
        self.plusButtonWidgets.clear()

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

    def getAddButtonsPositions(self) -> set[tuple[int, int]]:
        return {pos for _, pos in self.plusButtonWidgets}
    
    def getWidgetPositionRelativeToMain(self, widget: QWidget) -> tuple[int, int]:
        for w, pos in self.getAllWidgets():
            if w == widget:
                return (pos[0] - self.mainWidgetLocation[0], pos[1] - self.mainWidgetLocation[1])
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
            
class TemplatePreviewLayout(QGridLayout):
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # REMOVE !!! Better idea - use QPixmap with QDrag!!!
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    
    # !TODO: This layout will display boxes based on Template data
    # For example:
    # (0,0; 1,0; 1,1; 3,1) means:
    # ![M][X][ ]   
    # ![ ][X][X]   
    # (0,0; -1,-1) means:
    # ![X][ ]
    # ![ ][M]
    # X = occupied, M = main widget
    # Generate only needed number of rows and columns
    def __init__(self, parent=None):
        super().__init__(parent)