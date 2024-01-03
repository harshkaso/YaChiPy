import dearpygui.dearpygui as dpg
from random import randint
from .config import SCREEN_WIDTH, SCREEN_HEIGHT, MEM_SIZE, PROG_COUNTER, FONT, KEY_MAP

class Chip8CPU:
    def __init__(self, screen) -> None:
        # MEMORY
        self.memory = bytearray(MEM_SIZE)
        # REGISTERS
        self.v = [0] * 16
        self.i = 0
        self.sp = 0x52
        self.pc = PROG_COUNTER
        # TIMER
        self.st = 0
        self.dt = 0
        
        # DEBUG VARIABLES
        self.update_indices = {
            'registers': set([]),
            'memory': set([]),
        }

        self.operation_lookup = {
            0x0000: self._0___,
            0x1000: self._1NNN,
            0x2000: self._2NNN,
            0x3000: self._3XNN,
            0x4000: self._4XNN,
            0x5000: self._5XY0,
            0x6000: self._6XNN,
            0x7000: self._7XNN,
            0x8000: self._8___,
            0x9000: self._9XY0,
            0xA000: self._ANNN,
            0xB000: self._BNNN,
            0xC000: self._CXNN,
            0xD000: self._DXYN,
            0xE000: self._E___,
            0xF000: self._F___,
        }
        
        self.opcode = None
        self.screen = screen

        self.load_into_memory(FONT, 0)
        

    def __str__(self) -> str:
        pass
    
    def reset(self):
        # MEMORY
        self.memory = bytearray(4096)
        # REGISTERS
        self.v = [0] * 16
        self.i = 0
        self.sp = 0x52
        self.pc = PROG_COUNTER
        # TIMER
        self.st = 0
        self.dt = 0
        self.opcode = None
        self.load_into_memory(FONT, 0)
        # DEBUG VARIABLES
        self.update_indices = {
            'registers': set([]),
            'memory': set([]),
        }



    def load_into_memory(self, file: list|str, mem_origin: int = PROG_COUNTER) -> bool:
        try:
            if isinstance(file, str):
                with open(file, 'rb') as rom:
                    rom_content = rom.read()
            elif isinstance(file, list):
                rom_content = bytes(file)
            self.memory[mem_origin : mem_origin + len(rom_content)] = rom_content
            self.update_indices['memory'].update([i for i in range(mem_origin, mem_origin+len(rom_content))])
            return True

        except FileNotFoundError as error:
            print(f'[Exception]: {error}')
            return False
    
    def tick(self, opcode:int=None) -> int:
        if opcode:
            self.opcode = opcode
        else:
            self.opcode = self.memory[self.pc] << 8 | self.memory[self.pc + 1]
            self.pc += 2
        
        operation = self.opcode & 0xF000
        try:
            self.operation_lookup[operation]()
        except KeyError as error:
            print(f'[ERROR] - Invalid Opcode')
        return self.opcode

    def tick_timers(self) -> None:
        if self.st > 0:
            self.st -= 1
        if self.dt > 0:
            self.dt -= 1
    
    def _0___(self) -> None:
        # Further decoding required
        if self.opcode == 0x00E0:
            self._00E0()
        elif self.opcode == 0x00EE:
            self._00EE()
    
    def _00E0(self) -> None:
        # Clear the screen.
        self.screen.clear_screen()
    
    def _00EE(self) -> None:
        # Return from Subroutine
        self.sp -= 1
        self.pc = self.memory[self.sp] << 8
        self.sp -= 1
        self.pc += self.memory[self.sp]
    
    def _1NNN(self) -> None:
        # Jump to address NNN
        nnn = self.opcode & 0x0FFF
        self.pc = nnn
    
    def _2NNN(self) -> None:
        # Call subroutine at NNN
        nnn = self.opcode & 0x0FFF
        self.memory[self.sp] = self.pc & 0x00FF
        self.sp += 1
        self.memory[self.sp] = (self.pc & 0xFF00) >> 8
        self.sp += 1
        self.pc = nnn
    
    def _3XNN(self) -> None:
        # Skips the next instruction if VX equals NN.
        x = (self.opcode & 0x0F00) >> 8 
        nn = self.opcode & 0x00FF
        if self.v[x] == nn:
            self.pc += 2
    
    def _4XNN(self) -> None:
        # Skips the next instruction if VX does not equal NN.
        x = (self.opcode & 0x0F00) >> 8 
        nn = self.opcode & 0x00FF
        if self.v[x] != nn:
            self.pc += 2
    
    def _5XY0(self) -> None:
        # Skips the next instruction if VX equals VY.
        x = (self.opcode & 0x0F00) >> 8 
        y = (self.opcode & 0x00F0) >> 4
        if self.v[x] == self.v[y]:
            self.pc += 2 
        

    def _6XNN(self) -> None:
        # Sets VX to NN
        x = (self.opcode & 0x0F00) >> 8
        nn = self.opcode & 0x00FF
        self.v[x] = nn
        self.update_indices['registers'].update([x])

    
    def _7XNN(self) -> None:
        # Adds NN to VX. (Carry flag is not changed)
        x = (self.opcode & 0x0F00) >> 8
        nn = self.opcode & 0x00FF
        self.v[x] = (self.v[x] + nn) & 0xFF
        self.update_indices['registers'].update([x])

    def _8___(self) -> None:
        # Further decoding required
        operation = self.opcode & 0x000F
        if operation == 0x0000:
            self._8XY0()
        elif operation == 0x0001:
            self._8XY1()
        elif operation == 0x0002:
            self._8XY2()
        elif operation == 0x0003:
            self._8XY3()
        elif operation == 0x0004:
            self._8XY4()
        elif operation == 0x0005:
            self._8XY5()
        elif operation == 0x0006:
            self._8XY6()
        elif operation == 0x0007:
            self._8XY7()
        elif operation == 0x000E:
            self._8XYE()
    
    def _8XY0(self) -> None:
        # Sets VX to the value of VY.
        x = (self.opcode & 0x0F00) >> 8 
        y = (self.opcode & 0x00F0) >> 4
        self.v[x] = self.v[y]
        self.update_indices['registers'].update([x])


    def _8XY1(self) -> None:
        # Sets VX to VX or VY. (Bitwise OR operation);
        x = (self.opcode & 0x0F00) >> 8 
        y = (self.opcode & 0x00F0) >> 4
        self.v[x] |= self.v[y]
        self.update_indices['registers'].update([x])


    def _8XY2(self) -> None:
        # Sets VX to VX and VY. (Bitwise AND operation);
        x = (self.opcode & 0x0F00) >> 8 
        y = (self.opcode & 0x00F0) >> 4
        self.v[x] &= self.v[y]
        self.update_indices['registers'].update([x])


    def _8XY3(self) -> None:
        # Sets VX to VX xor VY.
        x = (self.opcode & 0x0F00) >> 8 
        y = (self.opcode & 0x00F0) >> 4
        self.v[x] ^= self.v[y]
        self.update_indices['registers'].update([x])



    def _8XY4(self) -> None:
        # Adds VY to VX. VF is set to 1 when there's a carry, and to 0 when there is not.
        x = (self.opcode & 0x0F00) >> 8 
        y = (self.opcode & 0x00F0) >> 4
        result = self.v[x] + self.v[y]
        carry = 0
        if result > 0xFF:
            result &= 0xFF
            carry = 1
        self.v[x] = result
        self.v[0xF] = carry
        self.update_indices['registers'].update([x, 0xF])


    def _8XY5(self) -> None:
        # VY is subtracted from VX. VF is set to 0 when there's a borrow, and 1 when there is not.
        x = (self.opcode & 0x0F00) >> 8 
        y = (self.opcode & 0x00F0) >> 4
        result = self.v[x] - self.v[y]
        borrow = 1
        if self.v[x] < self.v[y]:
            result &= 0xFF
            borrow = 0
        self.v[x] = result
        self.v[0xF] = borrow
        self.update_indices['registers'].update([x, 0xF])



    def _8XY6(self) -> None:
        # Stores the least significant bit of VX in VF and then shifts VX to the right by 1.
        x = (self.opcode & 0x0F00) >> 8 
        y = (self.opcode & 0x00F0) >> 4
        dropped_bit = self.v[x] & 0x1
        self.v[x] >>= 1
        self.v[0xF] = dropped_bit
        self.update_indices['registers'].update([x, 0xF])


    def _8XY7(self) -> None:
        # Sets VX to VY minus VX. VF is set to 0 when there's a borrow, and 1 when there is not.
        x = (self.opcode & 0x0F00) >> 8 
        y = (self.opcode & 0x00F0) >> 4
        result = self.v[y] - self.v[x]
        borrow = 1
        if self.v[y] < self.v[x]:
            result &= 0xFF
            borrow = 0
        self.v[x] = result
        self.v[0xF] = borrow
        self.update_indices['registers'].update([x, 0xF])


    def _8XYE(self) -> None:
        # Stores the most significant bit of VX in VF and then shifts VX to the left by 1.
        x = (self.opcode & 0x0F00) >> 8 
        y = (self.opcode & 0x00F0) >> 4
        dropped_bit = (self.v[x] & 0x80) >> 7
        self.v[x] = (self.v[x] << 1) & 0xFF
        self.v[0xF] = dropped_bit
        self.update_indices['registers'].update([x, 0xF])

    
    def _9XY0(self) -> None:
        # Skips the next instruction if VX does not equal VY. (Usually the next instruction is a jump to skip a code block)
        x = (self.opcode & 0x0F00) >> 8 
        y = (self.opcode & 0x00F0) >> 4
        if self.v[x] != self.v[y]:
            self.pc += 2

    def _ANNN(self) -> None:
        # Sets I to the address NNN.
        nnn = self.opcode & 0x0FFF
        self.i = nnn
    
    def _BNNN(self) -> None:
        # Jumps to the address NNN plus V0.
        nnn = self.opcode & 0x0FFF
        self.pc = self.v[0] + nnn
    
    def _CXNN(self) -> None:
        # Sets VX to the result of a bitwise and operation on a random number (Typically: 0 to 255) and NN.
        x = (self.opcode & 0x0F00) >> 8
        nn = self.opcode & 0x00FF
        rnd = randint(0, 0xFF)
        self.v[x] = rnd & nn
        self.update_indices['registers'].update([x])

    
    def _DXYN(self) -> None:
        # Draws a sprite at coordinate (VX, VY) that has a width of 8 pixels and a height of N pixels.
        # Each row of 8 pixels is read as bit-coded starting from memory location I;
        # I value does not change after the execution of this instruction. As described above,
        # VF is set to 1 if any screen pixels are flipped from set to unset when the sprite is drawn, and to 0 if that does not happen
        x = (self.opcode & 0x0F00) >> 8
        y = (self.opcode & 0x00F0) >> 4
        n = self.opcode & 0x000F
        x_origin = self.v[x] % SCREEN_WIDTH
        y_origin = self.v[y] % SCREEN_HEIGHT
        self.v[0xF] = 0
        self.update_indices['registers'].update([0xF])
        for y_offset in range(n):
            sprite_pixel_row = bin(self.memory[self.i + y_offset])[2:].zfill(8)
            y_coord = y_origin + y_offset
            if y_coord >= SCREEN_HEIGHT: break

            for x_offset in range(8):
                x_coord = x_origin + x_offset
                if x_coord >= SCREEN_WIDTH: break
                
                idx = SCREEN_WIDTH * y_coord + x_coord
                sprite_pixel = int(sprite_pixel_row[x_offset])
                screen_pixel = self.screen.is_pixel_on(idx)

                if sprite_pixel and screen_pixel:
                    self.v[0xF] = 1
                    self.screen.turn_pixel_off(idx)
                elif sprite_pixel and not screen_pixel:
                    self.screen.turn_pixel_on(idx)
        
    def _E___(self) -> None:
        # Further decoding required
        operation = self.opcode & 0x000F
        if operation == 0x000E:
            self._EX9E()
        elif operation == 0x0001:
            self._EXA1()
    
    def _EX9E(self) -> None:
        # Skips the next instruction if the key stored in VX is pressed. (Usually the next instruction is a jump to skip a code block);
        x = (self.opcode & 0x0F00) >> 8
        if dpg.is_key_down(KEY_MAP[self.v[x]]):
            self.pc += 2
        
        

    def _EXA1(self) -> None:
        # Skips the next instruction if the key stored in VX is not pressed. (Usually the next instruction is a jump to skip a code block)
        x = (self.opcode & 0x0F00) >> 8
        if not dpg.is_key_down(KEY_MAP[self.v[x]]):
            self.pc += 2
    
    def _F___(self) -> None:
        operation = self.opcode & 0x00FF
        if operation == 0x0007:
            self._FX07()
        elif operation == 0x000A:
            self._FX0A()
        elif operation == 0x0015:
            self._FX15()
        elif operation == 0x0018:
            self._FX18()
        elif operation == 0x001E:
            self._FX1E()
        elif operation == 0x0029:
            self._FX29()
        elif operation == 0x0033:
            self._FX33()
        elif operation == 0x0055:
            self._FX55()
        elif operation == 0x0065:
            self._FX65()
    
    def _FX07(self) -> None:
        # Sets VX to the value of the delay timer.
        x = (self.opcode & 0x0F00) >> 8
        self.v[x] = self.dt
        self.update_indices['registers'].update([x])

    
    def _FX0A(self) -> None:
        # A key press is awaited, and then stored in VX. (Blocking Operation. All instruction halted until next key event)
        x = (self.opcode & 0x0F00) >> 8
        for key in KEY_MAP:
            if dpg.is_key_down(KEY_MAP[key]):
                self.v[x] = key
                self.update_indices['registers'].update([x])
                while dpg.is_key_down(KEY_MAP[key]):
                    dpg.render_dearpygui_frame()
                return
        self.pc -= 2


    def _FX15(self) -> None:
        # Sets the delay timer to VX.
        x = (self.opcode & 0x0F00) >> 8
        self.dt = self.v[x]

    def _FX18(self) -> None:
        # Sets the sound timer to VX.
        x = (self.opcode & 0x0F00) >> 8
        self.st = self.v[x]

    def _FX1E(self) -> None:
        # Adds VX to I. VF is not affected.
        x = (self.opcode & 0x0F00) >> 8
        self.i += self.v[x]
    
    def _FX29(self) -> None:
        # Sets I to the location of the sprite for the character in VX. Characters 0-F (in hexadecimal) are represented by a 4x5 font.
        x = (self.opcode & 0x0F00) >> 8
        self.i = 5 * self.v[x]

    def _FX33(self) -> None:
        # Stores the binary-coded decimal representation of VX, with the most significant of three digits at the address in I,
        # the middle digit at I plus 1, and the least significant digit at I plus 2. (In other words, take the decimal representation of VX,
        # place the hundreds digit in memory at location in I, the tens digit at location I+1, and the ones digit at location I+2.);
        x = (self.opcode & 0x0F00) >> 8
        bcd = f'{self.v[x]:03d}'
        self.memory[self.i] = int(bcd[0])
        self.memory[self.i + 1] = int(bcd[1])
        self.memory[self.i + 2] = int(bcd[2])


    def _FX55(self) -> None:
        # Stores V0 to VX (including VX) in memory starting at address I. The offset from I is increased by 1 for each value written, but I itself is left unmodified.
        x = (self.opcode & 0x0F00) >> 8
        self.memory[self.i : self.i + x + 1] = bytes(self.v[:x+1])
    
    def _FX65(self) -> None:
        # Fills V0 to VX (including VX) with values from memory starting at address I. The offset from I is increased by 1 for each value written, but I itself is left unmodified.
        x = (self.opcode & 0x0F00) >> 8
        self.v[:x+1] = self.memory[self.i : self.i + x + 1]