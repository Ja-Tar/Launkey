import asyncio
from typing import TYPE_CHECKING, Optional
import keyboard
import launchpad_py as launchpad
from PySide6 import QtAsyncio
from PySide6 import QtWidgets, QtGui

if TYPE_CHECKING:
    from .app import Launkey

# (red, green) tuples for each LED on the launchpad
# intensity from 0 to 3 for each color
launchpad_display = [(0, 0)] * 64
launchpad_automap = [(0, 0)] * 16
# first 8 LEDs are on the left and the next 8 LEDs are on the top

def run_MainWindow(main_window: "Launkey"):
    """
    Run the main window of the application.
    """
    lp = launchpad.Launchpad()
    print(lp.ListAll("Launchpad"))
    lp.Open()
    lp.Reset()
    lp.ButtonFlush()
    QtAsyncio.run(main_async_loop(lp, main_window))
    print("Launkey started")

async def main_async_loop(lp: launchpad.Launchpad, main_window: "Launkey"):
    """
    Main asynchronous loop for the application.
    """
    # Start the async test
    asyncio.create_task(async_test(lp))
    
    # Start the sync table
    asyncio.create_task(sync_table(main_window))

def change_leds_rapid(lp: launchpad.Launchpad, frame: list[tuple], automap: Optional[list[tuple]] = None):
    """
    Change the LEDs on the launchpad rapidly.
    """
    if automap is None:
        automap = [(0, 0)] * 16
    combined_frame = frame + automap
    # format the frame for rapid update with LedGetColor()
    formatted_frame = [lp.LedGetColor(x, y) for x, y in combined_frame]
    lp.LedCtrlRawRapid(formatted_frame)
    lp.LedCtrlRawRapidHome()
    launchpad_display[:] = frame[:]
    launchpad_automap[:] = automap[:]

async def async_test(lp: launchpad.Launchpad, anim_time: float = 0.1, automap_anim_time: float = 0.15):
    """
    Test the asynchronous functionality of the application.
    """
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
            change_leds_rapid(lp, frame, automap)
            await asyncio.sleep(anim_time)
            automap_pos = (automap_pos + 1) % automap_length
        await asyncio.sleep(0.5)
        lp.Reset()

async def sync_table(main_window):
    """
    Synchronize the GUI table with the launchpad.
    """
    while True:
        # Update the GUI table (move one row down)
        for row in range(8):
            for col in range(8):
                value = launchpad_display[row * 8 + col]
                item = QtWidgets.QTableWidgetItem()
                # Set background color based on value (red, green)
                r, g = value
                color = QtGui.QColor(85 * r, 85 * g, 0)
                item.setBackground(color)
                main_window.ui.tableLaunchpad.setItem(row + 1, col, item)
        # Update the GUI table with automap values (right column)
        for row in range(8):
            value = launchpad_automap[row]
            item = QtWidgets.QTableWidgetItem()
            r, g = value
            color = QtGui.QColor(85 * r, 85 * g, 0)
            item.setBackground(color)
            main_window.ui.tableLaunchpad.setItem(row + 1, 8, item)
        # Update the GUI table with automap values (top row)
        for col in range(8):
            value = launchpad_automap[col + 8]
            item = QtWidgets.QTableWidgetItem()
            r, g = value
            color = QtGui.QColor(85 * r, 85 * g, 0)
            item.setBackground(color)
            main_window.ui.tableLaunchpad.setItem(0, col, item)

        await asyncio.sleep(0.05)