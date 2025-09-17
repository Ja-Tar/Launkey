import importlib.metadata
import sys
import asyncio
import keyboard
import logging
import json

from typing import TYPE_CHECKING, Optional, Any
from PySide6 import QtAsyncio
from PySide6.QtCore import (QEvent, Qt)
from PySide6.QtWidgets import (QApplication, QInputDialog, QTableWidgetItem, QMessageBox, QDialog)
from PySide6.QtGui import (QColor)
import launchpad_py as launchpad

from .ui_mainwindow import Ui_MainWindow
from .ui_dialogtemplates import Ui_Dialog
from .custom_widgets import QDialogNoDefault, TemplateDisplay
from .templates import Template, getTemplateFolderPath, objectFromJson, TemplateItem

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

def mainWindowScript(main_window: "Launkey"):
    main_window.ui.buttonAddTemplate.clicked.connect(lambda: newTemplatePopup(main_window))
    loadTemplates(main_window)

    lpWrapper = LaunchpadWrapper(main_window)
    if lpWrapper.connect():
        main_window.ui.statusbar.showMessage("Launchpad connected")
        main_window.lpclose = lpWrapper.lp
    else:
        main_window.ui.statusbar.showMessage("Launchpad not found")
        QMessageBox.critical(
            main_window,
            "Launchpad Error",
            "Launchpad not found. Please close the app to connect to the Launchpad."
        )
        return
    main_window.ui.buttonRun.clicked.connect(lambda: asyncio.ensure_future(buttonRun(main_window, lpWrapper)))
    main_window.ui.buttonRun.setEnabled(True)

def loadTemplates(main_window: "Launkey"):
    template_files = getTemplateFileList()
    for template_file in template_files:
        try:
            with open(getTemplateFolderPath() / template_file, "r") as f:
                templateJsonData: list[dict[str, Any]] = json.load(f)
            templateData: list[Template | TemplateItem] = []
            for obj in templateJsonData:
                template = objectFromJson(obj)
                if template:
                    templateData.append(template)
            button = TemplateDisplay(templateData, main_window)
            main_window.ui.gridLayoutTemplates.addWidget(button)
        except Exception as e:
            message = f"Error loading template from {template_file}: {e}"
            messagebox = QMessageBox(QMessageBox.Icon.Critical, "Template Load Error", message, parent=main_window)
            messagebox.exec()

def getTemplateFileList() -> list[str]:
    folderPath = getTemplateFolderPath()
    return [f.name for f in folderPath.iterdir() if f.is_file() and f.suffix == ".json"]


async def buttonRun(main_window: "Launkey", lpWrapper: LaunchpadWrapper):
    if main_window.ui.buttonRun.text() == "Run":
        main_window.ui.buttonRun.setText("Stop")
        main_window.ui.statusbar.showMessage("Running...")
        lpWrapper.start_sync()
        asyncio.create_task(async_test(lpWrapper), name="async_test_loop") # REMOVE
        print("Started Launkey controller")
        return
    main_window.ui.buttonRun.setText("Run")
    main_window.ui.statusbar.showMessage("Stopped")
    # Stop the async loop and reset the launchpad
    for task in asyncio.all_tasks():
        if task.get_name() in ["async_test_loop", "sync_table_loop"]:
            task.cancel()
    lpWrapper.stop()

async def async_test(lpWrapper: LaunchpadWrapper, anim_time: float = 0.1): # REMOVE
    arrow_up_red = [
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 1, 1, 0, 0, 0,
        0, 0, 1, 3, 3, 1, 0, 0,
        0, 1, 3, 3, 3, 3, 1, 0,
        0, 0, 0, 3, 3, 0, 0, 0,
        0, 0, 0, 3, 3, 0, 0, 0,
        0, 0, 0, 3, 3, 0, 0, 0
    ]

    # autoMap animation: przesuwający się pasek
    autoMap_length = 16
    autoMap_color = (0, 3)  # Zielony pasek
    autoMap_off = (0, 0)
    autoMap_pos = 0

    while True:
        # Animate arrow moving up from bottom to top
        for row in range(6, -1, -1):
            frame = [(0, 0)] * 64
            # Copy the arrow shape into the current row
            for i in range(8):
                if row + i < 7:
                    for j in range(8):
                        dx = (row + i) * 8 + j
                        arrow_idx = i * 8 + j
                        if arrow_up_red[arrow_idx]:
                            frame[dx] = (arrow_up_red[arrow_idx], 0)
            # Animacja autoMap: przesuwający się pojedynczy "piksel"
            autoMap = [(0, 0)] * autoMap_length
            # Ustaw pasek na odpowiedniej pozycji
            autoMap = [autoMap_color if i == autoMap_pos else autoMap_off for i in range(autoMap_length)]
            lpWrapper.changeLedsRapid(frame, autoMap) # type: ignore
            await asyncio.sleep(anim_time)
            autoMap_pos = (autoMap_pos + 1) % autoMap_length
        await asyncio.sleep(0.5)
        lpWrapper.reset()

def selectTemplateTypePopup(main_window: "Launkey"):
    popup = QInputDialog(main_window)
    template_type, ok = popup.getItem(
        main_window,
        "Select Template Type",
        "Select the type of template you want to create:",
        template_types := [t.name for t in Template.Type],
        current=0,
        editable=False,
        flags=Qt.WindowType.WindowStaysOnTopHint
    )

    if not ok:
        return None
    return Template.Type[template_type]

def newTemplatePopup(main_window: "Launkey"):
    template_type = selectTemplateTypePopup(main_window)
    if template_type is None:
        return

    dialog = QDialogNoDefault(main_window)
    ui = Ui_Dialog()
    ui.setupUi(dialog, template_type)
    dialog.setWindowTitle("New Template")
    dialog.show()

    if dialog.exec() == QDialogNoDefault.DialogCode.Accepted:
        # TODO load template data into the main window
        print("Template saved")

def editTemplatePopup(main_window: "Launkey"):
    # TODO load template data into the dialog, with the ability to edit and save changes
    #dialog = QDialogNoDefault(main_window)
    #ui = Ui_Dialog()
    #ui.setupUi(dialog) # FIX
    #dialog.setWindowTitle("Edit Template")
    #dialog.show()
    pass