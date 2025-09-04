from typing import Any, Tuple
from enum import Enum

class LED(Enum):
    FULL = 3
    MEDIUM = 2
    LOW = 1
    OFF = 0

class Button:
    def __init__(self, name: str, launchpadKey: Tuple[int, int], keyboardCombo: str):
        self.name = name
        self.launchpadKey = launchpadKey
        self.keyColor: Tuple[LED, LED] = (LED.OFF, LED.OFF)
        self.keyboardCombo = keyboardCombo

    def __str__(self) -> str:
        return f"Button(name={self.name}, launchpadKey={self.launchpadKey}, keyColor={self.keyColor}, keyboardCombo={self.keyboardCombo})"

class Template:
    class Type(Enum):
        "This is main template type enum"
        BUTTONS = Button
        # TODO Add more types as needed

    def __init__(self, name: str, type: Type):
        self.name: str = name
        self.type: Template.Type = type

    def __str__(self) -> str:
        return f"Template(name={self.name}, type={self.type})"