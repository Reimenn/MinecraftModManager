import dearpygui.dearpygui as dpg
from gui.MainWindow import MainWindow
from gui.StateWatcher import watchers, on_update
from data.Settings import settings


def setup():
    dpg.create_context()

    dpg.create_viewport(x_pos=300)

    window = MainWindow()
    window.setup()

    dpg.setup_dearpygui()
    dpg.show_viewport()

    dpg.set_global_font_scale(settings.global_size)
    while dpg.is_dearpygui_running():
        for watcher in watchers:
            watcher.check()
        for update_fun in on_update:
            update_fun()
        dpg.render_dearpygui_frame()

    dpg.destroy_context()
