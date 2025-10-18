from typing import TYPE_CHECKING, Any

import sys
import requests

from datetime import date, timedelta
from importlib import metadata as importlibMetadata

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QDesktopServices

if TYPE_CHECKING:
    from .app import Launkey

class UpdateManager:
    def __init__(self, main_window: "Launkey") -> None:
        self.main_window = main_window
        self.settingLoader = QSettings("Ja-Tar", "Launkey")
        self.errors: list[str] = self.settingLoader.value("update/errors", []) # type: ignore
        self.lastChecked: date = self.settingLoader.value("update/lastChecked") # type: ignore
        self.installedVersion: str
        self.newestVersion: str
        self.assets: list[dict]

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
        elif len(self.errors) >= 5:
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

        # req = requests.get('https://api.github.com/repos/Ja-Tar/Launkey/releases/latest')
        # TODO add error count
        # self.json = req.json()

        json = {
            "url": "https://api.github.com/repos/Ja-Tar/Launkey/releases/253932902",
            "assets_url": "https://api.github.com/repos/Ja-Tar/Launkey/releases/253932902/assets",
            "upload_url": "https://uploads.github.com/repos/Ja-Tar/Launkey/releases/253932902/assets{?name,label}",
            "html_url": "https://github.com/Ja-Tar/Launkey/releases/tag/0.2.0",
            "id": 253932902,
            "author": {
                "login": "Ja-Tar",
                "id": 78786298,
                "node_id": "MDQ6VXNlcjc4Nzg2Mjk4",
                "avatar_url": "https://avatars.githubusercontent.com/u/78786298?v=4",
                "gravatar_id": "",
                "url": "https://api.github.com/users/Ja-Tar",
                "html_url": "https://github.com/Ja-Tar",
                "followers_url": "https://api.github.com/users/Ja-Tar/followers",
                "following_url": "https://api.github.com/users/Ja-Tar/following{/other_user}",
                "gists_url": "https://api.github.com/users/Ja-Tar/gists{/gist_id}",
                "starred_url": "https://api.github.com/users/Ja-Tar/starred{/owner}{/repo}",
                "subscriptions_url": "https://api.github.com/users/Ja-Tar/subscriptions",
                "organizations_url": "https://api.github.com/users/Ja-Tar/orgs",
                "repos_url": "https://api.github.com/users/Ja-Tar/repos",
                "events_url": "https://api.github.com/users/Ja-Tar/events{/privacy}",
                "received_events_url": "https://api.github.com/users/Ja-Tar/received_events",
                "type": "User",
                "user_view_type": "public",
                "site_admin": False,
            },
            "node_id": "RE_kwDOPBJdK84PIrVm",
            "tag_name": "0.2.1",
            "target_commitish": "main",
            "name": "0.2.0: Settings update (now with magic theme)",
            "draft": False,
            "immutable": False,
            "prerelease": False,
            "created_at": "2025-10-12T21:21:36Z",
            "updated_at": "2025-10-15T05:41:41Z",
            "published_at": "2025-10-12T21:28:11Z",
            "assets": [
                {
                    "url": "https://api.github.com/repos/Ja-Tar/Launkey/releases/assets/303480284",
                    "id": 303480284,
                    "node_id": "RA_kwDOPBJdK84SFr3c",
                    "name": "launkey-0.2.0-1.fc40.x86_64.rpm",
                    "label": "",
                    "uploader": {
                        "login": "github-actions[bot]",
                        "id": 41898282,
                        "node_id": "MDM6Qm90NDE4OTgyODI=",
                        "avatar_url": "https://avatars.githubusercontent.com/in/15368?v=4",
                        "gravatar_id": "",
                        "url": "https://api.github.com/users/github-actions%5Bbot%5D",
                        "html_url": "https://github.com/apps/github-actions",
                        "followers_url": "https://api.github.com/users/github-actions%5Bbot%5D/followers",
                        "following_url": "https://api.github.com/users/github-actions%5Bbot%5D/following{/other_user}",
                        "gists_url": "https://api.github.com/users/github-actions%5Bbot%5D/gists{/gist_id}",
                        "starred_url": "https://api.github.com/users/github-actions%5Bbot%5D/starred{/owner}{/repo}",
                        "subscriptions_url": "https://api.github.com/users/github-actions%5Bbot%5D/subscriptions",
                        "organizations_url": "https://api.github.com/users/github-actions%5Bbot%5D/orgs",
                        "repos_url": "https://api.github.com/users/github-actions%5Bbot%5D/repos",
                        "events_url": "https://api.github.com/users/github-actions%5Bbot%5D/events{/privacy}",
                        "received_events_url": "https://api.github.com/users/github-actions%5Bbot%5D/received_events",
                        "type": "Bot",
                        "user_view_type": "public",
                        "site_admin": False,
                    },
                    "content_type": "binary/octet-stream",
                    "state": "uploaded",
                    "size": 195054843,
                    "digest": "sha256:c487e7a1cd6b5dd7acdc558c3f491eb4b61822ac80cfda06894ff01baf5c79a7",
                    "download_count": 0,
                    "created_at": "2025-10-12T21:36:39Z",
                    "updated_at": "2025-10-12T21:36:46Z",
                    "browser_download_url": "https://github.com/Ja-Tar/Launkey/releases/download/0.2.0/launkey-0.2.0-1.fc40.x86_64.rpm",
                },
                {
                    "url": "https://api.github.com/repos/Ja-Tar/Launkey/releases/assets/303479811",
                    "id": 303479811,
                    "node_id": "RA_kwDOPBJdK84SFrwD",
                    "name": "Launkey-0.2.0.msi",
                    "label": "",
                    "uploader": {
                        "login": "github-actions[bot]",
                        "id": 41898282,
                        "node_id": "MDM6Qm90NDE4OTgyODI=",
                        "avatar_url": "https://avatars.githubusercontent.com/in/15368?v=4",
                        "gravatar_id": "",
                        "url": "https://api.github.com/users/github-actions%5Bbot%5D",
                        "html_url": "https://github.com/apps/github-actions",
                        "followers_url": "https://api.github.com/users/github-actions%5Bbot%5D/followers",
                        "following_url": "https://api.github.com/users/github-actions%5Bbot%5D/following{/other_user}",
                        "gists_url": "https://api.github.com/users/github-actions%5Bbot%5D/gists{/gist_id}",
                        "starred_url": "https://api.github.com/users/github-actions%5Bbot%5D/starred{/owner}{/repo}",
                        "subscriptions_url": "https://api.github.com/users/github-actions%5Bbot%5D/subscriptions",
                        "organizations_url": "https://api.github.com/users/github-actions%5Bbot%5D/orgs",
                        "repos_url": "https://api.github.com/users/github-actions%5Bbot%5D/repos",
                        "events_url": "https://api.github.com/users/github-actions%5Bbot%5D/events{/privacy}",
                        "received_events_url": "https://api.github.com/users/github-actions%5Bbot%5D/received_events",
                        "type": "Bot",
                        "user_view_type": "public",
                        "site_admin": False,
                    },
                    "content_type": "binary/octet-stream",
                    "state": "uploaded",
                    "size": 217735328,
                    "digest": "sha256:dc351299fe79c2a3363e1a47f633934d3984a0cd76f0e05e1c4702a8b36962d7",
                    "download_count": 1,
                    "created_at": "2025-10-12T21:33:10Z",
                    "updated_at": "2025-10-12T21:33:16Z",
                    "browser_download_url": "https://github.com/Ja-Tar/Launkey/releases/download/0.2.0/Launkey-0.2.0.msi",
                },
                {
                    "url": "https://api.github.com/repos/Ja-Tar/Launkey/releases/assets/303479809",
                    "id": 303479809,
                    "node_id": "RA_kwDOPBJdK84SFrwB",
                    "name": "Launkey-0.2.0.wixpdb",
                    "label": "",
                    "uploader": {
                        "login": "github-actions[bot]",
                        "id": 41898282,
                        "node_id": "MDM6Qm90NDE4OTgyODI=",
                        "avatar_url": "https://avatars.githubusercontent.com/in/15368?v=4",
                        "gravatar_id": "",
                        "url": "https://api.github.com/users/github-actions%5Bbot%5D",
                        "html_url": "https://github.com/apps/github-actions",
                        "followers_url": "https://api.github.com/users/github-actions%5Bbot%5D/followers",
                        "following_url": "https://api.github.com/users/github-actions%5Bbot%5D/following{/other_user}",
                        "gists_url": "https://api.github.com/users/github-actions%5Bbot%5D/gists{/gist_id}",
                        "starred_url": "https://api.github.com/users/github-actions%5Bbot%5D/starred{/owner}{/repo}",
                        "subscriptions_url": "https://api.github.com/users/github-actions%5Bbot%5D/subscriptions",
                        "organizations_url": "https://api.github.com/users/github-actions%5Bbot%5D/orgs",
                        "repos_url": "https://api.github.com/users/github-actions%5Bbot%5D/repos",
                        "events_url": "https://api.github.com/users/github-actions%5Bbot%5D/events{/privacy}",
                        "received_events_url": "https://api.github.com/users/github-actions%5Bbot%5D/received_events",
                        "type": "Bot",
                        "user_view_type": "public",
                        "site_admin": False,
                    },
                    "content_type": "binary/octet-stream",
                    "state": "uploaded",
                    "size": 2044514,
                    "digest": "sha256:609ea892a3f18611b1a88a30eeb6b2244c1066f0323198653d7dace5d554287c",
                    "download_count": 0,
                    "created_at": "2025-10-12T21:33:09Z",
                    "updated_at": "2025-10-12T21:33:09Z",
                    "browser_download_url": "https://github.com/Ja-Tar/Launkey/releases/download/0.2.0/Launkey-0.2.0.wixpdb",
                },
                {
                    "url": "https://api.github.com/repos/Ja-Tar/Launkey/releases/assets/303479793",
                    "id": 303479793,
                    "node_id": "RA_kwDOPBJdK84SFrvx",
                    "name": "launkey_0.2.0-1.ubuntu-noble_amd64.deb",
                    "label": "",
                    "uploader": {
                        "login": "github-actions[bot]",
                        "id": 41898282,
                        "node_id": "MDM6Qm90NDE4OTgyODI=",
                        "avatar_url": "https://avatars.githubusercontent.com/in/15368?v=4",
                        "gravatar_id": "",
                        "url": "https://api.github.com/users/github-actions%5Bbot%5D",
                        "html_url": "https://github.com/apps/github-actions",
                        "followers_url": "https://api.github.com/users/github-actions%5Bbot%5D/followers",
                        "following_url": "https://api.github.com/users/github-actions%5Bbot%5D/following{/other_user}",
                        "gists_url": "https://api.github.com/users/github-actions%5Bbot%5D/gists{/gist_id}",
                        "starred_url": "https://api.github.com/users/github-actions%5Bbot%5D/starred{/owner}{/repo}",
                        "subscriptions_url": "https://api.github.com/users/github-actions%5Bbot%5D/subscriptions",
                        "organizations_url": "https://api.github.com/users/github-actions%5Bbot%5D/orgs",
                        "repos_url": "https://api.github.com/users/github-actions%5Bbot%5D/repos",
                        "events_url": "https://api.github.com/users/github-actions%5Bbot%5D/events{/privacy}",
                        "received_events_url": "https://api.github.com/users/github-actions%5Bbot%5D/received_events",
                        "type": "Bot",
                        "user_view_type": "public",
                        "site_admin": False,
                    },
                    "content_type": "binary/octet-stream",
                    "state": "uploaded",
                    "size": 194533786,
                    "digest": "sha256:ed24ba90b9873868b9f1056b002a6d6c1d558bd5d0ebd0a9b1ac3772a3349b5d",
                    "download_count": 0,
                    "created_at": "2025-10-12T21:32:56Z",
                    "updated_at": "2025-10-12T21:33:00Z",
                    "browser_download_url": "https://github.com/Ja-Tar/Launkey/releases/download/0.2.0/launkey_0.2.0-1.ubuntu-noble_amd64.deb",
                },
            ],
            "tarball_url": "https://api.github.com/repos/Ja-Tar/Launkey/tarball/0.2.0",
            "zipball_url": "https://api.github.com/repos/Ja-Tar/Launkey/zipball/0.2.0",
            "body": '# HOW TO TEST (IMPORTANT)\r\n\r\n> [!NOTE]\r\n> Linux version is working now, but see #32 or [WIKI](https://github.com/Ja-Tar/Launkey/wiki/Troubleshooting#launchpad-connection-issues-launchpad-not-found-error-1)\r\n\r\nIf you don\'t have a launchpad you can use [Test mode](https://github.com/Ja-Tar/Launkey/wiki/User-Interface#test-mode)\r\n\r\n## What\'s Changed\r\n- Settings window added\r\n- Theme options added (**for now only magic one is working**)\r\n- Fixes\r\n\r\n### Dependencies \r\n* Bump briefcase from 0.3.24 to 0.3.25 by @dependabot[bot] in https://github.com/Ja-Tar/Launkey/pull/41\r\n* Bump pyside6 from 6.9.2 to 6.9.3 by @dependabot[bot] in https://github.com/Ja-Tar/Launkey/pull/42\r\n* Bump pyside6-essentials from 6.9.2 to 6.9.3 by @dependabot[bot] in https://github.com/Ja-Tar/Launkey/pull/40\r\n\r\n# Screenshot\r\n\r\n<img width="802" height="632" alt="obraz" src="https://github.com/user-attachments/assets/3c3610ea-9941-483d-9d72-ddeb6beb4bfe" />\r\n\r\n**Full Changelog**: https://github.com/Ja-Tar/Launkey/compare/0.1.3...0.2.0',
            "mentions_count": 1,
        } # REMOVE

        self.newestVersion = json.get("tag_name", "")
        self.assets = json.get("assets", [])

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
            # QDesktopServices.openUrl()
            pass
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
    um.saveData()
