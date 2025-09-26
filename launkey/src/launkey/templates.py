from typing import Any, Tuple, List
from enum import Enum, unique
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

def sterilizeTemplateName(name: str) -> str:
    # Replace spaces to underscores and remove invalid characters
    name = name.strip().replace(" ", "_")
    name = "".join(c for c in name if c.isalnum() or c in ('_', '-')).rstrip()
    return name

def recoverOriginalTemplateName(fileName: str) -> str:
    name = fileName.replace("_", " ")
    return name

@unique
class LED(Enum):
    FULL = 3
    MEDIUM = 2
    LOW = 1
    OFF = 0

LEDColorCodes = [
    ([LED.OFF, LED.OFF], "#000000"),
    ([LED.LOW, LED.OFF], "#ffcccc"),
    ([LED.MEDIUM, LED.OFF], "#ff8888"),
    ([LED.FULL, LED.OFF], "#ff0000"),
    ([LED.OFF, LED.LOW], "#ccffcc"),
    ([LED.OFF, LED.MEDIUM], "#88ff88"),
    ([LED.OFF, LED.FULL], "#00ff00"),
    ([LED.LOW, LED.LOW], "#ffffcc"),
    ([LED.MEDIUM, LED.MEDIUM], "#ffff88"),
    ([LED.FULL, LED.FULL], "#ffff00"),
    ([LED.MEDIUM, LED.LOW], "#ffd699"),
    ([LED.FULL, LED.MEDIUM], "#ffb366"),
    ([LED.FULL, LED.LOW], "#ff9900"),
    ([LED.LOW, LED.MEDIUM], "#ccff99"),
    ([LED.LOW, LED.FULL], "#99ff66"),
    ([LED.MEDIUM, LED.FULL], "#66ff33"),
]

def ledsToColorCode(leds: Tuple[LED, LED]) -> str:
    for led_pair, color in LEDColorCodes:
        if leds == tuple(led_pair):
            return color
    return "#000000"  # Default to black if not found

class TemplateItem:
    """Base class for items in a template"""
    def __init__(self, name: str, buttonID: str, location: Tuple[int, int]):
        self.name = name
        self.location = location
        self.buttonID = buttonID

    def __str__(self) -> str:
        return f"TemplateItem(name={self.name}, location={self.location}, buttonID={self.buttonID})"

    def toDict(self) -> dict[str, Any]:
        raise NotImplementedError("TemplateItem should not be used directly. Please use a subclass or another class that inherits from TemplateItem.")

class Button(TemplateItem):
    def __init__(
        self,
        name: str,
        buttonID: str,
        location: Tuple[int, int],
        /,
        normalColor: Tuple[LED, LED] = (LED.FULL, LED.OFF),
        pushedColor: Tuple[LED, LED] = (LED.OFF, LED.FULL),
        keyboardCombo: str = "",
    ):
        super().__init__(name, buttonID, location)
        self.normalColor: Tuple[LED, LED] = normalColor
        self.pushedColor: Tuple[LED, LED] = pushedColor
        self.keyboardCombo: str = keyboardCombo

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
    @unique
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
        return Button( # IDEA Maybe rework it?
            jsonData["name"],
            jsonData["buttonID"],
            tuple(jsonData["location"]),
            normalColor=(LED(jsonData["normalColor"][0]), LED(jsonData["normalColor"][1])),
            pushedColor=(LED(jsonData["pushedColor"][0]), LED(jsonData["pushedColor"][1])),
            keyboardCombo=jsonData["keyboardCombo"]
        )
    elif objType == "Template":
        return Template(
            name=jsonData["name"],
            type=Template.Type[jsonData["type"]]
        )
    
    raise ValueError(f"Unknown object type: {objType}")

def checkTemplate(templateData: list[Template | TemplateItem]) -> bool:
    if not templateData:
        return False
    elif not any(isinstance(item, Template) for item in templateData):
        raise ValueError("No Template object found in the file.")
    elif not all(isinstance(item, (Template, TemplateItem)) for item in templateData):
        raise ValueError("File contains invalid objects.")
    return True

def getTemplateType(template: List[Template | TemplateItem]) -> Template.Type | None:
    if not template:
        return None
    for item in template:
        if isinstance(item, Template):
            return item.type
    return None

# Loaded templates variable
loadedTemplates: dict[str, List[Template | TemplateItem]] = {}
