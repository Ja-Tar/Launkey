from PySide6.QtWidgets import QGridLayout, QWidget, QPushButton, QSizePolicy, QSpacerItem
from PySide6.QtCore import Qt, QSize

class SquareButton(QPushButton):
    def __init__(self, text: str, parent: QWidget = None): # type: ignore
        super().__init__(text, parent)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.setMinimumSize(QSize(10, 10))

    def hasHeightForWidth(self) -> bool: # skipcq: PYL-R0201
        return True

    def heightForWidth(self, arg__1: int) -> int: # skipcq: PYL-R0201
        return arg__1

class PlusButton(SquareButton):
    def __init__(self, parent: QWidget = None): # type: ignore
        super().__init__("+", parent)