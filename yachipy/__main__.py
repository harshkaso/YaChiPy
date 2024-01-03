from .emulator import Chip8

# Entry Point
def main():
    chip8 = Chip8()
    chip8.run()

if __name__ == '__main__':
    main()