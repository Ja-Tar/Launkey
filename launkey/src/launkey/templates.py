from typing import Any, Tuple
from enum import Enum
from pathlib import Path
from PySide6.QtCore import QStandardPaths

def ensureTemplatesFolderExists(systemPath: str) -> Path:
    folderName = "Launkey_Templates"
    fullPath = Path(systemPath) / folderName
    if not fullPath.exists():
        fullPath.mkdir(parents=True, exist_ok=True)
        print(f"Created folder: {fullPath}")
    return fullPath

def getTemplateFolderPath() -> Path:
    pathOnSystem = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    fullPath = ensureTemplatesFolderExists(pathOnSystem)
    return fullPath

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

    def __init__(self, name: str, type: Type): # skipcq: PYL-W0622
        self.name: str = name
        self.type: Template.Type = type

    def __str__(self) -> str:
        return f"Template(name={self.name}, type={self.type})"