"""CPU functionality."""

import sys
HLT = 0x01   
LDI = 0x82   
PRN = 0x47   
MUL = 0xA2   
ADD = 0xA0   
POP = 0x46   
PUSH = 0x45   
CALL = 0x50  
RET = 0x11   
CMP = 0xA7    
JMP = 0x54   
JEQ = 0x55   
JNE = 0x56   
AND = 0xA8   
OR = 0x69    
XOR = 0xAB   
NOT = 0x69   
SHL = 0xAC   
SHR = 0xAD   
MOD = 0xA4   
PRA = 0b01001000


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 0x100
        self.reg = [0] * 0x08
        self.pc = 0
        self.mar = 0
        self.mdr = 0
        self.fl = 0x00
        self.sp = 0xF4
        self.branchtable = {
            HLT: self.hlt,
            LDI: self.ldi,
            PRN: self.prn,
            POP: self.pop,
            PUSH: self.push,
            CALL: self.call,
            RET: self.ret,
            CMP: self.cmp,
            JMP: self.jmp,
            JEQ: self.jeq,
            JNE: self.jne,
            PRA: self.pra,
            'ALU': {
                ADD: self.alu,
                MUL: self.alu,
                AND: self.alu,
                OR: self.alu,
                XOR: self.alu,
                NOT: self.alu,
                SHL: self.alu,
                SHR: self.alu,
                MOD: self.alu
            }
        }

    def load(self, path):
        """Load a program into memory."""

        address = 0

        f = open(path)
        program = f.read().splitlines()
        f.close()

        for index, line in enumerate(program):
            comment = line.find('#')
            if comment != -1:
                line = line[:comment]
            if line != '':
                line = int(line.strip(), 2)
            program[index] = line

        while '' in program:
            program.remove('')

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def hlt(self, *args):
        exit()

    def ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b

    def prn(self, operand_a, *args):
        print(self.reg[operand_a])

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == AND:
            self.reg[reg_a] = (self.reg[reg_a] & self.reg[reg_b])
        elif op == OR:
            self.reg[reg_a] = (self.reg[reg_a] | self.reg[reg_b])
        elif op == XOR:
            self.reg[reg_a] = (self.reg[reg_a] ^ self.reg[reg_b])
        elif op == NOT:
            self.reg[reg_a] = (~ self.reg[reg_a])
        elif op == SHL:
            self.reg[reg_a] = (self.reg[reg_a] << self.reg[reg_b])
        elif op == SHR:
            self.reg[reg_a] = (self.reg[reg_a] >> self.reg[reg_b])
        elif op == MOD:
            self.reg[reg_a] = (self.reg[reg_a] % self.reg[reg_b])
        else:
            raise Exception("Unsupported ALU operation")

    def pop(self, operand_a, *args):
        """
        Copy val from sp to given register
        Increments sp
        """
        val = self.ram_read(self.sp)
        self.reg[operand_a] = val
        self.sp += 1

    def pra(self, *args):
        op_a = self.ram_read(self.pc + 1)
        print_ascii = chr(self.reg[op_a])
        print(print_ascii)

    def push(self, operand_a, *args):
        """
        Decrements sp
        Copy value in given register to sp
        """
        self.sp -= 1
        self.ram_write(self.sp, self.reg[operand_a])

    def call(self, operand_a, *args):
        """
        The address of the instruction directly after CALL is 
        pushed onto the stack. This allows us to return to where 
        we left off when the subroutine finishes executing.
        The PC is set to the address stored in the given register. 
        We jump to that location in RAM and execute the first 
        instruction in the subroutine. The PC can move forward or 
        backwards from its current location.
        """
        self.sp -= 1
        self.ram_write(self.sp, self.pc)
        self.push(operand_a)
        self.pc = self.mdr - 2

    def ret(self, *args):
        """
        Pop the value from the top of the stack and store it in the PC
        """
        self.pop(self.mdr)
        self.pc = self.ram[self.sp] + 1

    def cmp(self, a, b):
        if self.reg[a] == self.reg[b]:
            self.fl = 0x01
        elif self.reg[a] > self.reg[b]:
            self.fl = 0x02
        else:
            self.fl = 0x03

    def jmp(self, a, *args):
        self.pc = self.reg[a] - 2

    def jeq(self, a, *args):
        if f'{self.fl:x}' == f'{0x01}':
            self.pc = self.reg[a] - 2

    def jne(self, a, *args):
        if f'{self.fl:x}' != f'{0x01}':
            self.pc = self.reg[a] - 2

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

         while True:
            op = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if op in self.branch_table:
                self.branch_table[op](operand_a, operand_b)
            else:
                print("Unrecognized operation.")
                sys.exit(1)

    def ram_read(self, address):
        self.mar = address
        self.mdr = self.ram[address]
        return self.mdr

    def ram_write(self, address, value):
        self.mar = address
        self.mdr = value
        self.ram[self.mar] = self.mdr