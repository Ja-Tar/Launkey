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

        buttons_box = toga.Box(direction=COLUMN, style=Pack(margin=5, flex=1))
        
        max_rows = 8
        max_columns = 8

        self.buttons = []
        for row in range(max_rows):
            row_box = toga.Box(direction=ROW, style=Pack(margin=5, flex=1))
            for column in range(max_columns):
                button = toga.Button(
                    f"Button {row * max_columns + column + 1}",
                    on_press=self.button_pressed,
                    style=Pack(margin=5, height=60, flex=1)
                )
                row_box.add(button)
                self.buttons.append(button)
            buttons_box.add(row_box)

        main_box.add(buttons_box)

    def button_pressed(self, widget: toga.Button):
        #keyboard.press_and_release("tab")
        print(f"Button {widget.text} pressed")


def main():
    return Launkey()
