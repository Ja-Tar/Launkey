from typing import TYPE_CHECKING

from enum import Enum, auto, unique
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QPalette, QColor, QStyleHints, QGuiApplication

if TYPE_CHECKING:
    from .app import Launkey

@unique
class AppTheme(Enum):
    default = 0
    system = auto()
    light = auto()
    dark = auto()
    magic = auto()
    
class Theme:
    themeID: AppTheme
        
    def getPalette(self):
        raise ValueError("Theme class should not be used directly. Please use a subclass or another class that inherits from Theme.")

class Magic(Theme):
    themeID = AppTheme.magic
        
    palette = QPalette()
    
    palette.setColor(QPalette.ColorRole.Window, QColor("#472542"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#30202E"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#350F2F"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#44003B"))
    palette.setColor(QPalette.ColorRole.Accent, QColor("#BD24A8"))
    
def loadTheme(main_window: "Launkey"):
    #print("Change to: " + themeID.name)
    
    settingLoader = QSettings("Ja-Tar", "Launkey")
    themeID = AppTheme(settingLoader.value("Appearance/Theme", AppTheme.system.value, int))
    
    print()
    
    if themeID == AppTheme.default:
        QGuiApplication.setPalette(QPalette())
        
    if themeID == AppTheme.system:
        colorHint = QStyleHints.colorScheme(QGuiApplication.styleHints())
        if colorHint == Qt.ColorScheme.Dark:
            themeID = AppTheme.dark
        else:
            themeID = AppTheme.light
        
    match themeID:
        case AppTheme.light:
            print(AppTheme.light.name)
        case AppTheme.dark: 
            pass
        case AppTheme.magic:
            QGuiApplication.setPalette(Magic.palette)
    
    