from logging.config import valid_ident

import dearpygui.dearpygui as dpg
from data.Settings import settings
from gui.pages import PageBase


class SettingsPage(PageBase):
    def __init__(self):
        super().__init__()

    def build_page(self):
        with dpg.table(header_row=False):
            dpg.add_table_column(init_width_or_weight=2)
            dpg.add_table_column(init_width_or_weight=6)
            dpg.add_table_column(init_width_or_weight=2)
            with dpg.table_row():
                with dpg.table_cell():
                    pass
                with dpg.table_cell():
                    self._build_settings()
                with dpg.table_cell():
                    pass

    def _build_settings(self):
        def change_global_size(item, value, data):
            settings.global_size = value
            settings.save()
            dpg.set_global_font_scale(value)

        dpg.add_slider_float(label="界面缩放", callback=change_global_size,
                             default_value=settings.global_size,
                             max_value=2, min_value=0.5, format='%.1f')

        def change_game_dir(item, value, data):
            settings.game_version_dir = value
            settings.save()

        with dpg.group(horizontal=True):
            dpg.add_input_text(callback=change_game_dir,
                               default_value=settings.game_version_dir)
            dpg.add_button(label=' ... ', small=True)
            tip = dpg.add_text(default_value="游戏目录")
        with dpg.tooltip(tip):
            dpg.add_text('存放游戏版本的目录，\n应该设置为 .minecraft 目录下面的 versions 文件夹。')

        def change_local_dir(item, value, data):
            settings.local_mods_dir = value
            settings.save()

        with dpg.group(horizontal=True):
            dpg.add_input_text(callback=change_local_dir,
                               default_value=settings.local_mods_dir)
            dpg.add_button(label=' ... ', small=True)
            tip = dpg.add_text('MOD仓库目录')
        with dpg.tooltip(tip):
            dpg.add_text(
                '存放 mod 的目录，\n下载的 mod 文件会存放到这里，\n也可以把已有的 mod 放到这个目录里进行管理。')

        def test():
            with dpg.menu() as menu:
                dpg.add_menu_item(label='111')
                dpg.add_menu_item(label='111')
                dpg.add_menu_item(label='111')
