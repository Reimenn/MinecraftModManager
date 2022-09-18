import abc

import dearpygui.dearpygui as dpg
from gui import last_window

tItem = int | str


class ComponentBase(object):
    """组件基类
    """

    def __init__(self):
        self.ui: tItem = -1
        """组件在 dpg 中的 tag"""

    @abc.abstractmethod
    def setup(self):
        """安装组件"""
        pass

    def show(self):
        dpg.show_item(self.ui)

    def hide(self):
        dpg.hide_item(self.ui)


class center_group:
    """水平居中对齐组件,需要用 with 语法在其中添加子控件"""

    def __init__(self, window: tItem | None = None, horizontal_spacing: int = -1):
        self.horizontal_spacing = horizontal_spacing
        self.window = window
        if self.window is None:
            self.window = last_window()
        self.child_window: int | str = 0
        self.left: int | str = 0
        self.center: int | str = 0

    def __enter__(self) -> tItem:
        self.child_window = dpg.add_child_window(border=False)
        dpg.push_container_stack(self.child_window)

        line_group = dpg.add_group(horizontal=True)
        dpg.push_container_stack(line_group)

        self.left = dpg.add_group(horizontal=True)
        dpg.add_child_window(border=False, parent=self.left)

        self.center = dpg.add_group(
            horizontal=True, horizontal_spacing=self.horizontal_spacing)
        dpg.pop_container_stack()
        dpg.pop_container_stack()
        dpg.push_container_stack(self.center)

        with dpg.item_handler_registry() as handler:
            dpg.add_item_resize_handler(callback=self.rerender)
        dpg.bind_item_handler_registry(self.window, handler)  # type: ignore
        return self.child_window

    def __exit__(self, exc_type, exc_val, exc_tb):
        dpg.pop_container_stack()

    def rerender(self, item: int | str | None, value, data):
        parent_width = dpg.get_item_rect_size(self.child_window)[0]
        item_width = dpg.get_item_rect_size(self.center)[0]
        dpg.set_item_height(self.child_window,
                            dpg.get_item_rect_size(self.center)[1])
        width = int((parent_width - item_width) / 2) - 30
        width = max(width, 1)
        dpg.set_item_width(self.left, width)
