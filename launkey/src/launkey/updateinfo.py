import asyncio

from typing import TYPE_CHECKING

from PySide6.QtCore import QByteArray, QJsonDocument
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

if TYPE_CHECKING:
    from .app import Launkey
    
class NetworkMWrapper():
    def __init__(self, /, timeout: int = 100) -> None:
        self.networkM = QNetworkAccessManager()
        self.timeout = timeout # min 10 milliseconds 
        
    async def getData(self, networkRequest: QNetworkRequest):
        request = self.networkM.get(networkRequest)
        i = 0
        while not request.finished:
            await asyncio.sleep(0.01)
            i += 1
            if i > self.timeout:
                return self.handleNetworkData(request)
    
    def handleNetworkData(self, networkReplay: QNetworkReply):
        if networkReplay.error() == QNetworkReply.NetworkError.NoError:
            response: QByteArray = networkReplay.readAll()
        networkReplay.deleteLater()
    
class UpdateManager:
    def __init__(self, main_window: "Launkey") -> None:
        main_window = main_window
    
    async def updateNeeded(self) -> bool:
        # This needs to:
        # [ ] send a signal to github API 
        # [ ] receive information and add it to object variable
        # [ ] and finally check if current version is the same as received one
        
        nm = NetworkMWrapper()
        data = await nm.getData(QNetworkRequest("https://api.restful-api.dev/objects/7"))
        
    
    def displayUpdatePopup(self):
        pass

async def checkForUpdates(main_window: "Launkey"):
    print("Checking for updates")
    
    um = UpdateManager(main_window)
    
    if await um.updateNeeded():
        um.displayUpdatePopup()