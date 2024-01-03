import dearpygui.dearpygui as dpg

KEY_MAP = {
    dpg.mvKey_X: 0x0,
    dpg.mvKey_1: 0x1,
    dpg.mvKey_2: 0x2,
    dpg.mvKey_3: 0x3,
    dpg.mvKey_Q: 0x4,
    dpg.mvKey_W: 0x5,
    dpg.mvKey_E: 0x6,
    dpg.mvKey_A: 0x7,
    dpg.mvKey_S: 0x8,
    dpg.mvKey_D: 0x9,
    dpg.mvKey_Z: 0xA,
    dpg.mvKey_C: 0xB,
    dpg.mvKey_4: 0xC,
    dpg.mvKey_R: 0xD,
    dpg.mvKey_F: 0xE,
    dpg.mvKey_V: 0xF,
}

class Chip8Keyboard:
    def __init__(self) -> None:
        self.key_buffer = [0] * 16
        with dpg.handler_registry():
            dpg.add_key_down_handler(callback=self.key_down_handler)
            dpg.add_key_release_handler(callback=self.key_release_handler)


    def key_down_handler(self, sender, data) -> None:
        if data[0] in KEY_MAP:
            self.key_buffer[KEY_MAP[data[0]]] = 1


    def key_release_handler(self, sender, data) -> None:
        if data in KEY_MAP:
            self.key_buffer[KEY_MAP[data]] = 0

    def is_key_down(self, key) -> bool:
        return bool(self.key_buffer[key])
    
    def get_pressed_key(self) -> int:
        try:
            return self.key_buffer.index(1)
        except:
            return -1

