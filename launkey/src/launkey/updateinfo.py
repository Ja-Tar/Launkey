from typing import TYPE_CHECKING, Any

import sys
import requests

from datetime import date, timedelta
from importlib import metadata as importlibMetadata
from enum import Enum, unique, auto

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QMessageBox, QInputDialog
from PySide6.QtGui import QDesktopServices

@unique
class OS(Enum):
    windows = auto()
    linux = auto()

class FileToOS(Enum):
    rpm = OS.linux
    deb = OS.linux
    msi = OS.windows

if TYPE_CHECKING:
    from .app import Launkey

class UpdateManager:
    def __init__(self, main_window: "Launkey") -> None:
        self.main_window = main_window
        self.settingLoader = QSettings("Ja-Tar", "Launkey")
        self.errors: list[str] = self.settingLoader.value("update/errors", [])  # type: ignore
        self.lastChecked: date = self.settingLoader.value("update/lastChecked") # type: ignore
        self.assets: list[dict] = []
        self.installedVersion: str
        self.newestVersion: str
        
        if not self.errors or not self.lastChecked:
            self.errors = []
            self.lastChecked = date.fromtimestamp(0)

    async def updateNeeded(self, manual: bool):
        # This needs to:
        # [x] send a signal to github API
        # [x] receive information and add it to object variable
        # [x] check if current version is the same as received one
        # [x] save that version was checked on <DATE>
        # [x] count how many times error occurred
        # [x] inform about errors when more then 5 is counted

        if self.lastChecked and date.today() - timedelta(days=2) < self.lastChecked and not manual:
            print("Update has been checked in last 2 days")
            return False
        elif self.errors and len(self.errors) >= 5:
            messagebox = QMessageBox(
                QMessageBox.Icon.Critical,
                "Update Error",
                f"Checking for updates failed {len(self.errors)} times!",
                buttons=QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Retry,
                detailedText="\n".join(self.errors),
                parent=self.main_window
            )
            if messagebox.exec() == QMessageBox.StandardButton.Ok:
                return False

        print("Checking for updates")

        req = requests.get('https://api.github.com/repos/Ja-Tar/Launkey/releases/latest')
        if req.status_code != 200:
            self.errors.append(f"Failed to get info from github, code: {req.status_code}")
            return False
        json = req.json()

        self.newestVersion = json.get("tag_name", "")
        for asset in json.get("assets", []):
            fileEndings = tuple(e for e in FileToOS.__members__ if FileToOS[e].value == self.main_window.currentOS)
            for ending in fileEndings:
                if str(asset["name"]).endswith(ending):
                    cutAsset = {
                        "name": asset["name"],
                        "browser_download_url": asset["browser_download_url"]
                        }
                    self.assets.append(cutAsset)

        if len(self.assets) < 1:
            self.errors.append("Failed to get newest assets. Check again later.")
            return False

        app_module = sys.modules['__main__'].__package__
        if app_module:
            metadata = importlibMetadata.metadata(app_module)
            self.installedVersion = metadata["version"]
        else:
            self.errors.append("Failed to get __package__ info.")
            return False

        # Check is working
        self.lastChecked = date.today()
        self.errors.clear()

        if self.newestVersion != self.installedVersion:
            return True
        return False # No update needed

    def saveData(self):
        self.settingLoader.beginGroup("update")
        self.settingLoader.setValue("lastChecked", self.lastChecked)
        self.settingLoader.setValue("errors", self.errors)
        self.settingLoader.endGroup()

    def displayUpdatePopup(self):
        messagebox = QMessageBox(
            QMessageBox.Icon.Question,
            "Update",
            f"New update available {self.installedVersion} -> {self.newestVersion}.\nDownload?",
            buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            parent=self.main_window
        )
        if messagebox.exec() == QMessageBox.StandardButton.Yes:
            if self.main_window.currentOS == OS.windows:
                if len(self.assets) == 1:
                    QDesktopServices.openUrl(self.assets[0]["browser_download_url"])
                else:
                    self.errors.append(f"Wrong asset count for windows found: {len(self.assets)}")
                    raise NotImplementedError("Wrong asset count for windows!!!")
            elif self.main_window.currentOS == OS.linux:
                if len(self.assets) == 1:
                    QDesktopServices.openUrl(self.assets[0]["browser_download_url"])
                else:
                    items = [e["name"] for e in self.assets]
                    item, ok = QInputDialog.getItem(
                        self.main_window,
                        "Update",
                        "Choose file to download:",
                        items,
                        editable=False
                    )
                    if ok:
                        QDesktopServices.openUrl(self.assets[items.index(item)]["browser_download_url"])
        else:
            messagebox2 = QMessageBox(
                QMessageBox.Icon.Information,
                "Update",
                "Updates will be checked again in 2 days",
                parent=self.main_window,
            )
            messagebox2.exec()

async def checkForUpdates(main_window: "Launkey", /, manual: bool = False):
    um = UpdateManager(main_window)
    
    if await um.updateNeeded(manual):
        um.displayUpdatePopup()
    elif manual:
        messagebox = QMessageBox(
            QMessageBox.Icon.Information,
            "Update",
            "This is the newest version",
            parent=main_window
        )
        messagebox.exec()
    um.saveData()
