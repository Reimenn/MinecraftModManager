import dearpygui.dearpygui as dpg

from gui.Components.ModList import ModList
from gui.Pages import PageBase
from gui.Components.ModItem import ModItem
from data import Mod
from data import ModManager


class LocalPage(PageBase):
    get: 'LocalPage'

    def __init__(self):
        super().__init__()
        self.ml: ModList = None  # type: ignore
        self.loading: bool = False
        LocalPage.get = self
        with dpg.theme() as self.menu_theme:
            with dpg.theme_component():
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 0)

    def build_page(self):
        def on_create_mod_item(item: ModItem):
            dpg.set_item_callback(item.main_button_ui,
                                  callback=self.on_mod_main_button_click)
            dpg.set_item_callback(item.minor_button_ui,
                                  callback=self.on_mod_minor_button_click)

        self.ml = ModList(reload_callback=self.reload_mods,
                          on_create_mod_item=on_create_mod_item)
        self.ml.setup()

    def show(self):
        super().show()
        if not ModManager.get().local_mods:
            self.reload_mods()
        if not self.ml.mod_items:
            self.reshow_mods()

    def hide(self):
        super().hide()
        self.ml.clear()

    def set_loading(self, loading: bool):
        self.loading = loading
        self.ml.set_loading(loading)

    def reload_mods(self):
        if self.loading:
            return
        self.ml.clear()
        self.set_loading(True)
        import gc
        gc.collect()
        ModManager.get().reload_local_mods(
            on_load_one=self.ml.add,
            on_load_over=self.on_load_over
        )

    def reshow_mods(self):
        for mod in ModManager.get().local_mods:
            self.ml.add(mod)

    def on_load_over(self, mods: list[Mod]):
        self.set_loading(False)

    def on_mod_main_button_click(self, item: int | str, value, data: ModItem):
        from gui.MainWindow import MainWindow
        MainWindow.get.install_mod_menu.show(data.mod)
 
    def on_mod_minor_button_click(self, item: int | str, value, data: ModItem):
        from gui.MainWindow import MainWindow

        def _del_mod(mod: Mod):
            ModManager.get().local_mods.remove(mod)
            LocalPage.get.ml.remove(mod)
            mod.delete_file()

        MainWindow.get.mod_menu.show(data.mod, on_delete_mod=_del_mod)
