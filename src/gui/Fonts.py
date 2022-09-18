import dearpygui.dearpygui as dpg


class Fonts:
    font_s: int = 0
    font_b: int = 0
    is_disabled_text: str = '已被禁用'
    is_enabled_text: str = '使用中'


chars: str = '▼▽'


def __load():
    with dpg.font_registry():
        with dpg.font('SourceHanSansSC-Normal.otf', 32) as f:
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
            for i in chars:
                dpg.add_font_chars([ord(i) for i in chars])
            Fonts.font_s = f  # type: ignore
        with dpg.font('SourceHanSansSC-Normal.otf', 44) as f:
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
            for i in chars:
                dpg.add_font_chars([ord(i) for i in chars])
            Fonts.font_b = f  # type: ignore


def get_normal_font() -> int:
    if not Fonts.font_s:
        __load()
    assert Fonts.font_s
    return Fonts.font_s


def get_big_font() -> int:
    if not Fonts.font_b:
        __load()
    assert Fonts.font_b
    return Fonts.font_b
