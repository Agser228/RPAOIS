import re


class Assembler:
    def __init__(self, offset):
        self.opcode_map = {
            'MOV': 0x1,
            'CMP': 0x2,
            'ADD': 0x3,
            'DEC': 0x4,
            'JLO': 0x5,
            'JNZ': 0x6,
            'JMP': 0x7,
            'NOP': 0xF
        }
        self.labels = {}
        self.offset = offset

    def assemble(self, asm_code):
        machine_codes = []
        self.labels = {}
        lines = asm_code.splitlines()
        command = 0

        for line in lines:
            line = line.strip()
            if line.endswith(':'):
                label = line[:-1]
                self.labels[label] = command + len(self.labels)
                continue
            command += 1

        command = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.endswith(':'):
                machine_codes.append(0)
                command += 1
                continue

            parts = re.split(r'\s+', line, maxsplit=1)
            instruction = parts[0].upper()
            operands = parts[1] if len(parts) > 1 else None

            if instruction in self.opcode_map:
                opcode = self.opcode_map[instruction] << 12
                if operands:
                    operand_parts = operands.split(',')
                    src = operand_parts[0].strip()
                    s_field = self.process_src(src)
                    if len(operand_parts) > 1:
                        dst = operand_parts[1].strip()
                        d_field = self.process_dest(dst)
                        opcode |= d_field
                    opcode |= s_field << 6
                machine_codes.append(opcode)
            else:
                raise ValueError(f"Неизвестная команда ассмеблера {instruction}")

        return machine_codes

    def process_src(self, operand):
        if operand.startswith('R') and operand[1:].isdigit():
            # Регистровая адресация
            return self.get_register_code(operand)
        elif operand.startswith('@'):
            # Косвенная адресация
            reg = int(operand[1:]) if operand[1:].isdigit() else self.get_register_code(operand[1:])
            return 1 << 4 | reg
        elif operand.startswith('#'):
            # Непосредственное значение
            return 2 << 4 | int(operand[1:])
        elif operand in self.labels:
            # Метка
            return self.labels[operand]
        else:
            raise ValueError(f"Неизвестный операнд: {operand}")

    def process_dest(self, operand):
        if operand.startswith('R') and operand[1:].isdigit():
            # Регистровая адресация
            return self.get_register_code(operand)
        elif operand.startswith('@'):
            # Косвенная адресация
            return 1 << 4 | self.get_register_code(operand[1:])
        elif operand in self.labels:
            # Метка
            return self.labels[operand]
        else:
            raise ValueError(f"Неизвестный операнд: {operand}")

    def get_register_code(self, operand):
        if operand.startswith('R') and operand[1:].isdigit() and int(operand[1:]) < 16:
            return int(operand[1:])
        else:
            raise ValueError(f"Неизвестный регистр: {operand}")

