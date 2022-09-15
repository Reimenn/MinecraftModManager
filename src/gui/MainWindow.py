import os
from typing import Callable

import dearpygui.dearpygui as dpg
from data import Game, Mod, ModManager
from data.GameInfo import GameType
from dearpygui.demo import show_demo

from gui import Fonts, Theme
from gui.Components import center_group
from gui.Pages import PageBase
from gui.Pages.DownloadPage import DownloadPage
from gui.Pages.GamePage import GamePage
from gui.Pages.LocalPage import LocalPage
from gui.Pages.SettingsPage import SettingsPage
from gui.StateWatcher import StateWatcher, bind_watcher


class MainWindow:

    get: 'MainWindow'

    def __init__(self):
        self.ui: int | str = 0
        self.pages: dict[str, PageBase] = {}
        self.game_page: GamePage = None  # type: ignore
        self.local_page: LocalPage = None  # type: ignore
        self.settings_page: SettingsPage = None  # type: ignore
        self.install_mod_menu: InstallModMenu = InstallModMenu()
        self.mod_menu: ModMenu = ModMenu()
        MainWindow.get = self

    def setup(self):
        Theme.registry()
        with dpg.window(tag='main window', no_scrollbar=True) as main_window:  # type: ignore
            main_window: int | str
            self.ui = main_window
            dpg.bind_item_theme(main_window, 'main')
            dpg.bind_font(Fonts.get_normal_font())
            dpg.set_primary_window(main_window, True)
            self._setup_debug_menu_bar()
            self._setup_tabs()
            self.install_mod_menu.setup(main_window)
            self.mod_menu.setup(main_window)

    def _setup_debug_menu_bar(self):
        with dpg.menu_bar():
            dpg.add_menu_item(label='开发调试用工具栏')
            dpg.add_menu_item(label='Font', callback=dpg.show_font_manager)
            dpg.add_menu_item(
                label='Style', callback=dpg.show_style_editor)
            dpg.add_menu_item(label='Debug', callback=dpg.show_debug)
            dpg.add_menu_item(label='Metrics', callback=dpg.show_metrics)
            dpg.add_menu_item(
                label='Item', callback=dpg.show_item_registry)
            dpg.add_menu_item(label='Demo', callback=show_demo)
            

    def _setup_tabs(self):
        buttons = []

        def _callback(item, value, data):
            for button in buttons:
                dpg.bind_item_theme(button, '')
            dpg.bind_item_theme(item, 'tab_button_active')
            [v.hide() for v in self.pages.values()]
            self.pages[data].show()
        group = center_group(horizontal_spacing=0)
        with group as group_ui:
            buttons.append(dpg.add_button(
                label='本地', user_data='local', callback=_callback))
            buttons.append(dpg.add_button(
                label='游戏', user_data='game', callback=_callback))
            buttons.append(dpg.add_button(
                label='下载', user_data='download', callback=_callback))
            buttons.append(dpg.add_button(
                label='设置', user_data='settings', callback=_callback))
            dpg.bind_item_theme(group_ui, 'tab_theme')
        dpg.add_child_window(border=False, height=10)

        def _hover(item):
            cw = dpg.get_item_width(item)
            if cw is None:
                cw = 0
            dpg.set_item_width(item, int((200 - cw) * 0.1) + cw)
            group.rerender(None, None, None)

        def _else_hover(item):
            cw = dpg.get_item_width(item)
            if cw is None:
                cw = 0
            dpg.set_item_width(item, int((150 - cw) * 0.1) + cw)
            group.rerender(None, None, None)

        for b in buttons:
            bind_watcher(StateWatcher(b, 'hovered', _hover, _else_hover))

        self._setup_pages()

    def _setup_pages(self):
        local_page = LocalPage()
        local_page.setup()
        local_page.hide()
        self.pages['local'] = local_page
        game_page = GamePage()
        game_page.setup()
        game_page.hide()
        self.pages['game'] = game_page
        download_page = DownloadPage()
        download_page.setup()
        download_page.hide()
        self.pages['download'] = download_page
        settings_page = SettingsPage()
        settings_page.setup()
        settings_page.hide()
        self.pages['settings'] = settings_page

class _base_menu(object):
    def __init__(self) -> None:
        self.ui: int | str = 0

    def hide(self):
        dpg.hide_item(self.ui)

    def show(self):
        dpg.show_item(self.ui)

    def setup(self, parent: int | str) -> None:
        pass


class InstallModMenu(_base_menu):
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
            self.selected_game.add_mod(self.mod)
        except Exception as e:
            print(e)

    def show(self, mod: Mod) -> None:
        self.mod = mod
        super().show()


class ModMenu(_base_menu):
    """对一个mod进行操作的菜单, 用在ModItem的次要按钮中. 包含查看详细信息, 删除mod, 前往主页等操作.
    """

    def __init__(self) -> None:
        super().__init__()
        self.width = 200
        self.mod: Mod | None = None
        self.delete_click_count: int = 0

        self.mod_info_win_ui: str | int = 0
        self.to_homepage_btn_ui: str | int = 0
        self.delete_btn_ui: str | int = 0
        self.to_local_btn_ui: str | int = 0

        self.on_delete_mod: Callable[[Mod], None] | None = None

    def setup(self, parent: int | str) -> None:
        dpg.push_container_stack(parent)
        temp = dpg.add_text()
        with dpg.popup(temp) as self.ui:  # type: ignore
            def _btn(label: str, callback) -> int | str:
                return dpg.add_button(label=label,
                                      callback=callback,
                                      width=self.width)

            _btn('详细信息', self.show_info)
            self.to_homepage_btn_ui = _btn('前往主页', self.to_homepage)
            dpg.add_spacer()
            _btn('重命名', self.rename)
            _btn('打开文件位置', self.open_file_pos)
            self.to_local_btn_ui = _btn('添加到仓库', self.add_to_local)
            dpg.add_spacer()
            self.delete_btn_ui = _btn('删除', self.delete)
        dpg.pop_container_stack()
        dpg.delete_item(temp)
        self.hide()

    def show(self, mod: Mod, *,
             on_delete_mod: Callable[[Mod], None] | None = None,
             show_delete_button: bool = True,
             show_to_local_button: bool = False):
        """显示Mod操作菜单

        Args:
            mod: Mod
            on_delete_mod: 确认删除mod时的回调,这里应该实现mod删除的具体操作,(确认删除的步骤这个ModMenu已经完成了). Defaults to None.
            show_delete_button: 是否显示删除mod按钮. Defaults to True.
            show_to_local_btn: 是否显示添加到仓库按钮. Defaults to False.
        """
        self.mod = mod
        self.on_delete_mod = on_delete_mod
        self.delete_click_count = 0
        dpg.set_item_label(self.delete_btn_ui, '删除')
        dpg.configure_item(self.to_homepage_btn_ui, show=bool(mod.homepage))
        dpg.configure_item(self.to_local_btn_ui, show=show_to_local_button)
        dpg.configure_item(self.delete_btn_ui, show=show_delete_button)
        super().show()

    def show_info(self):
        if not self.mod:
            return
        mod = self.mod
        if self.mod_info_win_ui:
            dpg.delete_item(self.mod_info_win_ui)
        self.hide()
        with dpg.window(label="MOD 信息 - " + mod.name) as self.mod_info_win_ui:  # type: ignore
            with dpg.table(header_row=False, resizable=True, reorderable=True):
                dpg.add_table_column(init_width_or_weight=3)
                dpg.add_table_column(init_width_or_weight=6)

                def row(left: str, right: str):
                    with dpg.table_row():
                        with dpg.table_cell():
                            dpg.add_text(left)
                        with dpg.table_cell():
                            dpg.add_text(right)

                row('名称', mod.name)
                row('mod id', mod.mod_id)
                row('mod 版本', mod.version)
                row('作者', mod.authors)
                row('主页', mod.homepage)
                row('文件路径', mod.full_file_path)
                row('对应 mc 版本', mod.mc_version)
                row('需要的 mod 加载器', mod.loader)
                row('依赖的 mod 或 库', str(mod.dependencis))
                row('mod 描述', mod.description)

    def to_homepage(self):
        if not self.mod:
            return

        if not self.mod.homepage:
            return
        self.hide()
        import webbrowser
        webbrowser.open(self.mod.homepage)

    def rename(self):
        if not self.mod:
            return
        dpg.push_container_stack(self.ui)
        temp = dpg.add_text()
        with dpg.popup(temp) as pop:
            input_ui = dpg.add_input_text(default_value=self.mod.name)

            def __rename():
                assert self.mod
                new_name = str(dpg.get_value(input_ui))
                if os.path.exists(os.path.join(self.mod.full_file_path, '../', new_name)):
                    pass
                else:
                    self.mod.rename_file(new_name)
            dpg.add_button(label='重命名', callback=__rename)
        dpg.show_item(pop)  # type: ignore
        dpg.delete_item(temp)
        dpg.pop_container_stack()

    def open_file_pos(self):
        if self.mod:
            self.hide()
            os.system(f'explorer /select, "{self.mod.full_file_path}')

    def delete(self):
        if not self.mod:
            return
        if self.delete_click_count == 0:
            dpg.set_item_label(self.delete_btn_ui, '确认删除？')
            self.delete_click_count += 1
        elif self.delete_click_count == 1:
            self.hide()
            if self.on_delete_mod:
                self.on_delete_mod(self.mod)

    def add_to_local(self):
        if self.mod:
            ModManager.get().add_mod(self.mod)
        self.hide()
