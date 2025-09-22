from typing import TYPE_CHECKING, Optional, Any

import asyncio
import launchpad_py as launchpad

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import (
    QTableWidgetItem,
    QTableWidget,
    QAbstractItemView,
    QAbstractScrollArea,
    QSizePolicy,
    QItemDelegate,
)
from PySide6.QtGui import QColor, QBrush, QCursor, QDragEnterEvent, QDropEvent, QDragMoveEvent

if TYPE_CHECKING:
    from .app import Launkey

# ======================
# TODO REWRITE NEEDED!!!

class LaunchpadWrapper:
    def __init__(self, main_window: "Launkey"):
        self.lp = launchpad.Launchpad()
        self.guiTable = GUITable(main_window)
        self._sync_task = None

    def connect(self) -> bool:
        if self.lp.Check():
            self.lp.Open()
            self.lp.Reset()
            self.lp.ButtonFlush()
            return True
        return False

    def start_sync(self):
        if self._sync_task is None:
            self._sync_task = asyncio.create_task(self.guiTable.sync())

    def changeLedsRapid(self, frame: list[tuple[int, int]], autoMap: Optional[list[tuple[int, int]]] = None):
        if autoMap is None:
            autoMap = [(0, 0)] * 16
        combined_frame = frame + autoMap
        formatted_frame = [self.lp.LedGetColor(x, y) for x, y in combined_frame]
        self.lp.LedCtrlRawRapid(formatted_frame)
        self.lp.LedCtrlRawRapidHome()
        # Aktualizuj GUI tylko jeśli dane się zmieniły
        self.guiTable.update_frame(frame, autoMap)

    def reset(self):
        self.lp.Reset()
        self.lp.ButtonFlush()

    def stop(self):
        self.reset()
        self.guiTable.clearAndEnable()
        if self._sync_task:
            self._sync_task.cancel()
        self._sync_task = None

class GUITable:
    def __init__(self, main_window: "Launkey"):
        self.main_window: Launkey = main_window
        # (red, green) tuples for each LED on the launchpad
        # intensity from 0 to 3 for each color
        self.frame: list[tuple[int, int]] = [(0, 0)] * 64
        self.autoMap: list[tuple[int, int]] = [(0, 0)] * 16
        # first 8 LEDs are on the left and the next 8 LEDs are on the top

    def update_frame(self, frame, autoMap):
        self.frame[:] = frame[:]
        self.autoMap[:] = autoMap[:]

    async def sync(self):
        # disable the table to prevent user interaction during updates
        self.main_window.ui.tableLaunchpad.setEnabled(False)
        self.main_window.ui.tableLaunchpad.clearSelection()

        while True:
            # Update the GUI table (move one row down)
            for row in range(8):
                for col in range(8):
                    value = self.frame[row * 8 + col]
                    item = QTableWidgetItem()
                    # Set background color based on value (red, green)
                    r, g = value
                    color = QColor(85 * r, 85 * g, 0)
                    item.setBackground(color)
                    self.main_window.ui.tableLaunchpad.setItem(row + 1, col, item)
            # Update the GUI table with autoMap values (right column)
            for row in range(8):
                value = self.autoMap[row]
                item = QTableWidgetItem()
                r, g = value
                color = QColor(85 * r, 85 * g, 0)
                item.setBackground(color)
                self.main_window.ui.tableLaunchpad.setItem(row + 1, 8, item)
            # Update the GUI table with autoMap values (top row)
            for col in range(8):
                value = self.autoMap[col + 8]
                item = QTableWidgetItem()
                r, g = value
                color = QColor(85 * r, 85 * g, 0)
                item.setBackground(color)
                self.main_window.ui.tableLaunchpad.setItem(0, col, item)

            await asyncio.sleep(0.05)

    def clearAndEnable(self):
        for row in range(9):
            for col in range(9):
                if row == 0 and col == 8:
                    continue
                item = QTableWidgetItem()
                item.setBackground(QColor(255, 255, 255, 0))
                self.main_window.ui.tableLaunchpad.setItem(row, col, item)
        self.main_window.ui.tableLaunchpad.setEnabled(True)

# TODO REWRITE NEEDED!!!
# ======================

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
        self.setAlternatingRowColors(True)
        self.setAcceptDrops(True)

        self.setItemDelegate(QItemDelegate())

        noButtonBrush = QBrush(QColor(0, 0, 0, 255))
        noButtonBrush.setStyle(Qt.BrushStyle.DiagCrossPattern)
        noButton = QTableWidgetItem()
        noButton.setBackground(noButtonBrush)
        noButton.setFlags(
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEditable
            | Qt.ItemFlag.ItemIsDragEnabled
            | Qt.ItemFlag.ItemIsDropEnabled
            | Qt.ItemFlag.ItemIsUserCheckable
        )
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
        event.acceptProposedAction()

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        if event.mimeData().hasFormat("text/plain"):
            # Extract the template name from the drag object name
            templateName = event.source().objectName().replace("drag-", "")
            pos = event.position().toPoint()
            index: QModelIndex = self.indexAt(pos)
            if index.isValid():
                # TODO handle the drop logic here (load template, etc.)
                row = index.row()
                col = index.column()
                if (row == 0) or (col == 8):
                    return  # Ignore drops on autoMap cells
                item = self.item(row, col)
                if item is not None:
                    print(f"Template: {templateName}\nPosition: ({row-1}, {col})")
                    item.setBackground(QColor(200, 255, 200))  # Light green background to indicate filled cell
            event.acceptProposedAction()
