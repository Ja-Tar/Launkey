from enum import Enum, auto, unique

@unique
class AppTheme(Enum):
    normal = auto()
    dark = auto()
    magic = auto()