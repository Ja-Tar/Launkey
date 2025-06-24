"""
Control your game with Launchpad
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import keyboard 
#TODO: Add root check on LINUX
#TODO: Test on macOS

class Launkey(toga.App): # pylint: disable=inherit-non-class
    def startup(self):
        main_box = toga.Box(direction=COLUMN)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

        #TODO: Add interface


def main():
    return Launkey()
