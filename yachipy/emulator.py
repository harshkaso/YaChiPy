import dearpygui.dearpygui as dpg
from .cpu import Chip8CPU
from .screen import Chip8Screen
from.config import MEM_SIZE, ROM_FOLDER, SCALE, KEY_MAP_R, ACCENT_COLOR, NEUTRAL_COLOR, DULL_COLOR, SCREEN_HEIGHT, SCREEN_WIDTH
import time
import threading

class Chip8:
    def __init__(self) -> None:
        self._paused= True
        self.cpu_clockspeed = 500
        self.current_time, self.accumulator = 0, 0
        self.rom_selected = False

        dpg.create_context()
        dpg.setup_dearpygui()
        with dpg.handler_registry():
            dpg.add_key_down_handler(callback=self.key_down_handler)
            dpg.add_key_release_handler(callback=self.key_release_handler)
        with dpg.window(label='emulator') as emulator:
            self.screen = Chip8Screen()
            self.cpu = Chip8CPU(screen=self.screen)
            
            self.emulator_display = self.screen.show_emulator_display()
            self.show_general_settings()
            self.show_register_display()
            self.show_memory_display()
            self.show_keypad_display()
            self.show_info_display()
            dpg.set_primary_window(emulator, True)

        dpg.create_viewport(title='YaChiPy')
        # dpg.set_exit_callback(callback=self.cpu.terminate)


    def key_down_handler(self, sender, data):
        if data[0] in KEY_MAP_R.keys():
            btn_tag = str(KEY_MAP_R[data[0]])
            with dpg.theme() as highlight:
                with dpg.theme_component(dpg.mvAll):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, ACCENT_COLOR)
            dpg.bind_item_theme(btn_tag, highlight)
    
    def key_release_handler(self, sender, data):
        if data in KEY_MAP_R.keys():
            btn_tag = str(KEY_MAP_R[data])
            with dpg.theme() as dehighlight:
                with dpg.theme_component(dpg.mvAll):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, NEUTRAL_COLOR)
            dpg.bind_item_theme(btn_tag, dehighlight)
        # with dpg.theme() as highlight:
        #     with dpg.theme_component(dpg.mvAll):
        #         dpg.add_theme_color(dpg.mvThemeCol_Button, sender,)

    
    def load_rom(self, sender, data):
        self.cpu.reset()
        rom_info = list(data['selections'].items())[0]
        self.cpu.load_into_memory(rom_info[1])
        dpg.configure_item('rom_selector', label=rom_info[0])
        dpg.configure_item('pause_button', label='Start')
        self.screen.clear_screen()
        if not self.rom_selected:
            self.rom_selected = True

    def open_file_dialog(self, sender, data):
        if not self._paused:
            self.toggle_pause() 
        dpg.show_item("file_dialog")

    def toggle_pause(self) -> None:
        if not self.rom_selected:
            with dpg.window(label='Alert', width=500, height=100, popup=True):
                dpg.add_text(default_value='Please select a rom first.')
            return
        self._paused = not self._paused
        if self._paused:
            dpg.configure_item('pause_button', label='Resume')
            dpg.configure_item('tick_button', enabled=True)
        else:
            dpg.configure_item('pause_button', label='Pause')
            dpg.configure_item('tick_button', enabled=False)
            self.current_time = time.perf_counter()
    
    def set_clockspeed(self, sender, data):
        self.cpu_clockspeed = data

    def set_pixel_off_color(self, sender, data):
        color = [int(i*255) for i in data]
        self.screen.set_pixel_off_color(color)
        
    def set_pixel_on_color(self, sender, data):
        color = [int(i*255) for i in data]
        self.screen.set_pixel_on_color(color)
    
    def render_chip8_display(self) -> None:
        if self._paused:
            return
        new_time = time.perf_counter()
        frame_time = new_time - self.current_time
        self.current_time = new_time
        self.accumulator += frame_time
        cpu_delta_time = 1/self.cpu_clockspeed
        while self.accumulator >= cpu_delta_time:
            self.cpu.tick()
            self.accumulator -= cpu_delta_time

    def show_general_settings(self):
        with dpg.child_window(tag='utility_window', width=200, height=32*SCALE, pos=[0,0]):
            dpg.add_text(default_value='GENERAL SETTINGS')

            with dpg.file_dialog(tag='file_dialog', default_path=ROM_FOLDER, callback=self.load_rom, width=700, height=400, modal=True, show=False):
                dpg.add_file_extension('.*')

            with dpg.child_window():
                dpg.add_button(label='Select Rom', tag='rom_selector', callback=self.open_file_dialog , width=-1)
                dpg.add_spacer()


                with dpg.group(horizontal=True):
                    dpg.add_button(label= 'Start', tag='pause_button', width=80, callback=self.toggle_pause)
                    dpg.add_button(label= 'Tick', tag='tick_button', width=80, callback=lambda: self.cpu.tick(), enabled=False)
                dpg.add_spacer()
                
                dpg.add_separator()
                dpg.add_text(default_value='CPU Clockspeed (Hz)')
                dpg.add_slider_int(tag='cpu_clockspeed', width=-1, min_value=10, default_value=500, max_value=1000, callback=self.set_clockspeed)
                dpg.add_spacer()
                
                dpg.add_separator()
                dpg.add_text(default_value='Pixel Colors')
                with dpg.group(horizontal=True):
                    dpg.add_color_edit(default_value=self.screen.color_pixel_off, callback=self.set_pixel_off_color)
                    dpg.add_text(default_value='OFF', color=ACCENT_COLOR)
                with dpg.group(horizontal=True):
                    dpg.add_color_edit(default_value=self.screen.color_pixel_on, callback=self.set_pixel_on_color)
                    dpg.add_text(default_value='ON', color=ACCENT_COLOR)

    
    def show_register_display(self):
        self.v =[None]*len(self.cpu.v)
        with dpg.child_window(tag='register_window', width=200, height=32*SCALE, pos=[64*SCALE+200, 0]):
            dpg.add_text(default_value='REGISTERS')
            with dpg.child_window():
                for i in range(8):
                    with dpg.group(horizontal=True):
                        dpg.add_text(default_value='V'+hex(i).upper()[-1]+':', color=ACCENT_COLOR)
                        self.v[i] = dpg.add_text(default_value=hex(self.cpu.v[i])[2:].zfill(2).upper())
                        dpg.add_spacer()
                        dpg.add_text(default_value='V'+hex(i+8).upper()[-1]+':', color=ACCENT_COLOR)
                        self.v[i+8] = dpg.add_text(default_value=hex(self.cpu.v[i+8])[2:].zfill(2).upper())

                dpg.add_separator()

                with dpg.group(horizontal=True):
                    dpg.add_text(default_value='PC:', color=ACCENT_COLOR)
                    self.pc = dpg.add_text(default_value=hex(self.cpu.pc)[2:].zfill(3).upper())

                with dpg.group(horizontal=True):
                    dpg.add_text(default_value='SP:', color=ACCENT_COLOR)
                    self.sp = dpg.add_text(default_value=hex(self.cpu.sp)[2:].zfill(3).upper())

                with dpg.group(horizontal=True):
                    dpg.add_text(default_value='I :', color=ACCENT_COLOR)
                    self.i = dpg.add_text(default_value=hex(self.cpu.i)[2:].zfill(3).upper())
                
                with dpg.group(horizontal=True):
                    dpg.add_text(default_value='ST:', color=ACCENT_COLOR)
                    self.st = dpg.add_text(default_value=hex(self.cpu.st)[2:].zfill(3).upper())
                
                with dpg.group(horizontal=True):
                    dpg.add_text(default_value='DT:', color=ACCENT_COLOR)
                    self.dt = dpg.add_text(default_value=hex(self.cpu.dt)[2:].zfill(3).upper())

                
    def show_memory_display(self):
        self.memory = [None] * MEM_SIZE
        with dpg.child_window(tag='memory_display', width=64*SCALE, height=-1, pos=[0,32*SCALE]):
            dpg.add_text(default_value='MEMORY')
            with dpg.child_window():
                for i in range(0, MEM_SIZE, 16):
                    with dpg.group(horizontal=True):
                        dpg.add_text(default_value=hex(i)[2:-1].zfill(2).upper()+'X:', color=ACCENT_COLOR)
                        dpg.add_spacer()
                        for j in range(16):
                            if j == 8:
                                dpg.add_spacer()
                            
                            color = None
                            byte = self.cpu.memory[i+j]
                            if byte == 00:
                                color = [150,150,150]
                                color = DULL_COLOR
                            self.memory[i+j] = dpg.add_text(default_value=hex(self.cpu.memory[i+j])[2:].zfill(2).upper(), color=color)
    
    def show_keypad_display(self):
        with dpg.child_window(tag='keypad_display', width=400, height=-1, pos=[64*SCALE, 32*SCALE]):
            dpg.add_text(default_value='KEYPAD')
            # dpg.add_separator()
            with dpg.child_window(tag='keypad'):
                with dpg.group(horizontal=True):
                    dpg.add_button(width=86, height=100, label='1', tag='1')
                    dpg.add_button(width=86, height=100, label='2', tag='2')
                    dpg.add_button(width=86, height=100, label='3', tag='3')
                    dpg.add_button(width=86, height=100, label='C', tag='12')
            
                with dpg.group(horizontal=True):
                    dpg.add_button(width=86, height=100, label='4', tag='4')
                    dpg.add_button(width=86, height=100, label='5', tag='5')
                    dpg.add_button(width=86, height=100, label='6', tag='6')
                    dpg.add_button(width=86, height=100, label='D', tag='13')


                with dpg.group(horizontal=True):
                    dpg.add_button(width=86, height=100, label='7', tag='7')
                    dpg.add_button(width=86, height=100, label='8', tag='8')
                    dpg.add_button(width=86, height=100, label='9', tag='9')
                    dpg.add_button(width=86, height=100, label='E', tag='14')

                with dpg.group(horizontal=True):
                    dpg.add_button(width=86, height=100, label='A', tag='10')
                    dpg.add_button(width=86, height=100, label='0', tag='0')
                    dpg.add_button(width=86, height=100, label='B', tag='11')
                    dpg.add_button(width=86, height=100, label='F', tag='15')
        
        with dpg.theme() as keypad_themes:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, x=8, y=8)
        dpg.bind_item_theme('keypad', keypad_themes)

    def show_info_display(self):
        with dpg.child_window(width=-1, height=-1, pos=[64*SCALE+400,0]):
            dpg.add_text(default_value='INFORMATION')
            with dpg.child_window() as info_window:
                with open('yachipy/app_info.txt', 'r') as file:
                    dpg.add_text(default_value=file.read(), wrap=dpg.get_item_height(info_window))




    def update_register_display(self):
        for i in self.cpu.update_indices['registers']:
            dpg.set_value(self.v[i], hex(self.cpu.v[i])[2:].zfill(2).upper())
        self.cpu.update_indices['registers']=set([])
        
        dpg.set_value(self.pc, hex(self.cpu.pc)[2:].zfill(3).upper())
        dpg.set_value(self.sp, hex(self.cpu.sp)[2:].zfill(3).upper())
        dpg.set_value(self.i, hex(self.cpu.i)[2:].zfill(3).upper())
        dpg.set_value(self.st, hex(self.cpu.st)[2:].zfill(3).upper())
        dpg.set_value(self.dt, hex(self.cpu.dt)[2:].zfill(3).upper())
    
    def update_memory_display(self):
        for i in self.cpu.update_indices['memory']:
            color = None
            if self.cpu.memory[i] == 0:
                color = NEUTRAL_COLOR
            dpg.configure_item(self.memory[i], default_value=hex(self.cpu.memory[i])[2:].zfill(2).upper(), color=color)
        self.cpu.update_indices['memory']=set([])

    # def bind_themes(self) -> None:
    #     with dpg.theme() as emulator_theme:
    #         with dpg.theme_component(dpg.mvAll):
    #             dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0)
    #             dpg.add_theme_color(dpg.mvThemeCol_ChildBg, self.screen.color_pixel_off, category=dpg.mvThemeCat_Core)

    #     dpg.bind_item_theme(self.emulator_display, emulator_theme)


    def run(self) -> None:
        # Do bunch of other setups if required
        # self.bind_themes()
        dpg.show_viewport()
        # dpg.show_metrics()
        dpg.show_style_editor()
        dpg.maximize_viewport()
        dpg.set_viewport_vsync(False)

        

        # threading.Thread(target=self.cpu.run, args=[]).start()
        # dpg.start_dearpygui()

        self.current_time = time.perf_counter()
        while dpg.is_dearpygui_running():
            self.render_chip8_display()
            self.cpu.tick_timers()
            self.update_register_display()
            self.update_memory_display()
            dpg.render_dearpygui_frame()

        dpg.destroy_context()
        