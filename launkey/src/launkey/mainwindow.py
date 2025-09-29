import asyncio
import keyboard
import json
from pathlib import Path

from typing import TYPE_CHECKING, Any, List

#from PySide6 import QtAsyncio
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QInputDialog, QMessageBox, QErrorMessage
#import launchpad_py as launchpad

from .ui_dialogtemplates import Ui_Dialog
from .custom_widgets import QDialogNoDefault, TemplateDisplay
from .templates import Template, TemplateItem, getTemplateFolderPath, objectFromJson, checkTemplate, sterilizeTemplateName, loadedTemplates
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
    loadedDisplaysName: List[str] = []
    for item in layoutItems:
        item = item[0]
        if isinstance(item, TemplateDisplay):
            loadedDisplaysName.append(item.text)
    return any(name == templateName for name in loadedDisplaysName)

async def buttonRun(main_window: "Launkey", lpWrapper: LaunchpadWrapper):
    main_window.set_close(lpWrapper.lp)
    return
    if main_window.ui.buttonRun.text() == "Run":
        main_window.ui.buttonRun.setText("Stop")
        main_window.ui.statusbar.showMessage("Running...")
        lpWrapper.start_sync()
        asyncio.create_task(async_test(lpWrapper), name="async_test_loop") # REMOVE
        print("Started Launkey controller")
        return
    main_window.ui.buttonRun.setText("Run")
    main_window.ui.statusbar.showMessage("Stopped")
    # Stop the async loop and reset the launchpad
    for task in asyncio.all_tasks():
        if task.get_name() in ["async_test_loop", "sync_table_loop"]:
            task.cancel()
    lpWrapper.stop()

async def async_test(lpWrapper: LaunchpadWrapper, anim_time: float = 0.1): # REMOVE
    arrow_up_red = [
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 1, 1, 0, 0, 0,
        0, 0, 1, 3, 3, 1, 0, 0,
        0, 1, 3, 3, 3, 3, 1, 0,
        0, 0, 0, 3, 3, 0, 0, 0,
        0, 0, 0, 3, 3, 0, 0, 0,
        0, 0, 0, 3, 3, 0, 0, 0
    ]

    # autoMap animation: przesuwający się pasek
    autoMap_length = 16
    autoMap_color = (0, 3)  # Zielony pasek
    autoMap_off = (0, 0)
    autoMap_pos = 0

    while True:
        # Animate arrow moving up from bottom to top
        for row in range(6, -1, -1):
            frame = [(0, 0)] * 64
            # Copy the arrow shape into the current row
            for i in range(8):
                if row + i < 7:
                    for j in range(8):
                        dx = (row + i) * 8 + j
                        arrow_idx = i * 8 + j
                        if arrow_up_red[arrow_idx]:
                            frame[dx] = (arrow_up_red[arrow_idx], 0)
            # Animacja autoMap: przesuwający się pojedynczy "piksel"
            autoMap = [(0, 0)] * autoMap_length
            # Ustaw pasek na odpowiedniej pozycji
            autoMap = [autoMap_color if i == autoMap_pos else autoMap_off for i in range(autoMap_length)]
            lpWrapper.changeLedsRapid(frame, autoMap) # type: ignore
            await asyncio.sleep(anim_time)
            autoMap_pos = (autoMap_pos + 1) % autoMap_length
        await asyncio.sleep(0.5)
        lpWrapper.reset()

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