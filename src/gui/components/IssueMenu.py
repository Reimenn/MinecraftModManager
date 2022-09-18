import dearpygui.dearpygui as dpg
from data.GameModsCheck import ModCheckResult
from data.ModInfo import Mod
from gui.components import ComponentBase


class IssueMenu(ComponentBase):
    def __init__(self):
        super().__init__()
        self.width = 400
        self.issues: dict[Mod, list[ModCheckResult]] = {}

    def setup(self):
        temp = dpg.add_text()

        with dpg.popup(temp) as self.ui:  # type: ignore
            dpg.add_text(default_value="问题如下：")

        dpg.delete_item(temp)
        return super().setup()

    def show(self, issues: dict[Mod, list[ModCheckResult]]):
        self.issues = issues
        return super().show()
