"""
Control your game with Launchpad
"""

import importlib.metadata
import sys

from PySide6 import QtWidgets, QtAsyncio
import launchpad_py as launchpad

from .ui_mainwindow import Ui_MainWindow
from .mainwindow import mainWindowScript


class Launkey(QtWidgets.QMainWindow):
    def __init__(self):
        super(Launkey, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.lpclose = None
    
    def set_close(self, close_flag: launchpad.Launchpad):
        self.lpclose = close_flag

    def closeEvent(self, event):
        # Zamknij launchpada przed zamknięciem aplikacji
        if self.lpclose is not None:
            try:
                self.lpclose.Reset()
                self.lpclose.Close()
                print("Launchpad disconnected successfully.")
            except Exception as e:
                print(f"Błąd przy zamykaniu Launchpada: {e}")
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

    QtWidgets.QApplication.setApplicationName(metadata["Launkey"])

    QtWidgets.QApplication(sys.argv)
    main_window = Launkey()
    main_window.show()
    mainWindowScript(main_window)
    sys.exit(QtAsyncio.run())
