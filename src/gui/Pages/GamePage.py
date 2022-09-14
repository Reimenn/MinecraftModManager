import dearpygui.dearpygui as dpg
from data.Settings import settings
from data import Game, ModManager
from data.ModInfo import Mod
from gui.Components.GameList import GameList
from gui.Components.ModItem import ModItem
from gui.Components.ModList import ModList
from gui.Fonts import Fonts
from gui.Pages import PageBase


class GamePage(PageBase):
    """游戏页面, 管理本地各个游戏下mod的页面
    """
    get: 'GamePage'

    def __init__(self):
        super().__init__()
        self.loading: bool = False
        self.game_list: GameList = GameList(
            on_selected_game=self.on_change_game,
            on_reloaded_game=self.on_reload_game)

        self.mod_list: ModList = ModList(reload_callback=self.reload_mods,
                                         show_loader_filter=False,
                                         show_version_filter=False,
                                         on_create_mod_item=self._on_create_mod_item)
        self.current_game: Game | None = None
        GamePage.get = self

    def build_page(self):
        dpg.configure_item(self.ui, no_scrollbar=True)
        with dpg.table(header_row=False):
            dpg.add_table_column(init_width_or_weight=10)
            dpg.add_table_column(init_width_or_weight=30)
            with dpg.table_row():
                with dpg.table_cell():
                    self.game_list.setup()
                with dpg.table_cell():
                    self.mod_list.setup()

    def _on_create_mod_item(self, item: ModItem):
        """对 mod 列表中的 ModItem 进行设置
        """
        dpg.set_item_callback(item.main_button_ui,
                              self.on_mod_main_button_click)
        if item.mod.is_enabled():
            dpg.set_item_label(item.main_button_ui, Fonts.is_enabled_text)
        else:
            dpg.set_item_label(item.main_button_ui, Fonts.is_disabled_text)

        dpg.set_item_callback(item.minor_button_ui,
                              self.on_mod_minor_button_click)

    def show(self):
        super().show()
        if not self.game_list.show_items:
            self.game_list.reload_games()
        if self.current_game and not self.mod_list.mod_items:
            self.try_show_mods()

    def hide(self):
        super().hide()
        self.mod_list.clear()

    def set_loading(self, loading: bool):
        self.loading = loading
        self.mod_list.set_loading(loading)
        if loading:
            dpg.disable_item(self.game_list.reload_button_ui)
            dpg.disable_item(self.game_list.game_list_ui)
        else:
            dpg.enable_item(self.game_list.reload_button_ui)
            dpg.enable_item(self.game_list.game_list_ui)

    def reload_mods(self):
        """重新加载当前选中游戏的 mod
        """
        if not self.current_game:
            return
        self.mod_list.clear()
        self.set_loading(True)
        self.current_game.reload_mods(
            self.mod_list.add, self.on_load_mod_over
        )

    def try_show_mods(self):
        """尝试显示mod, 若mod还未加载则加载mod
        """
        if not self.current_game:
            return
        if self.current_game.mod_list:
            self.mod_list.clear()
            for mod in self.current_game.mod_list:
                self.mod_list.add(mod)
        else:
            self.reload_mods()

    def on_change_game(self, game: Game):
        """改变选择的游戏时触发, 这会尝试刷新mod列表(调用 try_show_mods)
        """
        self.current_game = game
        self.try_show_mods()

    def on_reload_game(self):
        """当重新加载游戏时触发, 这会清空 mod 列表并设置 current_game = None
        """
        self.current_game = None
        self.mod_list.clear()

    def on_load_mod_over(self, mods: list[Mod]):
        self.set_loading(False)

    def on_mod_main_button_click(self, item: int | str, value, data: ModItem):
        """当ModItem的主要按钮按下
        """
        mod = data.mod
        if mod.is_enabled():
            mod.disable()
            dpg.set_item_label(data.main_button_ui, Fonts.is_disabled_text)
        else:
            mod.enable()
            dpg.set_item_label(data.main_button_ui, Fonts.is_enabled_text)
        data.reshow_info()

    def on_mod_minor_button_click(self, item: int | str, value, data: ModItem):
        """当ModItem的次要按钮按下
        """
        from gui.MainWindow import MainWindow

        def _del_mod(mod: Mod):
            if not self.current_game:
                return
            self.mod_list.remove(mod)
            self.current_game.remove_mod(mod)

        MainWindow.get.mod_menu.show(data.mod, show_to_local_button=True,
                                     on_delete_mod=_del_mod)
