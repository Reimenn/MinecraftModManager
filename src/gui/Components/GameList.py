from ast import Call
from typing import Callable

import dearpygui.dearpygui as dpg
from data import ModManager
from data.GameInfo import Game
from gui.components import ComponentBase
from gui.Fonts import Fonts

tUI = int | str


class GameList(ComponentBase):
    """游戏列表,包含游戏信息, 刷新按钮, 游戏列表"""
    def __init__(self, show_reload_button: bool = True,
                 on_selected_game: Callable[[Game], None] | None = None,
                 on_reloaded_game: Callable[[], None] | None = None
                 ) -> None:
        """
        Args:
            reload_button: 是否显示刷新按钮. Defaults to True.
            on_selected_game: 选择一个游戏时触发. Defaults to None.
            on_reloaded_game: 重载游戏完成后触发. Defaults to None.
        """
        self.show_reload_button: bool = show_reload_button
        self.on_selected_game: Callable[[
            Game], None] | None = on_selected_game

        self.ui: tUI = 0
        self.game_title_ui: tUI = 0
        self.game_info_ui: tUI = 0
        self.game_list_ui: tUI = 0
        self.reload_button_ui: tUI = 0
        self.show_items: list[str] = []
        self.selected_game: Game | None = None
        self.on_reloaded_game: Callable[[], None] | None = on_reloaded_game

    def setup(self) -> None:
        with dpg.child_window(border=False) as self.ui:  # type: ignore
            self.game_title_ui = dpg.add_text(default_value=' ')
            dpg.bind_item_font(self.game_title_ui, Fonts.font_b)
            self.game_info_ui = dpg.add_text(default_value=' \n ')
            if self.show_reload_button:
                self.reload_button_ui = dpg.add_button(
                    label="刷新游戏列表", width=-4,
                    callback=self.reload_games)
            with dpg.child_window(border=False, autosize_x=True, autosize_y=True) as list_window:
                self.game_list_ui = dpg.add_listbox(
                    default_value='', width=-4,
                    callback=self.on_select_game)
                dpg.bind_item_theme(list_window, 'list_zero')  # type: ignore
        self.__update_list()

    def __update_list(self) -> None:
        dpg.configure_item(
            self.game_list_ui,
            num_items=len(self.show_items),
            items=self.show_items,
            default_value=''
        )

    def reload_games(self) -> None:
        """重新加载游戏
        """

        games = ModManager.get().get_games_or_load().copy()
        games.sort(key=lambda x: x.game_type + x.version)
        last_loader: str = ''
        self.show_items = []
        self.selected_game = None
        for game in games:
            if game.game_type != last_loader:
                last_loader = game.game_type
                self.show_items.append(f'- - - - < {last_loader} > - - - -')
            self.show_items.append(game.dir_name)
        self.__update_list()
        dpg.set_value(self.game_title_ui, '')
        dpg.set_value(self.game_info_ui,' \n ')
        if self.on_reloaded_game:
            self.on_reloaded_game()

    def on_select_game(self, item: tUI, value: str, data) -> None:
        """选择一个游戏后触发
        """
        for game in ModManager.get().get_games_or_load():
            if game.dir_name != value:
                continue
            dpg.set_value(self.game_title_ui, game.version)
            dpg.set_value(self.game_info_ui,
                          game.game_type + '\n' + game.dir_name)
            self.selected_game = game
            if self.on_selected_game:
                self.on_selected_game(game)
            break
        