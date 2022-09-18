from gui.pages import PageBase
import dearpygui.dearpygui as dpg

class DownloadPage(PageBase):
    def __init__(self):
        super().__init__()

    def build_page(self):
        with dpg.tab_bar():
            with dpg.tab(label="MC MOD 百科"):
                def _test():
                    pass
                dpg.add_button(label="测试", callback=_test)
            with dpg.tab(label="CuroseForge"):
                pass
            with dpg.tab(label="ModRihon"):
                pass
