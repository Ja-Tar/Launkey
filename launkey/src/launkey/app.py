"""
Control your game with Launchpad
"""

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import keyboard


class Launkey(toga.App): # pylint: disable=inherit-non-class
    def startup(self):
        main_box = toga.Box(direction=COLUMN)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

        button = toga.Button("Click me", on_press=my_callback)
        test_input = toga.TextInput(placeholder="Type here", style=Pack(flex=1))
        main_box.add(button)
        main_box.add(test_input)

def my_callback(widget):
    keyboard.press_and_release("tab")


def main():
    return Launkey()
