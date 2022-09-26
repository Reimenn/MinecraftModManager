from os import link, system
from typing import Callable

import dearpygui.dearpygui as dpg
from data import ModFile, ModManager
from gui.components import ComponentBase


class ModMenu(ComponentBase):
    """对一个mod进行操作的菜单, 用在ModItem的次要按钮中. 包含查看详细信息, 删除mod, 前往主页等操作.
    """

    def __init__(self) -> None:
        super().__init__()
        self.width = 200
        self.mod: ModFile | None = None
        self.delete_click_count: int = 0

        self.mod_info_win_ui: str | int = 0
        self.to_homepage_btn_ui: str | int = 0
        self.delete_btn_ui: str | int = 0
        self.to_local_btn_ui: str | int = 0

        self.on_delete_mod: Callable[[ModFile], None] | None = None

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

    def show(self, mod: ModFile, *,
             on_delete_mod: Callable[[ModFile], None] | None = None,
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

        links = {}
        for info in mod.mod_info:
            links.update(info.links)
        dpg.configure_item(self.to_homepage_btn_ui, show='homepage' in links)
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
        label = "MOD 信息 - " + '|'.join(mod.get_names())
        with dpg.window(label=label) as self.mod_info_win_ui:  # type: ignore
            with dpg.table(header_row=False, resizable=True, reorderable=True):
                dpg.add_table_column(init_width_or_weight=3)
                dpg.add_table_column(init_width_or_weight=6)

                row_start = ''

                def row(left: str, right: str):
                    with dpg.table_row():
                        with dpg.table_cell():
                            dpg.add_text(row_start + left)
                        with dpg.table_cell():
                            dpg.add_text(right)

                row('文件路径', mod.get_full_path())

                for info in mod.mod_info:
                    row(f"在 {info.loader} 加载器中的信息：", '')
                    row_start = '\t'
                    row('名称', info.name)
                    row('mod 描述', info.description)
                    row('mod id', info.mod_id)
                    for provide in info.provide_mods_id:
                        row('provide id', provide)
                    row('mod 版本', info.version)
                    for k, v in info.links.items():
                        row(f'外部链接 {k}', v)
                    row('对应 mc 版本', info.mc_version)
                    row('需要的 mod 加载器', info.loader)
                    for dep in info.dependencies:
                        if dep.mandatory:
                            row('必备前置 mod', dep.mod_id +
                                ': ' + dep.version_range)
                    for dep in info.dependencies:
                        if not dep.mandatory:
                            row('可选前置 mod', dep.mod_id +
                                ': ' + dep.version_range)
                    for child in info.child_mods:
                        row('内部子 mod', str(child.get_names()) +
                            " id => " + str(child.get_ids()))
                    row_start = ''

    def to_homepage(self):
        if self.mod is None:
            return

        link = None
        for info in self.mod.mod_info:
            links = list(info.links.values())
            if links:
                link = links[0]
        self.hide()
        if link:
            import webbrowser
            webbrowser.open(link)

    def rename(self):
        # TODO: mod 文件重命名
        print("重命名！！！")

    def open_file_pos(self):
        if self.mod:
            self.hide()
            system(f'explorer /select, "{self.mod.full_file_path}')

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
