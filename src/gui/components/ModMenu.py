from os import system
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
                row('mod 描述', mod.description)
                row('mod id', mod.mod_id)
                for provid in mod.provide_mods_id:
                    row('provid id', provid)
                row('mod 版本', mod.version)
                row('作者', mod.authors)
                row('主页', mod.homepage)
                row('文件路径', mod.full_file_path)
                row('对应 mc 版本', mod.mc_version)
                row('需要的 mod 加载器', mod.loader)
                for dep in mod.dependencis:
                    if dep.mandatory:
                        row('必备前置 mod', dep.mod_id + ': ' + dep.version_range)
                for dep in mod.dependencis:
                    if not dep.mandatory:
                        row('可选前置 mod', dep.mod_id + ': ' + dep.version_range)
                for child in mod.child_mods:
                    row('内部子 mod', child.name + ", " +
                        child.mod_id + ": " + child.version)

    def to_homepage(self):
        if not self.mod or not self.mod.homepage:
            return
        self.hide()
        import webbrowser
        webbrowser.open(self.mod.homepage)

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
