import abc
import dearpygui.dearpygui as dpg


class PageBase(object):
    """页面基类
    """
    def __init__(self):
        self.ui: str | int = -1

    def setup(self):
        """安装页面, 包含 child_window
        """
        with dpg.child_window(border=False, no_scrollbar=True) as window:
            self.ui = window  # type: ignore
            self.build_page()

    @abc.abstractmethod
    def build_page(self):
        """安装页面内部内容
        """
        pass

    def show(self):
        dpg.show_item(self.ui)

    def hide(self):
        dpg.hide_item(self.ui)


__all__ = [
    'PageBase'
]
