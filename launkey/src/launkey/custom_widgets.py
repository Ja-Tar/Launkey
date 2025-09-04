from PySide6.QtWidgets import QGridLayout, QWidget, QPushButton, QSizePolicy, QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import Qt, QSize

class SquareButton(QPushButton):
    def __init__(self, text: str, parent: QWidget = None): # type: ignore
        super().__init__(text, parent)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.setMinimumSize(QSize(60, 60))

    def hasHeightForWidth(self) -> bool: # skipcq: PYL-R0201
        return True

    def heightForWidth(self, arg__1: int) -> int: # skipcq: PYL-R0201
        return arg__1

class PlusButton(SquareButton):
    def __init__(self, parent: QWidget = None): # type: ignore
        super().__init__("+", parent)
        self.setObjectName("plusButton")
        self.setMinimumSize(QSize(30, 30))
        self.setMaximumSize(QSize(50, 50))

class ToggleButton(SquareButton):
    def __init__(self, text: str, buttonID: str, parent: QWidget = None): # type: ignore
        super().__init__(text, parent)
        self.setObjectName("toggleButton")
        self.setCheckable(True)
        self.setChecked(False)
        self.setStyleSheet("border-color: darkgray; border-width: 1px;")
        self.toggled.connect(self.onToggled)

        self.buttonID = buttonID

    def onToggled(self, checked: bool):
        self.setStyleSheet("border: 5px solid lightblue; border-width: 5px;" if checked else "border-color: darkgray; border-width: 1px;")

    def getButtonID(self) -> str:
        return self.buttonID

    def checkToggle(self, buttonID: str):
        if self.buttonID != buttonID:
            self.setChecked(False)
        else:
            self.setChecked(True)

class TemplateOptionsList(QTreeWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        optionsListPolicy = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        optionsListPolicy.setHorizontalStretch(7)
        self.setSizePolicy(optionsListPolicy)
        self.setObjectName("optionsList")

        self.setHeaderLabels(["Option", "Value"])
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTreeWidget.SelectionBehavior.SelectRows)
        self.setEditTriggers(QTreeWidget.EditTrigger.NoEditTriggers)
        self.setRootIsDecorated(True)

    def loadDefaultOptions(self):
        pass