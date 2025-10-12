from enum import Enum, auto, unique

@unique
class AppTheme(Enum):
    system = 0
    white = auto()
    dark = auto()
    magic = auto()