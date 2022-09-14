import dearpygui.dearpygui as dpg

from gui.Components import ComponentBase


class ListView(ComponentBase):
    """列表基类, 通过 dpg 的 ChildWindow 实现"""
    def __init__(self):
        super().__init__()
        self.values: list[int | str] = []

    def setup(self, **kwargs):
        with dpg.child_window(**kwargs) as window:
            self.ui = window  # type: ignore

    def add(self, item: int | str):
        """添加一个控件

        Args:
            item: 控件 tag
        """
        dpg.move_item(item, parent=self.ui)
        self.values.append(item)

    def remove(self, item: int | str):
        """删除一个控件

        Args:
            item: 控件 tag
        """
        dpg.delete_item(item)
        self.values.remove(item)

    def clear(self):
        """清除全部内容
        """
        for i in self.values:
            dpg.delete_item(i)
        self.values.clear()
