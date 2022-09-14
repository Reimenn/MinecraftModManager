import dearpygui.dearpygui as dpg


def last_window() -> str | int:
    buf: list = []
    result: str | int = -1
    while True:
        try:
            pop = dpg.pop_container_stack()
            buf.append(pop)
            if dpg.get_item_type(pop) == 'mvAppItemType::mvWindowAppItem':
                result = pop
                break
        except SystemError:
            break
    while buf:
        dpg.push_container_stack(buf.pop())
    if result is None:
        raise SystemError("not found last window")
    return result
