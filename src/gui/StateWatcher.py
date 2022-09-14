"""全局实现监听器, 用于实现每帧进行的一些动作
"""

import dearpygui.dearpygui as dpg
from typing import Callable

tItem = int | str
tState = str
tCallback = Callable[[tItem], None]
tElseCallback = Callable[[tItem], None]

check_cache: dict[str, Callable] = {}
for i in [i for i in dir(dpg) if i.startswith('is_item_')]:
    check_cache[i.split('_')[2]] = getattr(dpg, i)


class StateWatcher:
    """一个dpg控件的状态监听器
    """
    def __init__(self, item: tItem, state: tState,
                 callback: tCallback | None = None, else_callback: tElseCallback | None = None):
        self.else_callback = else_callback
        self.callback = callback
        self.item = item
        self.state = state

    def check(self):
        if check_cache[self.state](self.item):
            if self.callback:
                self.callback(self.item)
        else:
            if self.else_callback:
                self.else_callback(self.item)


watchers: list[StateWatcher] = []


def bind_watcher(watcher: StateWatcher):
    watchers.append(watcher)


def remove_watcher(item: int | str, state: str | None = None):
    remove_list = []
    for w in watchers:
        if item == w.item:
            if state is None:
                remove_list.append(w)
            elif state == w.state:
                remove_list.append(w)
    for r in remove_list:
        watchers.remove(r)


on_update: list[Callable[[], None]] = []
