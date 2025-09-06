from typing import Any, Tuple
from enum import Enum

class LED(Enum):
    FULL = 3
    MEDIUM = 2
    LOW = 1
    OFF = 0

class Button:
    def __init__(self, name: str, buttonID: str, location: Tuple[int, int]):
        self.name = name
        self.buttonID = buttonID
        self.location = location
        self.normalColor: Tuple[LED, LED] = (LED.FULL, LED.OFF)
        self.pushedColor: Tuple[LED, LED] = (LED.OFF, LED.FULL)
        self.keyboardCombo: str = ""

    def __str__(self) -> str:
        return f"Button(name={self.name}, location={self.location}, normalColor={self.normalColor}, pushedColor={self.pushedColor}, keyboardCombo={self.keyboardCombo})"

class Template:
    class Type(Enum):
        "This is main template type enum"
        BUTTONS = Button
        # TODO Add more types as needed

    def __init__(self, displayName: str, type: Type):
        self.displayName: str = displayName
        self.type: Template.Type = type

    def __str__(self) -> str:
        return f"Template(displayName={self.displayName}, type={self.type})"