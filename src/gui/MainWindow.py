import dearpygui.dearpygui as dpg
from dearpygui.demo import show_demo

from gui import Fonts, Theme
from gui.components import center_group
from gui.components.InstallModMenu import InstallModMenu
from gui.components.ModMenu import ModMenu
from gui.pages import PageBase
from gui.pages.DownloadPage import DownloadPage
from gui.pages.GamePage import GamePage
from gui.pages.LocalPage import LocalPage
from gui.pages.SettingsPage import SettingsPage
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
