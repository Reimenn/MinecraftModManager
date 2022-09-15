from typing import Callable

import dearpygui.dearpygui as dpg
from data import Mod
from data.Settings import settings
from gui.components import ComponentBase
from gui.components.ListView import ListView
from gui.components.ModItem import ModItem


class ModList(ComponentBase):
    """mod 列表组件, 包含加载器筛选器, 版本筛选器, 名称筛选器, 刷新按钮
    """

    def __init__(self,
                 show_reload_button: bool = True,
                 show_loader_filter: bool = True,
                 show_version_filter: bool = True,
                 show_name_filter: bool = True,
                 show_tools: bool = True,
                 reload_callback: Callable[[], None] | None = None,
                 on_create_mod_item: Callable[[ModItem], None] | None = None
                 ):
        """
        Args:
            show_reload_button: 是否显示刷新按钮. Defaults to True.
            show_loader_filter: 是否显示加载器筛选. Defaults to True.
            show_version_filter: 是否显示版本筛选. Defaults to True.
            show_name_filter: 是否显示名称筛选. Defaults to True.
            show_tools: 是否显示工具栏(各种筛选和刷新按钮的部分). Defaults to True.
            reload_callback: 点击刷新按钮的回调. Defaults to None.
            on_create_mod_item: 创建新的ModItem的回调,可以在这个回调里面对ModItem做些设定. Defaults to None.
        """
        self.reload_callback = reload_callback
        self.show_reload_button = show_reload_button
        self.show_loader_filter: bool = show_loader_filter
        self.show_version_filter: bool = show_version_filter
        self.show_name_filter: bool = show_name_filter
        self.show_tools: bool = show_tools
        self.lv: ListView = None  # type: ignore
        self.loading = False
        self.search_input_ui: int = 0
        self.reload_button: int = 0
        self.loading_indicator: int = 0
        self.mod_items: list[ModItem] = []
        self.on_create_mod_item = on_create_mod_item
        self.filter: dict[str, str | bool] = {
            'forge': True,
            'fabric': True,
            'quilt': True,
            'other': True,
            'version': '',
            'keyword': ''
        }
        self.ui: int = 0

    def setup(self):
        with dpg.child_window(border=False, no_scrollbar=True) as self.ui:  # type: ignore
            if self.show_tools:
                with dpg.group(horizontal=True):
                    if self.show_loader_filter:
                        dpg.add_checkbox(label="Forge", default_value=True, user_data='filter_forge',
                                         callback=self.on_filter_change)
                        dpg.add_checkbox(label="Fabric", default_value=True, user_data='filter_fabric',
                                         callback=self.on_filter_change)
                        dpg.add_checkbox(label="Quilt", default_value=True, user_data='filter_quilt',
                                         callback=self.on_filter_change)
                        dpg.add_checkbox(label="Other", default_value=True, user_data='filter_other',
                                         callback=self.on_filter_change)
                        dpg.add_spacer()
                    if self.show_version_filter:
                        dpg.add_input_text(
                            hint="版本搜索", width=150,
                            user_data='filter_version', callback=self.on_filter_change)
                    if self.show_name_filter:
                        width = -1
                        if self.show_reload_button:
                            width = -settings.get_size(150)
                        self.search_input_ui = dpg.add_input_text(
                            hint='关键字搜索', width=width, user_data='filter_keyword',
                            callback=self.on_filter_change)  # type: ignore
                    if self.show_reload_button:
                        self.reload_button = dpg.add_button(  # type: ignore
                            label="刷新", width=-1, callback=self.reload_callback)  # type: ignore
                        self.loading_indicator = dpg.add_loading_indicator(  # type: ignore
                            radius=1, show=False)
            self.lv = ListView()
            self.lv.setup()

    def set_loading(self, loading: bool):
        """设定loading状态, 这会改变刷新按钮
        """
        if not self.show_reload_button:
            return
        if loading:
            dpg.disable_item(self.reload_button)
            dpg.show_item(self.loading_indicator)
            dpg.hide_item(self.reload_button)
        else:
            dpg.enable_item(self.reload_button)
            dpg.hide_item(self.loading_indicator)
            dpg.show_item(self.reload_button)
        self.loading = loading

    def clear(self):
        """清空 mod 列表
        """
        self.lv.clear()
        self.mod_items.clear()
        self.set_loading(False)

    def add(self, mod: Mod):
        """添加一个新mod

        Args:
            mod (ModInfo): 新mod
        """
        mi = ModItem(mod)
        dpg.push_container_stack(self.lv.ui)
        mi.setup()
        if self.on_create_mod_item:
            self.on_create_mod_item(mi)

        dpg.pop_container_stack()
        dpg.set_item_user_data(mi.ui, mi.mod)
        self.mod_items.append(mi)
        self.lv.add(mi.ui)

    def remove(self, mod: Mod):
        """删除一个mod
        """
        remove_target = None
        for mod_item in self.mod_items:
            if mod_item.mod == mod:
                remove_target = mod_item
        if remove_target is None:
            return
        self.mod_items.remove(remove_target)
        self.lv.remove(remove_target.ui)

    def on_filter_change(self, item, value, data: str):
        """内部回调, 当各种筛选器被修改时触发
        """
        self.filter[data.split('_')[1]] = value
        for i in self.lv.values:
            mod: Mod = dpg.get_item_user_data(i)  # type: ignore
            show = False

            if self.filter['forge'] and 'forge' in mod.loader:
                show = True
            elif self.filter['fabric'] and 'fabric' in mod.loader:
                show = True
            elif self.filter['quilt'] and 'quilt' in mod.loader:
                show = True
            elif self.filter['other'] and 'forge' not in mod.loader and \
                    'fabric' not in mod.loader and 'quilt' not in mod.loader:
                show = True
            if self.filter['keyword']:
                if self.filter['keyword'].lower() not in mod.get_search_text().lower():  # type: ignore
                    show = False
            if show:
                dpg.show_item(i)
            else:
                dpg.hide_item(i)
