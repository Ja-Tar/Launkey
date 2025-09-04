from enum import Enum
from typing import TYPE_CHECKING, Optional
from typing import Any
from PySide6.QtWidgets import QWidget, QSizePolicy, QTreeWidget, QTreeWidgetItem, QComboBox, QLineEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QColor, QIcon

from .templates import Template, LED, Button

if TYPE_CHECKING:
    from .custom_layouts import TemplateGridLayout

class StringEditWidget(QLineEdit):
    def __init__(self, text: str, property: str, objectToChange: object, parent: QWidget | None = None):
        super().__init__(text, parent)
        self.setObjectName("textEditWidget")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.editingFinished.connect(lambda: self.changeObjectProperty(objectToChange, property, self.text()))

    def changeObjectProperty(self, objectToChange: object, property: str, newValue: Any):
        print(f"Changing string {property} to {newValue}")
        setattr(objectToChange, property, newValue)

class NameEditWidget(StringEditWidget):

    def __init__(
        self,
        text: str,
        property: str,
        objectToChange: object,
        gridLayout: "TemplateGridLayout",
        parent: QWidget | None = None,
    ):
        super().__init__(text, property, objectToChange, parent)
        self.gridLayout = gridLayout
        self.setObjectName("nameEditWidget")
        self.editingFinished.disconnect()
        self.editingFinished.connect(lambda: self.changeObjectProperty(objectToChange, property, self.text()))

    def changeObjectProperty(self, objectToChange: object, property: str, newValue: Any):
        if not newValue.strip():
            print("Name cannot be empty.")
            self.setText(getattr(objectToChange, property))
            return
        super().changeObjectProperty(objectToChange, property, newValue)
        button_id = getattr(objectToChange, "buttonID", None)
        if button_id:
            self.gridLayout.updateButtonText(button_id, newValue)


class EnumEditWidget(QComboBox):
    def __init__(self, currentValue: Enum, property: str, objectToChange: object, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("enumEditWidget")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        enumType = type(currentValue)
        for value in enumType:
            self.addItem(value.name, value)

        self.setCurrentText(currentValue.name)
        self.currentIndexChanged.connect(lambda _: self.changeObjectProperty(objectToChange, property, self.currentData()))

    def changeObjectProperty(self, objectToChange: object, property: str, newValue: Any):
        print(f"Changing enum {property} to {newValue}")
        setattr(objectToChange, property, newValue)

class ButtonColorSelector(QComboBox):
    def __init__(self, currentValue: tuple[int, int], property: str, objectToChange: object, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("buttonColorSelector")
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setIconSize(QPixmap(20, 20).size())
        self.setFixedWidth(50)

        color_options = [
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

        for value, color in color_options:
            pixmap = QPixmap(20, 20)
            pixmap.fill(QColor(color))
            icon = QIcon(pixmap)
            self.addItem(icon, "", value)
        index = self.findData(list(currentValue))
        self.setCurrentIndex(index)
        self.currentIndexChanged.connect(lambda _: self._changeObjectProperty(objectToChange, property, tuple(self.currentData())))

    def _changeObjectProperty(self, objectToChange: object, property: str, newValue: Any):
        print(f"Changing color {property} to {newValue}")
        setattr(objectToChange, property, newValue)

    def getColorValue(self) -> tuple[int, int]:
        return self.currentData()  # type: ignore

class TemplateOptionsList(QTreeWidget):
    propertyIgnoreList = ["location", "buttonID"]

    def __init__(self, template_type: Template.Type, parent: QWidget | None = None):
        super().__init__(parent)
        optionsListPolicy = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        optionsListPolicy.setHorizontalStretch(7)
        self.setSizePolicy(optionsListPolicy)
        self.setObjectName("optionsList")

        self.setHeaderLabels(["Option", "Value"])
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QTreeWidget.SelectionMode.NoSelection)
        self.setEditTriggers(QTreeWidget.EditTrigger.NoEditTriggers)
        self.setRootIsDecorated(True)
        self.setItemsExpandable(True)
        self.setExpandsOnDoubleClick(True)

        self.gridLayout: Optional["TemplateGridLayout"] = None
        self.loadDefaultOptions(template_type)

        self.template: Template
        self.templateChildren: dict[str, object] = {}
        self.selectedChildID: str = ""
        self.mainChildID: str = ""
        self.templateType = template_type

    def getWidgetForType(self, objectToChange: object, property: str, value: Any) -> QWidget:
        if property == "name" and self.gridLayout is not None:
            return NameEditWidget(value, property, objectToChange, self.gridLayout)
        elif isinstance(value, str):
            return StringEditWidget(value, property, objectToChange)
        elif isinstance(value, Enum):
            return EnumEditWidget(value, property, objectToChange)
        elif isinstance(value, tuple) and all(isinstance(i, LED) for i in value) and len(value) == 2:
            return ButtonColorSelector(value, property, objectToChange)
        else:
            raise NotImplementedError(f"Unsupported property type: {type(value)}")

    def _addOptions(self, obj: object, title: str) -> None:
        objVars = vars(obj).copy()
        for prop in self.propertyIgnoreList:
            if prop in objVars:
                del objVars[prop]
        topWidget = QTreeWidgetItem([title], type=0)
        self.addTopLevelItem(topWidget)

        for option, value in objVars.items():
            widget = self.getWidgetForType(obj, option, value)
            item = QTreeWidgetItem([option], type=1)
            topWidget.addChild(item)
            self.setItemWidget(item, 1, widget)

        self.expandItem(topWidget)

    def templateTypeOptions(self, template: Template) -> None:
        self._addOptions(template, "Template settings")

    def childTypeOptions(self, child: object) -> None:
        self._addOptions(child, f"{type(child).__name__} settings")

    def loadDefaultOptions(self, template_type: Template.Type) -> None:
        # get options from template class
        self.clear()
        self.setStyleSheet(
            """
            QTreeView::item:selected {
            }

            QTreeView::item:hover {
            }

            QTreeView::item:hover:selected {
            }
            """
        )

        self.template = Template(name="Example", type=template_type)
        self.templateTypeOptions(self.template)
        self.resizeColumnToContents(0)
        self.header().setStretchLastSection(True)

    def addChild(self, childID: str, location: tuple[int, int], main: bool = False) -> None:
        child = self.templateType.value(name=f"Button {len(self.templateChildren) + 1}", buttonID=childID, location=location)
        self.templateChildren[childID] = child
        if main or not self.mainChildID:
            self.mainChildID = childID

    def selectChild(self, childID: str) -> None:
        if childID not in self.templateChildren:
            raise ValueError(f"Child ID {childID} not found in template children.")
        self.selectedChildID = childID
        self.clear()
        self.templateTypeOptions(self.template)
        if childID in self.templateChildren:
            self.childTypeOptions(self.templateChildren[childID])
        self.resizeColumnToContents(0)
        self.header().setStretchLastSection(True)

    def deleteChild(self, childID: str) -> None:
        if childID in self.templateChildren and childID != self.mainChildID:
            del self.templateChildren[childID]
            self.clear()
            self.templateTypeOptions(self.template)
            self.resizeColumnToContents(0)
            self.header().setStretchLastSection(True)

    def getObjects(self) -> list[object]:
        return [self.template] + list(self.templateChildren.values())
