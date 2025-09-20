import asyncio
import keyboard
import json

from typing import TYPE_CHECKING, Any, List

#from PySide6 import QtAsyncio
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QInputDialog, QMessageBox, QFrame
#import launchpad_py as launchpad

from .ui_dialogtemplates import Ui_Dialog
from .custom_widgets import QDialogNoDefault, TemplateDisplay
from .templates import Template, getTemplateFolderPath, objectFromJson, TemplateItem
from .launchpad_control import LaunchpadWrapper

if TYPE_CHECKING:
    from .app import Launkey

def mainWindowScript(main_window: "Launkey"):
    main_window.ui.buttonAddTemplate.clicked.connect(lambda: newTemplatePopup(main_window))
    loadTemplates(main_window)

    lpWrapper = LaunchpadWrapper(main_window)
    if lpWrapper.connect():
        main_window.ui.statusbar.showMessage("Launchpad connected")
        main_window.lpclose = lpWrapper.lp
    else:
        main_window.ui.statusbar.showMessage("Launchpad not found")
        QMessageBox.critical(
            main_window,
            "Launchpad Error",
            "Launchpad not found. Please close the app to connect to the Launchpad."
        )
        return
    main_window.ui.buttonRun.clicked.connect(lambda: asyncio.ensure_future(buttonRun(main_window, lpWrapper)))
    main_window.ui.buttonRun.setEnabled(True)

def loadTemplates(main_window: "Launkey"):
    template_files = getTemplateFileList()
    for template_file in template_files:
        try:
            with open(getTemplateFolderPath() / template_file, "r") as f:
                templateJsonData: list[dict[str, Any]] = json.load(f)
            templateData: list[Template | TemplateItem] = []
            for obj in templateJsonData:
                template = objectFromJson(obj)
                if template:
                    templateData.append(template)
            templateDisplay = TemplateDisplay(templateData, main_window)
            if not checkForDuplicates(main_window, templateDisplay.text):
                main_window.ui.gridLayoutTemplates.addWidget(templateDisplay)
        except Exception as e:
            message = f"Error loading template from {template_file}: {e}"
            messagebox = QMessageBox(QMessageBox.Icon.Critical, "Template Load Error", message, parent=main_window)
            messagebox.exec()

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
        loadTemplates(main_window)
        print("Refreshed templates")

def editTemplatePopup(main_window: "Launkey"):
    # TODO load template data into the dialog, with the ability to edit and save changes
    #dialog = QDialogNoDefault(main_window)
    #ui = Ui_Dialog()
    #ui.setupUi(dialog) # FIX
    #dialog.setWindowTitle("Edit Template")
    #dialog.show()
    pass