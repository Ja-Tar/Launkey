import asyncio
import keyboard
import json
from pathlib import Path

from typing import TYPE_CHECKING

#from PySide6 import QtAsyncio
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QInputDialog, QMessageBox, QErrorMessage
#import launchpad_py as launchpad

from .ui_dialogtemplates import Ui_Dialog
from .custom_widgets import QDialogNoDefault, TemplateDisplay
from .templates import Template, TemplateItem, Button, getTemplateFolderPath, objectFromJson, checkTemplate, sterilizeTemplateName, loadedTemplates
from .launchpad_control import LaunchpadWrapper

if TYPE_CHECKING:
    from .app import Launkey

def mainWindowScript(main_window: "Launkey"):
    main_window.ui.buttonAddTemplate.clicked.connect(lambda: newTemplatePopup(main_window))
    importTemplates(main_window)
    lpWrapper = LaunchpadWrapper(main_window.ui.tableLaunchpad)
    if lpWrapper.connect():
        main_window.ui.statusbar.showMessage("Launchpad connected")
        main_window.lpclose = lpWrapper.lp
    else:
        main_window.ui.statusbar.showMessage("Launchpad not found")
        QMessageBox.warning(
            main_window,
            "Launchpad Error",
            "Launchpad not found. Please connect your Launchpad and try again.",
            QMessageBox.StandardButton.Ok
        )
        return
    main_window.ui.buttonRun.clicked.connect(lambda: asyncio.ensure_future(buttonRun(main_window, lpWrapper)))
    main_window.ui.buttonRun.setEnabled(True)

def importTemplates(main_window: "Launkey", currentTemplateDisplayName: str | None = None):
    if currentTemplateDisplayName:
        removeTemplateForRefresh(main_window, currentTemplateDisplayName)

    template_files = getTemplateFileList()
    for template_file in template_files:
        try:
            template_path = getTemplateFolderPath() / template_file
            templateData = parseTemplateFile(main_window, template_path)
            if not templateData:
                continue

            addTemplateToLayout(main_window, templateData, template_file)
        except Exception as e:
            message = f"Error loading template from {template_file}: {e}"
            messagebox = QMessageBox(QMessageBox.Icon.Critical, "Template Load Error", message, parent=main_window)
            messagebox.exec()

def removeTemplateForRefresh(main_window, currentTemplateDisplayName):
    for i in reversed(range(main_window.ui.gridLayoutTemplates.count())):
        item = main_window.ui.gridLayoutTemplates.itemAt(i)
        if item is None:
            continue
        widget = item.widget()
        if isinstance(widget, TemplateDisplay) and widget.text == currentTemplateDisplayName:
            main_window.ui.gridLayoutTemplates.removeWidget(widget)
            widget.deleteLater()
            if currentTemplateDisplayName in loadedTemplates:
                del loadedTemplates[currentTemplateDisplayName]
            break

def parseTemplateFile(main_window: "Launkey", filePath: Path) -> list[Template | TemplateItem]:
        errorMessageTitle = "Load Template Error"

        templateJsonData: list[dict[str, object]] = []
        templateData: list[Template | TemplateItem] = []
        try:
            with open(filePath, "r") as f:
                templateJsonData: list[dict[str, object]] = json.load(f)
        except Exception as e:
            QMessageBox.warning(main_window, errorMessageTitle, f"Failed to load template file: {e}")
            return []
        for obj in templateJsonData:
            try:
                template = objectFromJson(obj)
            except ValueError as e:
                QMessageBox.warning(main_window, errorMessageTitle, f"Error parsing template data: {e}")
                continue
            if template:
                templateData.append(template)
        
        if not checkTemplate(templateData):
            QMessageBox.warning(main_window, errorMessageTitle, "Template file is invalid or contains no Template object.")
            return []
    
        return templateData

def addTemplateToLayout(main_window: "Launkey", templateData: list[Template | TemplateItem], templateFileName: str):
    templateDisplay = TemplateDisplay(main_window, templateData, main_window)
    if not checkForDuplicates(main_window, templateDisplay.text):
        main_window.ui.gridLayoutTemplates.addWidget(templateDisplay)
        loadedTemplates[templateFileName] = templateData

def getTemplateFileList() -> list[str]:
    folderPath = getTemplateFolderPath()
    return [f.name for f in folderPath.iterdir() if f.is_file() and f.suffix == ".json"]

def checkForDuplicates(main_window: "Launkey", templateName: str) -> bool:
    layoutItems = main_window.ui.gridLayoutTemplates.items
    loadedDisplaysName: list[str] = []
    for item in layoutItems:
        item = item[0]
        if isinstance(item, TemplateDisplay):
            loadedDisplaysName.append(item.text)
    return any(name == templateName for name in loadedDisplaysName)

async def buttonRun(main_window: "Launkey", lpWrapper: LaunchpadWrapper):
    if main_window.ui.buttonRun.text() == "Run":
        main_window.ui.buttonRun.setText("Stop")
        main_window.ui.statusbar.showMessage("Running...")
        lpWrapper.start()
        asyncio.create_task(listenForButtonPress(lpWrapper), name="listenForButtonPress")
        print("Started Launkey controller")
        return
    main_window.ui.buttonRun.setText("Run")
    main_window.ui.statusbar.showMessage("Stopped")
    # Stop the async loop and reset the launchpad
    for task in asyncio.all_tasks():
        if task.get_name() in ["listenForButtonPress"]:
            task.cancel()
    lpWrapper.reset()

async def listenForButtonPress(lpWrapper: LaunchpadWrapper) -> str:
    print("Waiting for button press...")
    while True:
        event = lpWrapper.lp.ButtonStateXY()  # type: ignore
        if event:
            if event[2] == 1:  # Button pressed
                asyncio.create_task(buttonClicked(lpWrapper, (event[0], event[1]), lpWrapper.table.getTemplateItemAtButton((event[0], event[1]))), name="buttonClicked")
            if event[2] == 0:  # Button released
                lpWrapper.buttonUnpressed((event[0], event[1]))
        await asyncio.sleep(0.01)

async def buttonClicked(lpWrapper: LaunchpadWrapper, buttonPos: tuple[int, int], templateItem: TemplateItem | None):
    if isinstance(templateItem, Button):
        lpWrapper.buttonPressed(buttonPos, templateItem)

def selectTemplateTypePopup(main_window: "Launkey"):
    popup = QInputDialog(main_window)
    template_type, ok = popup.getItem(
        main_window,
        "Select Template Type",
        "Select the type of template you want to create:",
        template_types := [t.name for t in Template.Type],
        current=0,
        editable=False,
        flags=Qt.WindowType.WindowStaysOnTopHint
    )

    if not ok:
        return None
    return Template.Type[template_type]

def newTemplatePopup(main_window: "Launkey"):
    template_type = selectTemplateTypePopup(main_window)
    if template_type is None:
        return

    dialog = QDialogNoDefault(main_window)
    ui = Ui_Dialog()
    ui.setupUi(dialog, template_type)
    dialog.setWindowTitle("New Template")
    dialog.show()

    if dialog.exec() == QDialogNoDefault.DialogCode.Accepted:
        importTemplates(main_window)
        print("Refreshed templates")

def editTemplatePopup(main_window: "Launkey", templateDisplayName: str):
    # TODO load template data into the dialog, with the ability to edit and save changes
    templateFileName = sterilizeTemplateName(templateDisplayName) + ".json"
    if templateFileName not in loadedTemplates:
        error_dialog = QErrorMessage(main_window)
        error_dialog.showMessage(f"Template '{templateFileName}' not found.")
        return
    
    dialog = QDialogNoDefault(main_window)
    ui = Ui_Dialog()
    ui.loadTemplate(dialog, loadedTemplates[templateFileName])
    dialog.setWindowTitle("Edit Template")
    dialog.show()

    if dialog.exec() == QDialogNoDefault.DialogCode.Accepted:
        importTemplates(main_window, templateDisplayName)
        print("Refreshed templates")