""" 图片缓存, 用来暂存 mod 的缩略图, 加快反复刷新 mod 列表时的响应速度
"""
import os
from io import BytesIO

import dearpygui.dearpygui as dpg
from PIL.Image import Resampling, Image, open as open_image
from data import ModFile

cache: dict[ModFile, int | str] = {}


def get(mod: ModFile, height: int = 180) -> int | str:
    """获取某个 mod 的缩略图, 若已经缓存则直接返回, 否则生成
    """
    if mod not in cache:
        icon = mod.get_icon()
        if not icon:
            return 0
        img: Image = open_image(BytesIO(icon))
        img = img.resize((height, height), Resampling.NEAREST)
        img.save('./___temp___.png')

        width, height, _, img_data = dpg.load_image('./___temp___.png')

        os.remove('./___temp___.png')

        with dpg.texture_registry():
            cache[mod] = dpg.add_static_texture(width, height, img_data)

    return cache[mod]


def remove(mod: ModFile | list[ModFile]):
    """移除某些已经缓存好的mod缩略图,释放内存(其实也占不了多少地方)
    """
    if isinstance(mod, list):
        for m in mod:
            remove(m)
        return
    if mod in cache:
        dpg.delete_item(cache[mod])
        del cache[mod]


def clear():
    """清空全部缓存的图片"""
    remove(list(cache.keys()))
