"""
Control your game with Launchpad
"""
import importlib.metadata
import sys
import os

from PySide6 import QtAsyncio
from PySide6.QtCore import (QEvent)
from PySide6.QtWidgets import (QApplication, QMainWindow, QMessageBox)
from PySide6.QtGui import (QIcon, QPixmap)
import launchpad_py as launchpad

from .icon import icon
from .ui_mainwindow import Ui_MainWindow
from .mainwindow import mainWindowScript
from .updateinfo import OS

def relaunchAsRoot() -> bool:
    if os.geteuid() != 0: # type: ignore
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText("Root access for shortcuts is required. Relaunch as root?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if msg.exec() == QMessageBox.StandardButton.Yes:
            os.execvp("sudo", ["sudo", sys.executable] + sys.argv)
        else:
            return False
    return True # with root 

def checkForLinux() -> bool:
    if sys.platform in ("linux", "linux2"):
        return True
    return False

class Launkey(QMainWindow):
    def __init__(self, root: bool, currentOS: OS):
        super(Launkey, self).__init__()
        self.ui = Ui_MainWindow()
        self.root = root
        self.currentOS = currentOS
        self.ui.setupUi(self)
        self.lpclose = None
    
    def set_close(self, close_flag: launchpad.Launchpad):
        self.lpclose = close_flag

    def closeEvent(self, event: QEvent):
        # Zamknij launchpada przed zamknięciem aplikacji
        if self.lpclose is not None:
            try:
                self.lpclose.Reset()
                self.lpclose.Close()
                print("Launchpad disconnected successfully.")
            except Exception as e:
                print(f"ERR: {e}")
        event.accept()


def main():
    # Linux desktop environments use an app's .desktop file to integrate the app
    # in to their application menus. The .desktop file of this app will include
    # the StartupWMClass key, set to app's formal name. This helps associate the
    # app's windows to its menu item.
    #
    # For association to work, any windows of the app must have WMCLASS property
    # set to match the value set in app's desktop file. For PySide6, this is set
    # with setApplicationName().

    # Find the name of the module that was used to start the app
    app_module = sys.modules["__main__"].__package__ 
    # Retrieve the app's metadata
    metadata = importlib.metadata.metadata(app_module or "launkey")

    QApplication.setApplicationName(metadata["Launkey"])

    QApplication(sys.argv)

    if checkForLinux():
        root = relaunchAsRoot()
        currentOS = OS.linux
    else:
        root = True
        currentOS = OS.windows

    main_window = Launkey(root, currentOS)
    loadAppIcon(main_window)
    main_window.show()
    sys.exit(QtAsyncio.run(mainWindowScript(main_window)))

def loadAppIcon(main_window: "Launkey"):
    pixmap = QPixmap()
    pixmap.loadFromData(icon)
    appIcon = QIcon(pixmap)
    main_window.setWindowIcon(appIcon)
