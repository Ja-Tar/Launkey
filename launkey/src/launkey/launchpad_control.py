from typing import TYPE_CHECKING, Optional, Any

import asyncio
import launchpad_py as launchpad

from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtGui import QColor

if TYPE_CHECKING:
    from .app import Launkey

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