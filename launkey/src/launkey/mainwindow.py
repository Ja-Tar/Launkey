import asyncio
from typing import TYPE_CHECKING, Optional
import keyboard
import launchpad_py as launchpad
#from PySide6 import QtAsyncio
from PySide6 import QtWidgets, QtGui

from .ui_dialogtemplates import Ui_Dialog

if TYPE_CHECKING:
    from .app import Launkey

class LaunchpadWrapper:
    def __init__(self):
        self.lp = launchpad.Launchpad()
        # (red, green) tuples for each LED on the launchpad
        # intensity from 0 to 3 for each color
        self.launchpad_display = [(0, 0)] * 64 
        self.launchpad_automap = [(0, 0)] * 16
        # first 8 LEDs are on the left and the next 8 LEDs are on the top

    def connect(self) -> bool:
        if self.lp.Check():
            self.lp.Open()
            self.lp.Reset()
            self.lp.ButtonFlush()
            return True
        return False

    def changeLedsRapid(self, frame: list[tuple], automap: Optional[list[tuple]] = None):
        if automap is None:
            automap = [(0, 0)] * 16
        combined_frame = frame + automap
        # format the frame for rapid update with LedGetColor()
        formatted_frame = [self.lp.LedGetColor(x, y) for x, y in combined_frame]
        self.lp.LedCtrlRawRapid(formatted_frame)
        self.lp.LedCtrlRawRapidHome()
        self.launchpad_display[:] = frame[:]
        self.launchpad_automap[:] = automap[:]

    def reset(self):
        self.lp.Reset()
        self.lp.ButtonFlush()

class GUITable:
    def __init__(self, main_window: "Launkey"):
        self.main_window = main_window

    async def sync(self, frame: list[tuple], automap: list[tuple]):
        # disable the table to prevent user interaction during updates
        self.main_window.ui.tableLaunchpad.setEnabled(False)
        self.main_window.ui.tableLaunchpad.clearSelection()

        while True:
            # Update the GUI table (move one row down)
            for row in range(8):
                for col in range(8):
                    value = frame[row * 8 + col]
                    item = QtWidgets.QTableWidgetItem()
                    # Set background color based on value (red, green)
                    r, g = value
                    color = QtGui.QColor(85 * r, 85 * g, 0)
                    item.setBackground(color)
                    self.main_window.ui.tableLaunchpad.setItem(row + 1, col, item)
            # Update the GUI table with automap values (right column)
            for row in range(8):
                value = automap[row]
                item = QtWidgets.QTableWidgetItem()
                r, g = value
                color = QtGui.QColor(85 * r, 85 * g, 0)
                item.setBackground(color)
                self.main_window.ui.tableLaunchpad.setItem(row + 1, 8, item)
            # Update the GUI table with automap values (top row)
            for col in range(8):
                value = automap[col + 8]
                item = QtWidgets.QTableWidgetItem()
                r, g = value
                color = QtGui.QColor(85 * r, 85 * g, 0)
                item.setBackground(color)
                self.main_window.ui.tableLaunchpad.setItem(0, col, item)

            await asyncio.sleep(0.05)

    def clear(self):
        for row in range(9):
            for col in range(9):
                if row == 0 and col == 8:
                    continue
                item = QtWidgets.QTableWidgetItem()
                item.setBackground(QtGui.QColor(255, 255, 255, 0))
                self.main_window.ui.tableLaunchpad.setItem(row, col, item)
        self.main_window.ui.tableLaunchpad.setEnabled(True)

def mainWindowScript(main_window: "Launkey"):
    # REMOVE for testing popup
    #openEditTemplatePopup(main_window)
    #return

    main_window.ui.buttonAddPreset.clicked.connect(lambda: openEditTemplatePopup(main_window))

    lpWrapper = LaunchpadWrapper()
    if lpWrapper.connect():
        main_window.ui.statusbar.showMessage("Launchpad connected")
        main_window.ui.tableLaunchpad.setEnabled(True)
        main_window.lpclose = lpWrapper.lp
    else:
        main_window.ui.statusbar.showMessage("Launchpad not found")
        main_window.ui.tableLaunchpad.setEnabled(False)
        QtWidgets.QMessageBox.critical(
            main_window,
            "Launchpad Error",
            "Launchpad not found. Please close the app to connect to the Launchpad."
        )
        return
    main_window.ui.buttonRun.clicked.connect(lambda: asyncio.ensure_future(buttonRun(main_window, lpWrapper)))
    main_window.ui.buttonRun.setEnabled(True)

async def buttonRun(main_window: "Launkey", lpWrapper: LaunchpadWrapper):
    gui_table = GUITable(main_window)
    if main_window.ui.buttonRun.text() == "Run":
        main_window.ui.buttonRun.setText("Stop")
        main_window.ui.statusbar.showMessage("Running...")
        asyncio.create_task(async_test(lpWrapper), name="async_test_loop") # REMOVE
        asyncio.create_task(gui_table.sync(), name="sync_table_loop")
        print("Started Launkey controller")
        return
    main_window.ui.buttonRun.setText("Run")
    main_window.ui.statusbar.showMessage("Stopped")
    # Stop the async loop and reset the launchpad
    for task in asyncio.all_tasks():
        if task.get_name() in ["async_test_loop", "sync_table_loop"]:
            task.cancel()
    lpWrapper.reset()
    gui_table.clear()

async def async_test(lpWrapper: LaunchpadWrapper, anim_time: float = 0.1):
    arrow_up_red = [
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 1, 1, 0, 0, 0,
        0, 0, 1, 3, 3, 1, 0, 0,
        0, 1, 3, 3, 3, 3, 1, 0,
        0, 0, 0, 3, 3, 0, 0, 0,
        0, 0, 0, 3, 3, 0, 0, 0,
        0, 0, 0, 3, 3, 0, 0, 0
    ]

    # Automap animation: przesuwający się pasek
    automap_length = 16
    automap_color = (0, 3)  # Zielony pasek
    automap_off = (0, 0)
    automap_pos = 0

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
            # Animacja automap: przesuwający się pojedynczy "piksel"
            automap = [(0, 0)] * automap_length
            # Ustaw pasek na odpowiedniej pozycji
            automap = [automap_color if i == automap_pos else automap_off for i in range(automap_length)]
            lpWrapper.changeLedsRapid(frame, automap)
            await asyncio.sleep(anim_time)
            automap_pos = (automap_pos + 1) % automap_length
        await asyncio.sleep(0.5)
        lpWrapper.reset()

def openEditTemplatePopup(main_window: "Launkey"):
    dialog = QtWidgets.QDialog(main_window)
    ui = Ui_Dialog()
    ui.setupUi(dialog)
    dialog.setWindowTitle("Edit Template")
    dialog.show()