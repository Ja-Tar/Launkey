from typing import TYPE_CHECKING, Optional

import asyncio
import struct
import keyboard
import launchpad_py as launchpad

from enum import Enum, auto
from PySide6.QtCore import QModelIndex, Qt, QPoint
from PySide6.QtWidgets import (
    QTableWidgetItem, QTableWidget, QAbstractScrollArea, QSizePolicy, QItemDelegate,
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
from .custom_widgets import QLabelStatusBarInfo, ShortcutDisplay

# Override keyboard on_press and on_release because of the bug in keyboard package
def _onpress(callback, suppress=False):
    return keyboard.hook(lambda e: e.event_type == keyboard.KEY_DOWN and callback(e), suppress=suppress)
def _onrelease(callback, suppress=False):
    return keyboard.hook(lambda e: e.event_type == keyboard.KEY_UP and callback(e), suppress=suppress)

keyboard.on_press = _onpress
keyboard.on_release = _onrelease

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
        self.loadedTemplates: dict[tuple[int, int], TemplateItem] = {}  # To track loaded templates items
        self.loadedTempTypes: dict[tuple[tuple[int, int], ...], Template] = {}  # To track loaded template types
        self.pressedButtons: list[tuple[int, int]] = []  # To track button states

        # (red, green) tuples for each LED on the launchpad
        self.currentFrame: list[tuple[LED, LED]] = [(LED.OFF, LED.OFF)] * 64
        self.currentAutoMap: list[tuple[LED, LED]] = [(LED.OFF, LED.OFF)] * 16
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
            # b''.join(struct.pack('ii', row, col) for row, col in self.locationList) # skipqc PY-W0069
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
                row = index.row()
                col = index.column()
                tablePosition = (row, col)
                if (row == 0) or (col == 8): # REMOVE temporary disable to autoMap
                    return  # Ignore drops on autoMap cells
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
            templateLayout: list[tuple[int, int]] = []
            for templateItem in templateData:
                if isinstance(templateItem, Template):
                    pass
                elif isinstance(templateItem, TemplateItem):
                    itemPos = (tablePosition[0] + templateItem.location[0], tablePosition[1] + templateItem.location[1])
                    item = self.item(*itemPos)
                    if item is not None:
                        templateLayout.append(itemPos)
                        self.occupiedCells.append(itemPos)
                        self.loadedTemplates[itemPos] = templateItem
                    else:
                        raise ValueError(f"Item position {itemPos} is invalid")
                else:
                    raise ValueError(f"Unknown template item type: {templateItem}")
            self.drawTemplateItemsInTable([item for item in templateData if isinstance(item, TemplateItem)], templateLayout)
            if templateData and isinstance(templateData[0], Template):
                self.loadedTempTypes[tuple(templateLayout)] = templateData[0]

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
    
    def returnFirstFrame(self) -> list[tuple[LED, LED]]:
        frame: list[tuple[LED, LED]] = [(LED.OFF, LED.OFF)] * 64
        #autoMap: list[tuple[LED, LED]] = [(LED.OFF, LED.OFF)] * 16

        for tablePosition, itemData in self.loadedTemplates.items():
            launchpadPos = (tablePosition[0] - 1, tablePosition[1])  # Adjust for autoMap row
            
            if isinstance(itemData, Button):
                index = launchpadPos[0] * 8 + launchpadPos[1]
                if 0 <= index < 64:
                    frame[index] = itemData.normalColor
            else:
                raise ValueError(f"Unknown TemplateItem type: {itemData}")
                # TODO handle other TemplateItem types when added
        self.currentFrame = frame
        return frame
    
    def drawFirstTableFrame(self):
        for row in range(1, 9):
            for col in range(8):
                item = self.item(row, col)
                if item is not None:
                    launchpadPos = (row - 1, col)  # Adjust for autoMap row
                    index = launchpadPos[0] * 8 + launchpadPos[1]
                    if 0 <= index < 64:
                        color = self.currentFrame[index]
                        colorCode = ledsToColorCode(color)
                        if not colorCode == "#222222":
                            item.setBackground(QColor(colorCode))
                        else:
                            newItem = QTableWidgetItem()
                            self.setItem(row, col, newItem)

    def changeButtonColorInTable(self, buttonPos: tuple[int, int], newColor: tuple[LED, LED]):
        item = self.item(*buttonPos)
        if item is not None:
            colorCode = ledsToColorCode(newColor)
            if not colorCode == "#222222":
                item.setBackground(QColor(colorCode))
            else:
                newItem = QTableWidgetItem()
                self.setItem(*buttonPos, newItem)

    def getTemplateItemAtButton(self, buttonPos: tuple[int, int]) -> TemplateItem | None: # buttonPos is launchpad position is flipped (y, x)
        buttonPos = (buttonPos[1], buttonPos[0])
        for tablePosition, itemData in self.loadedTemplates.items():
            if tablePosition == buttonPos:
                return itemData
        return None  # Return empty list if not found
    
    def isFrameChangeNeeded(self, newFrame: list[tuple[LED, LED]], newAutoMap: Optional[list[tuple[LED, LED]]] = None) -> bool:
        if newAutoMap is None:
            newAutoMap = [(LED.OFF, LED.OFF)] * 16
        if newFrame != self.currentFrame or newAutoMap != self.currentAutoMap:
            self.currentFrame = newFrame
            self.currentAutoMap = newAutoMap
            return True
        return False
    
    def buttonPressed(self, buttonPos: tuple[int, int], buttonItem: Button):
        buttonPos = (buttonPos[1], buttonPos[0])  # flip to table position
        index = (buttonPos[0] - 1) * 8 + buttonPos[1]  # Adjust for autoMap row
        if 0 <= index < 64:
            self.currentFrame[index] = buttonItem.pushedColor
            self.pressedButtons.append((buttonPos))
        self.changeButtonColorInTable(buttonPos, buttonItem.pushedColor)

    def buttonUnpressed(self, buttonPos: tuple[int, int]):
        buttonPos = (buttonPos[1], buttonPos[0])  # flip to table position
        index = (buttonPos[0] - 1) * 8 + buttonPos[1]  # Adjust for autoMap row
        if 0 <= index < 64:
            if buttonPos in self.pressedButtons:
                item = self.loadedTemplates.get(buttonPos)
                if isinstance(item, Button):
                    self.currentFrame[index] = item.normalColor
                    self.changeButtonColorInTable(buttonPos, item.normalColor)
                else:
                    raise ValueError(f"Unknown TemplateItem type: {item}")
                self.pressedButtons.remove(buttonPos)

class LaunchpadWrapper:
    def __init__(self, table: LaunchpadTable):
        self.lp = launchpad.Launchpad()
        self.table = table

    def connect(self) -> bool:
        if self.lp.Check():
            self.lp.Open()
            self.lp.Reset()
            self.lp.ButtonFlush()
            return True
        return False
    
    def start(self):
        returnFrame = self.table.returnFirstFrame()
        self.table.drawFirstTableFrame()
        self.changeLedsRapid(returnFrame)

    def startTestMode(self):
        self.table.returnFirstFrame()
        self.table.drawFirstTableFrame()

    def stop(self):
        self.resetTable()
        self.resetPad()

    def stopTestMode(self):
        self.resetTable()

    def changeLedsRapid(self, frame: list[tuple[LED, LED]], autoMap: Optional[list[tuple[LED, LED]]] = None):
        if autoMap is None:
            autoMap = [(LED.OFF, LED.OFF)] * 16
        combined_frame = frame + autoMap
        combined_frame = [(r.value, g.value) for r, g in combined_frame]
        formatted_frame = [self.lp.LedGetColor(x, y) for x, y in combined_frame]
        self.lp.LedCtrlRawRapid(formatted_frame)
        self.lp.LedCtrlRawRapidHome()

    def getButtonStates(self) -> Optional[list[tuple[int, int, bool]]]:
        if self.lp.ButtonChanged():
            return self.lp.ButtonStateXY()
        return None
    
    async def buttonPressed(self, buttonPos: tuple[int, int], templateItem: TemplateItem | None, /, testMode: ShortcutDisplay | None = None):
        if isinstance(templateItem, Button):
            self.table.buttonPressed(buttonPos, templateItem)
            if testMode:
                testMode.setShortcutText(templateItem.keyboardCombo)
                return
            self.lp.LedCtrlXY(buttonPos[0], buttonPos[1], templateItem.pushedColor[0].value, templateItem.pushedColor[1].value)
            keyboard.press(templateItem.keyboardCombo)

    async def buttonUnpressed(self, buttonPos: tuple[int, int], /, testMode: ShortcutDisplay | None = None):
        for pos in self.table.pressedButtons:
            if buttonPos == (pos[1], pos[0]):  # flip to table position
                item = self.table.loadedTemplates.get(pos)
                if isinstance(item, Button):
                    if testMode:
                        testMode.clearShortcutText(item.keyboardCombo)
                        continue
                    self.lp.LedCtrlXY(buttonPos[0], buttonPos[1], item.normalColor[0].value, item.normalColor[1].value)
                    keyboard.release(item.keyboardCombo)
        self.table.buttonUnpressed(buttonPos)

    def resetPad(self):
        self.lp.Reset()
    
    def resetTable(self):
        # Rebuild original templates with self.table.loadedTempTypes
        loadedTemplates = {
            key: value for key, value in self.table.loadedTemplates.items()
        }
        loadedCombinations: list[tuple[tuple[tuple[int, int], ...], list[TemplateItem]]] = []
        for locations, _ in self.table.loadedTempTypes.items():
            templateToSave: tuple[tuple[tuple[int, int], ...], list[TemplateItem]] = (
                locations,
                [item for loc in locations if (item := loadedTemplates.get(loc)) is not None]
            )
            loadedCombinations.append(templateToSave)

        for template in loadedCombinations:
            locs = template[0]
            data = template[1]
            self.table.drawTemplateItemsInTable(
                data, list(locs)
            )

class KeyboardTester:
    def __init__(self, main_window: "Launkey", lpWrapper: LaunchpadWrapper, testModeDisplay: ShortcutDisplay):
        self.main_window = main_window
        self.lpWrapper = lpWrapper
        self.lowerHalf = False  # On launchpad the lower half is rows 5-8
        self.pressedKeys: list[str] = []
        self.testModeDisplay = testModeDisplay

    def checkTestMode(self, checked: bool = False):
        if checked:
            self.testModeOn()
            self.testModeDisplay.show()
        else:
            self.testModeOff()
            self.testModeDisplay.hide()

    def testModeOn(self):
        self.main_window.ui.statusbar.addWidget(QLabelStatusBarInfo("Test Mode Active", colour="yellow"))
        self.main_window.ui.buttonRun.setEnabled(True)

    async def testModeRun(self):
        if self.main_window.ui.buttonRun.text() == "Run":
            self.main_window.ui.startRun()
            self.lpWrapper.startTestMode()
            loop = asyncio.get_running_loop()
            keyboard.on_press(lambda event: self.onPressCallback(event, loop))
            keyboard.on_release(lambda event: self.onReleaseCallback(event, loop))
            return
        self.main_window.ui.stopRun()
        keyboard.unhook_all()
        for task in asyncio.all_tasks():
            if task.get_name() in ["testModeLoop"]:
                task.cancel()
        self.lpWrapper.stopTestMode()

    def onPressCallback(self, event: keyboard.KeyboardEvent, loop: asyncio.AbstractEventLoop):
        asyncio.run_coroutine_threadsafe(self.keyboardTestingPress(event), loop)

    def onReleaseCallback(self, event: keyboard.KeyboardEvent, loop: asyncio.AbstractEventLoop):
        asyncio.run_coroutine_threadsafe(self.keyboardTestingUnpress(event), loop)

    keyboardTable = {
        1: "12345678",
        2: "qwertyui",
        3: "asdfghjk",
        4: "zxcvbnm,"
    }
    lowerHalfChanger = "/"

    async def keyboardTestingPress(self, event: keyboard.KeyboardEvent):
        if not event.name:
            raise ValueError("Event name is empty, press event")
        elif event.name in self.pressedKeys:
            return  # Key is already pressed, ignore
        for row, keys in self.keyboardTable.items():
            if event.name in keys:
                self.pressedKeys.append(event.name)
                keyIndex = keys.index(event.name)
                buttonPos = (keyIndex, row + (4 if self.lowerHalf else 0))
                await self.lpWrapper.buttonPressed(buttonPos, self.lpWrapper.table.getTemplateItemAtButton((buttonPos[0], buttonPos[1])), testMode=self.testModeDisplay)
        if event.name == self.lowerHalfChanger:
            self.lowerHalf = not self.lowerHalf
            self.testModeDisplay.changeSideLabel("Bottom Half" if self.lowerHalf else "Top Half")

    async def keyboardTestingUnpress(self, event: keyboard.KeyboardEvent):
        if not event.name:
            raise ValueError("Event name is empty, release event")
        elif event.name not in self.pressedKeys:
            return  # Key is not pressed, ignore
        for row, keys in self.keyboardTable.items():
            if event.name in keys:
                self.pressedKeys.remove(event.name)
                keyIndex = keys.index(event.name)
                buttonPos = (keyIndex, row + (4 if self.lowerHalf else 0))
                await self.lpWrapper.buttonUnpressed((buttonPos[0], buttonPos[1]), testMode=self.testModeDisplay)

    def keyboardTestingUnpressSync(self, event):
        asyncio.create_task(self.keyboardTestingUnpress(event))

    def testModeOff(self):
        for widget in self.main_window.ui.statusbar.findChildren(QLabelStatusBarInfo):
            if widget.text() == "Test Mode Active":
                self.main_window.ui.statusbar.removeWidget(widget)
                break
        self.main_window.ui.buttonRun.setEnabled(False)
