import dearpygui.dearpygui as dpg
from .config import DISP_BUFFER_SIZE, SCALE

class Chip8Screen:
    def __init__(self) -> None:
        self.disp_buffer = [None] * DISP_BUFFER_SIZE
        self.color_pixel_off = [244,180,26, 255]
        self.color_pixel_on = [20,61,89, 255]

        

    def clear_screen(self):
        for pixel in self.disp_buffer:
            dpg.configure_item(pixel, show=False)
    
    def turn_pixel_on(self, idx):
        dpg.configure_item(self.disp_buffer[idx], show=True)
    
    def turn_pixel_off(self, idx):
        dpg.configure_item(self.disp_buffer[idx], show=False)
    
    def is_pixel_on(self, idx):
        return dpg.is_item_shown(self.disp_buffer[idx])
    
    def show_emulator_display(self) -> dpg.window:
        with dpg.child_window(tag='display', width=64*SCALE, height=32*SCALE, pos=[200,0]) as display:
            with dpg.drawlist(width=64*SCALE, height=32*SCALE, tag='pixel_matrix') as pixel_matrix:
                for idx in range(DISP_BUFFER_SIZE):
                    x = (idx % 64) * SCALE
                    y = (idx // 64) * SCALE
                    self.disp_buffer[idx] = dpg.draw_rectangle(pmin=[x,y], pmax=[x+SCALE,y+SCALE], fill=self.color_pixel_on, color=self.color_pixel_on, show=False)
        
        with dpg.theme() as emulator_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0)
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, self.color_pixel_off, category=dpg.mvThemeCat_Core)

        dpg.bind_item_theme('display', emulator_theme)
        self.display = display
        return display
    
    def set_pixel_off_color(self, color):
        self.color_pixel_off = color
        with dpg.theme() as background_color:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0)
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, color, category=dpg.mvThemeCat_Core)

        dpg.bind_item_theme(self.display, background_color)

    def set_pixel_on_color(self, color):
        self.color_pixel_on = color
        for idx in range(DISP_BUFFER_SIZE):
            dpg.configure_item(self.disp_buffer[idx], fill=color, color=color)