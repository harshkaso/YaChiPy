from .screen import Chip8Screen
from .keyboard import Chip8Keyboard

class IOController:
    def __init__(self) -> None:
        self.screen = Chip8Screen(debugger=True)
        self.keyboard  = Chip8Keyboard()

    def clear_screen(self) -> None:
        self.screen.clear_screen()
    
    def turn_pixel_on(self, idx) -> None:
        self.screen.turn_pixel_on(idx)
    
    def turn_pixel_off(self, idx) -> None:
        self.screen.turn_pixel_off(idx)

    def is_pixel_on(self, idx) -> None:
        return self.screen.is_pixel_on(idx)

    def is_key_down(self, key) -> bool:
        return self.keyboard.is_key_down(key)
    
    def get_pressed_key(self) -> int:
        return self.keyboard.get_pressed_key()