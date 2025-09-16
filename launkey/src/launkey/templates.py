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

    def toDict(self) -> dict[str, Any]:
        return {
            "__type__": "Button",
            "name": self.name,
            "buttonID": self.buttonID,
            "location": self.location,
            "normalColor": (self.normalColor[0].value, self.normalColor[1].value),
            "pushedColor": (self.pushedColor[0].value, self.pushedColor[1].value),
            "keyboardCombo": self.keyboardCombo
        }

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
    
    def toDict(self) -> dict[str, Any]:
        return {
            "__type__": "Template",
            "name": self.name,
            "type": self.type.name
        }

def objectFromJson(jsonData: dict[str, Any]) -> Template | Button:
    objType = jsonData.get("__type__")

    if objType == "Button":
        return Button(
            name=jsonData["name"],
            buttonID=jsonData["buttonID"],
            location=tuple(jsonData["location"]),
        )
    elif objType == "Template":
        return Template(
            name=jsonData["name"],
            type=Template.Type[jsonData["type"]]
        )
    
    raise ValueError(f"Unknown object type: {objType}")