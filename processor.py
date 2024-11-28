class MSP430Emulator:
    def __init__(self, offset):
        self.registers = [0] * 16
        self.PC = 0
        self.offset = offset
        self.memory = [0] * 1024
        self.program_size = 0
        self.compare_register = 0

    def load_program(self, program):
        self.memory[self.offset:] = [0] * (len(self.memory) - self.offset)
        for i, code in enumerate(program):
            self.memory[i + self.offset] = code
        self.program_size = len(program)
        self.PC = self.offset

    def step(self):
        instruction = self.memory[self.PC]
        if instruction is None or instruction == 0x0:
            self.PC += 1
            print("\nПустое поле команды")
            return
        self.execute_instruction(instruction)
        print(self.registers)

    def execute_instruction(self, instruction):
        opcode = instruction >> 12 # команда для выполнения
        s_type = (instruction & 0x0C00) >> 10 # тип адресации @\#\R
        src = (instruction & 0x03C0) >> 6 # само значение число
        d_type = (instruction & 0x0030) >> 4 #  тип адресации @\R
        dst = instruction & 0x000F # 2е значение число

        print(f"\nТекущая команда: {self.PC} {hex(instruction)}, src: {src}, dst: {dst}, As: {s_type}, Ad: {d_type}")

        src_value = self.get_value(src, s_type)
        dst_value = self.get_value(dst, d_type)

        match opcode:
            case 0x1:  # MOV
                self.set_value(dst, d_type, src_value)
                print(f"MOV: {src_value} -> R{dst}")
            case 0x2:  # CMP
                self.compare_register = 1 if dst_value - src_value < 0 else 0
                print(f"CMP: {dst_value} - {src_value} = {dst_value - src_value}; compare_register = {self.compare_register}")
            case 0x3:  # ADD
                new_value = dst_value + src_value
                self.set_value(dst, d_type, new_value)
                print(f"ADD: {src_value} + {dst_value} -> R{dst}")
            case 0x5:  # JLO
                self.PC = src + self.offset if self.compare_register == 1 else self.PC + 1  # проверка фага
                print(f"JLO: переход на {src} при compare_register = {self.compare_register}")
            case 0x7:  # JMP
                self.PC = src + self.offset
                print(f"JMP: переход на {self.PC}")
            case 0xF:  # NOP
                print("NOP: ничего не делаем")
                self.PC += 1
                raise UserWarning(f"Программа завершила своё выполнение")
            case _:
                raise ValueError(f"Неизвестная инструкция: {hex(opcode)}")
        if opcode not in (0x5, 0x7):
            self.PC += 1

    def get_value(self, operand, addressing_mode):
        if addressing_mode == 0:
            return self.registers[operand]
        elif addressing_mode == 1:
            address = self.registers[operand]
            return self.memory[address]
        elif addressing_mode == 2:
            return operand
        else:
            raise ValueError("Неизвестный режим адресации")

    def set_value(self, dst, addressing_mode, value):
        if addressing_mode == 0:
            self.registers[dst] = value
        elif addressing_mode == 1:
            address = self.registers[dst]
            self.memory[address] = value
        else:
            raise ValueError("Неподдерживаемая операция записи для режима адресации")

# emulator = MSP430Emulator()
# program = [17668, 18949, 21509]
# # program = [17668, 18949, 21509, 17670, 39942, 8199, 12296, 16646, 17155]
# emulator.load_program(program)
# emulator.run()
