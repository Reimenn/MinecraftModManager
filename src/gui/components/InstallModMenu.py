import dearpygui.dearpygui as dpg
from data import ModManager
from data.GameInfo import Game, GameType
from data.ModInfo import Mod
from gui.components import ComponentBase
from gui.pages.GamePage import GamePage


class InstallModMenu(ComponentBase):
    """安装mod的菜单, 这里包含游戏选择, 游戏信息显示和安装按钮, 用于把一个 mod 安装到一个 game 中
    """

    def __init__(self) -> None:
        super().__init__()
        self.width: int = 400

        self.version_ui: int | str = 0
        self.loader_ui: int | str = 0
        self.err_ui: int | str = 0

        self.selected_game: Game | None = None
        self.mod: Mod | None = None

    def setup(self, parent: int | str) -> None:
        dpg.push_container_stack(parent)
        temp = dpg.add_text('')
        with dpg.popup(temp, no_move=True) as self.ui:  # type: ignore
            dpg.add_text("安装到哪个游戏？")
            dpg.add_spacer()

            if not GamePage.get.game_list.show_items:
                GamePage.get.game_list.reload_games()
            items = GamePage.get.game_list.show_items
            dpg.add_combo(items=items, width=self.width,
                          callback=self.on_selected_game,
                          default_value='')

            self.version_ui = dpg.add_text()
            self.loader_ui = dpg.add_text()
            self.err_ui = dpg.add_text()
            dpg.hide_item(self.err_ui)
            dpg.add_button(label="安装 >", width=self.width,
                           callback=self.on_install_button_click)

        dpg.pop_container_stack()
        dpg.delete_item(temp)

    def on_selected_game(self, item, value: str, data):
        self.selected_game = None
        for game in ModManager.get().get_games_or_load():
            if game.dir_name != value:
                continue
            self.selected_game = game
            break
        # 若选择了不存在的游戏
        if not self.selected_game:
            dpg.set_value(self.version_ui, '')
            dpg.set_value(self.loader_ui, '')
            return
        # 更新界面
        game = self.selected_game
        dpg.set_value(self.version_ui, game.version)
        dpg.set_value(self.loader_ui, game.game_type)
        if game.game_type == GameType.other:
            dpg.set_value(self.err_ui, '未知的mod加载器，mod文件将会被安装到mods文件夹中。')
            dpg.show_item(self.err_ui)
        elif game.game_type == GameType.vanilla:
            dpg.set_value(self.err_ui, '注意：正在给原版游戏添加 mod')
            dpg.show_item(self.err_ui)
        else:
            dpg.hide_item(self.err_ui)

    def on_install_button_click(self, item, value, data):
        if not self.selected_game or not self.mod:
            self.hide()
            return
        try:
            self.hide()
            self.selected_game.add_mod(self.mod)
        except Exception as e:
            print(e)

    def show(self, mod: Mod) -> None:
        self.mod = mod
        super().show()
