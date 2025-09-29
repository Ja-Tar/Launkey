from typing import TYPE_CHECKING, Optional, Any

import asyncio
import struct
import launchpad_py as launchpad

from enum import Enum, auto
from PySide6.QtCore import QModelIndex, Qt, QPoint
from PySide6.QtWidgets import (
    QTableWidgetItem, QTableWidget, QAbstractItemView,
    QAbstractScrollArea, QSizePolicy, QItemDelegate,
)
from PySide6.QtGui import (
    QColor, QBrush, QDragEnterEvent, QDropEvent, 
    QDragMoveEvent, QPixmap, QPainter, QPen,
)

from .templates import (
    Template, TemplateItem, Button, LED,
    sterilizeTemplateName,
    ledsToColorCode,
    loadedTemplates,
)

if TYPE_CHECKING:
    from .app import Launkey

class Sides(Enum):
    LEFT = auto()
    RIGHT = auto()
    TOP = auto()
    BOTTOM = auto()

class LaunchpadTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(9, 9, parent)  # 8x8 grid + 1 row and 1 column for autoMap
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(True)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(4)
        self.setSizePolicy(sizePolicy)
        #self.viewport().setProperty("cursor", QCursor(Qt.CursorShape.ArrowCursor))
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)

        self.setItemDelegate(QItemDelegate())

        noButtonBrush = QBrush(QColor(0, 0, 0, 255))
        noButtonBrush.setStyle(Qt.BrushStyle.DiagCrossPattern)
        noButton = QTableWidgetItem()
        noButton.setBackground(noButtonBrush)
        noButton.setFlags(Qt.ItemFlag.NoItemFlags)
        # top row and left column are for autoMap
        self.setItem(0, 8, noButton)  # top-right corner cell

        disabledButtonBrush = QBrush(QColor(200, 200, 200, 100))
        disabledButtonBrush.setStyle(Qt.BrushStyle.FDiagPattern)
        disabledButton = QTableWidgetItem()
        disabledButton.setToolTip("Disabled for NOW")
        disabledButton.setBackground(disabledButtonBrush)
        disabledButton.setFlags(Qt.ItemFlag.NoItemFlags)

        # REMOVE temporary disable to autoMap
        for i in range(8):
            self.setItem(0, i, disabledButton.clone())  # top row
            self.setItem(i + 1, 8, disabledButton.clone())  # right column

        self.setStyleSheet("""
            QTableWidget {
                gridline-color: darkgray;
                border: 1px solid darkgray;
            }
        """)

        for i in range(9):
            self.setColumnWidth(i, 40) # IDEA size setting in settings
            self.setRowHeight(i, 40)

        # Initialize all cells with empty items
        self.clear()

        # Initialize variables
        self.occupiedCells: list[tuple[int, int]] = []  # To track occupied cells
        self.loadedTemplates: dict[tuple[int, int], list[Template | TemplateItem]] = {}  # To track loaded templates

        # (red, green) tuples for each LED on the launchpad
        self.frame: list[tuple[LED, LED]] = [(LED.OFF, LED.OFF)] * 64
        self.autoMap: list[tuple[LED, LED]] = [(LED.OFF, LED.OFF)] * 16
        # first 8 LEDs are on the left and the next 8 LEDs are on the top
        # tuple is main object position in table

    def resetTemplates(self):
        self.occupiedCells.clear()
        self.loadedTemplates.clear()
        self.clear()

    def clear(self):
        for row in range(9):
            for col in range(9):
                if row == 0 and col == 8:
                    continue  # Skip the top-right corner cell

                # REMOVE temporary disable to autoMap
                if (row == 0) or (col == 8):
                    continue

                item = QTableWidgetItem()
                self.setItem(row, col, item)

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        if event.mimeData().hasFormat("application/x-template"):
            mimeData = event.mimeData().data("application/x-template")
            # b''.join(struct.pack('ii', row, col) for row, col in self.locationList)
            occupiedRelativePositions: list[tuple[int, int]] = [tuple(struct.unpack('ii', mimeData.data()[i:i + 8])) for i in range(0, len(mimeData.data()), 8)]
            pos = event.position().toPoint()
            index: QModelIndex = self.indexAt(pos)
            if occupiedRelativePositions and index.isValid():
                tablePosition = (index.row(), index.column())
                for relPos in occupiedRelativePositions:
                    pos = (tablePosition[0] + relPos[0], tablePosition[1] + relPos[1])
                    if self.isOnOccupiedCells(pos):
                        event.ignore()
                        return
                    elif self.isOutOfBounds(pos):
                        event.ignore()
                        return
                event.acceptProposedAction()
                return
        event.ignore()

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        if event.mimeData().hasFormat("application/x-template"):
            # Extract the template name from the drag object name
            templateName = event.mimeData().text()
            templateFileName = sterilizeTemplateName(templateName) + ".json"
            if templateFileName not in loadedTemplates:
                raise ValueError(f"Template {templateFileName} not loaded")

            pos = event.position().toPoint()
            index: QModelIndex = self.indexAt(pos)
            if index.isValid():
                self.isValidLocation((index.row(), index.column()), loadedTemplates[templateFileName])
                # TODO handle the drop logic here (load template, etc.)
                row = index.row()
                col = index.column()
                tablePosition = (row, col)
                if (row == 0) or (col == 8): # REMOVE temporary disable to autoMap
                    return  # Ignore drops on autoMap cells
                print("====================")
                print(f"File name: {templateFileName}")
                templateData = loadedTemplates[templateFileName]
                if not templateData:
                    raise ValueError(f"Template {templateFileName} is empty")
                self.loadDataFromTemplate(tablePosition, templateData)
                event.acceptProposedAction()

    def isValidLocation(self, tablePosition: tuple[int, int], templateData: list[Template | TemplateItem]) -> bool:
        for item in templateData:
            if isinstance(item, TemplateItem):
                itemPos = (tablePosition[0] + item.location[0], tablePosition[1] + item.location[1])
                if self.isOutOfBounds(itemPos):
                    return False
                if self.isOnOccupiedCells(itemPos):
                    return False
        return True

    def isOutOfBounds(self, itemPos: tuple[int, int]) -> bool:
        item = self.item(*itemPos)
        if not item:
            return True
        elif item.flags() == Qt.ItemFlag.NoItemFlags:
            return True
        return False

    def isOnOccupiedCells(self, itemPos: tuple[int, int]) -> bool:
        return itemPos in self.occupiedCells

    def loadDataFromTemplate(self, tablePosition: tuple[int, int], templateData: list[Template | TemplateItem]):
        item = self.item(*tablePosition)
        if item is not None:
            # REMOVE debug
            launchpadPosition = (tablePosition[0] - 1, tablePosition[1])  # Adjust for autoMap row
            print(f"Loading template at launchpad position: {launchpadPosition}")

            self.loadedTemplates[tablePosition] = templateData
            templateLayout: list[tuple[int, int]] = []
            for templateItem in templateData:
                if isinstance(templateItem, Template):
                    print(f"Main template item {templateItem}")
                elif isinstance(templateItem, TemplateItem):
                    print(f"Sub template item {templateItem.location} -> {templateItem}")
                    itemPos = (tablePosition[0] + templateItem.location[0], tablePosition[1] + templateItem.location[1])
                    item = self.item(*itemPos)
                    if item is not None:
                        templateLayout.append(itemPos)
                        self.occupiedCells.append(itemPos)
                    else:
                        raise ValueError(f"Item position {itemPos} is invalid")
                else:
                    raise ValueError(f"Unknown template item type: {templateItem}")
            self.drawTemplateItemsInTable([item for item in templateData if isinstance(item, TemplateItem)], templateLayout)
            print(f"Occupied cells: {self.occupiedCells}")

    def drawTemplateItemsInTable(self, templateData: list[TemplateItem], templateLayout: list[tuple[int, int]]):
        for i, templateItem in enumerate(templateData):
            itemPos = templateLayout[i]
            item = self.item(*itemPos)
            if item is None:
                continue

            pixmap = QPixmap(38, 38)
            painter = QPainter(pixmap)
            painter.fillRect(0, 0, 38, 38, Qt.GlobalColor.black)

            # TODO remember to add types of TemplateItem when more are added
            if isinstance(templateItem, Button):
                colorCode = ledsToColorCode(templateItem.normalColor)
                painter.setBrush(colorCode)
                painter.drawRoundedRect(0, 0, 38, 38, 10, 10)
                if colorCode == "#222222":
                    painter.setPen(QPen(Qt.GlobalColor.darkGray, 2, Qt.PenStyle.DotLine))
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    painter.drawRoundedRect(1, 1, 36, 36, 10, 10)


            painter.setPen(QPen(Qt.GlobalColor.gray, 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            toDraw = self._getWhatToDraw(itemPos, templateLayout)
            center = painter.viewport().center()
            adjustedCenter = center + QPoint(1, 1) # slight adjustment
            if Sides.LEFT in toDraw:
                painter.drawLine(adjustedCenter.x(), adjustedCenter.y(), 0, adjustedCenter.y())
            if Sides.RIGHT in toDraw:
                painter.drawLine(adjustedCenter.x(), adjustedCenter.y(), 38, adjustedCenter.y())
            if Sides.TOP in toDraw:
                painter.drawLine(adjustedCenter.x(), adjustedCenter.y(), adjustedCenter.x(), 0)
            if Sides.BOTTOM in toDraw:
                painter.drawLine(adjustedCenter.x(), adjustedCenter.y(), adjustedCenter.x(), 38)


            painter.end()
            item.setBackground(pixmap)

    def _getWhatToDraw(self, itemPos: tuple[int, int], templateLayout: list[tuple[int, int]]) -> list[str]:
        sides = []
        x, y = itemPos
        if (x, y - 1) in templateLayout:
            sides.append(Sides.LEFT)
        if (x, y + 1) in templateLayout:
            sides.append(Sides.RIGHT)
        if (x - 1, y) in templateLayout:
            sides.append(Sides.TOP)
        if (x + 1, y) in templateLayout:
            sides.append(Sides.BOTTOM)
        return sides
    
class LaunchpadWrapper:
    def __init__(self, table: LaunchpadTable):
        self.lp = launchpad.Launchpad()
        self.table = table
        self.connected = False

    def connect(self) -> bool:
        print(self.lp.ListAll())
        if self.lp.Check():
            self.lp.Open()
            self.lp.Reset()
            self.lp.ButtonFlush()
            return True
        return False
    
    def changeLedsRapid(self, frame: list[tuple[LED, LED]], autoMap: Optional[list[tuple[LED, LED]]] = None):
        if autoMap is None:
            autoMap = [(LED.OFF, LED.OFF)] * 16
        combined_frame = frame + autoMap
        formatted_frame = [self.lp.LedGetColor(x, y) for x, y in combined_frame]
        self.lp.LedCtrlRawRapid(formatted_frame)
        self.lp.LedCtrlRawRapidHome()
        # TODO: add sync to table frame and autoMap (can be also done when clicking buttons)

    def getButtonState(self) -> Optional[list[tuple[int, int, bool]]]:
        if self.lp.ButtonChanged():
            return self.lp.ButtonStateXY()
        return None
    
    def reset(self):
        self.lp.Reset()
        self.lp.ButtonFlush()