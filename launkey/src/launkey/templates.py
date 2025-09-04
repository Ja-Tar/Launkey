from typing import Tuple
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

class Template:
    class Type(Enum):
        BUTTON = Button
        # TODO Add more types as needed

    def __init__(self, name: str, type: Type):
        self.name = name
        self.type = type