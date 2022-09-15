import dearpygui.dearpygui as dpg

from data.Settings import settings


def registry():
    with dpg.theme(tag='debug'):
        with dpg.theme_component():
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, [100, 10, 10, 100])
            dpg.add_theme_color(dpg.mvThemeCol_Border, [200, 40, 40, 255])
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 2)

    with dpg.theme(tag='main'):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 0, 0)
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarSize,
                                settings.get_size(20))

    with dpg.theme(tag='zero'):
        with dpg.theme_component():
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 0)

    with dpg.theme(tag='list_zero'):
        with dpg.theme_component():
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 12)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0)

    with dpg.theme(tag='button_zero'):
        with dpg.theme_component():
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0)

    with dpg.theme(tag='tab_button_active'):
        with dpg.theme_component():
            dpg.add_theme_color(dpg.mvThemeCol_Button,
                                value=(29, 151, 236, 103))

    with dpg.theme(tag='tab_theme'):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_style()
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 40, 8)
