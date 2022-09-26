import os
import dearpygui.dearpygui as dpg
from data import ModFile
from data.Settings import settings
from gui import ImageCache
from gui.components import ComponentBase
from gui.Fonts import get_big_font


class ModItem(ComponentBase):
    """mod 列表中展示的 mod 项目, 包含图标, 信息, 操作按钮
    """

    def __init__(self, mod: ModFile):
        super().__init__()
        self.main_button_ui: int | str = 0
        self.minor_button_ui: int | str = 0
        self.title_ui: int | str = -1
        self.info_ui: int | str = -1
        self.desc_ui: int | str = -1
        self.mod = mod
        self.height: int = settings.get_size(180)
        self.table: int | str = -1

    def setup(self):
        with dpg.child_window(border=False, height=self.height,
                              indent=1, user_data=self) as self.ui:  # type: ignore
            with dpg.group(horizontal=True):
                self.__setup_icon()
                self.__setup_info()
                self.__setup_buttons()

    def __setup_icon(self):
        with dpg.child_window(height=self.height, width=self.height, border=False):
            if self.mod.get_icon():
                img = ImageCache.get(self.mod, self.height)
                with dpg.drawlist(width=self.height, height=self.height):
                    dpg.draw_image(img, (0, 0), (self.height, self.height))
            else:
                dpg.add_child_window(
                    border=False, width=self.height, height=self.height)

    def __setup_info(self):
        with dpg.child_window(height=self.height, width=-220, border=False, no_scrollbar=True):
            self.title_ui = dpg.add_text()
            dpg.bind_item_font(self.title_ui, get_big_font())
            dpg.add_spacer()
            self.info_ui = dpg.add_text()
            self.desc_ui = dpg.add_text()
            self.reshow_info()

    def __setup_buttons(self):
        with dpg.child_window(height=self.height, width=-10, border=False) as buttons:
            top = int(self.height * 0.3)
            m = self.height - top * 2
            dpg.add_child_window(border=False, height=top)
            with dpg.group(horizontal=True):
                self.main_button_ui = dpg.add_button(
                    label='安装', width=-40, height=int(m),
                    user_data=self)
                # ▼▽
                self.minor_button_ui = dpg.add_button(
                    label="▽", width=-1, height=int(m),
                    user_data=self)
                dpg.bind_item_theme(self.minor_button_ui, 'button_zero')
            dpg.bind_item_theme(buttons, 'zero')  # type: ignore

    def reshow_info(self):
        """刷新控件上显示的mod名字, 文件名, 描述信息
        """
        dpg.set_value(self.title_ui, '|'.join(self.mod.get_names()))

        infos = []
        des = ''
        for info in self.mod.mod_info:
            infos.append(
                f"API:{info.loader}   VER:{info.version}   MC:{info.mc_version}")
            if len(info.description) > len(des):
                des = info.description

        dpg.set_value(self.info_ui,
                      "\n".join(infos) + '\n' + f"来自文件：{os.path.basename(self.mod.full_file_path)}")
        dpg.set_value(self.desc_ui,
                      des.replace('\n', '\t'))
