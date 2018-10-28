from random import randrange

from riscvmodel.variant import Variant
from riscvmodel.types import Register, RegisterFile, RVFITrace
from riscvmodel.program import Program


# todo: raise exception on memory misalignment
class State(object):
    def __init__(self, variant: Variant):
        self.variant = variant
        self.intreg = RegisterFile(variant.intregs, 32, {0: 0x0})
        self.pc = Register(32)
        self.pc_update = Register(32)
        self.initialized = True
        self.memory = {}
        self.memory_update = None

    def randomize(self):
        self.intreg.randomize()

    def changes(self):
        intregs = self.intreg.changes()
        c = ["x{} = {}".format(r, c[1]) for r, c in intregs.items()]
        if self.pc_update.value != self.pc.value + 4:
            c.append("pc = {}".format(self.pc_update))
        if self.memory_update is not None:
            if self.memory_update[0] == 1:
                data = "{:02x}".format(self.memory_update[2] & 0xFF)
            elif self.memory_update[0] == 2:
                data = "{:04x}".format(self.memory_update[2] & 0xFFFF)
            else:
                data = "{:08x}".format(self.memory_update[2])
            c.append("mem[{}] = {}".format(self.memory_update[1], data))
        if len(c) == 0:
            return "no change"
        else:
            return ", ".join(c)

    def commit(self):
        self.intreg.commit()
        self.pc.set(self.pc_update.value)
        if self.memory_update is not None:
            address = self.memory_update[1]
            base = address >> 2
            offset = address & 0x3
            if base not in self.memory:
                self.memory[base] = randrange(0, 1 << 32)
            data = self.memory_update[2]
            if self.memory_update[0] == 1:
                mask = ~(0xFF << (offset*8)) & 0xFFFFFFFF
                data = (self.memory[base] & mask) | (data << (offset*8))
            elif self.memory_update[0] == 2:
                mask = ~(0xFF << (offset*8)) & 0xFFFFFFFF
                data = (self.memory[base] & mask) | (data << (offset*8))
            self.memory[base] = data
            self.memory_update = None

    def reset(self, pc = 0):
        self.pc.set(pc)

    def lb(self, address):
        word = address >> 2
        offset = address % 4
        if word not in self.memory:
            self.memory[word] = randrange(0, 1 << 32)
        return (self.memory[word] >> (offset*8)) & 0xff

    def lh(self, address):
        word = address >> 2
        offset = (address >> 1) % 2
        if word not in self.memory:
            self.memory[word] = randrange(0, 1 << 32)
        return (self.memory[word] >> (offset*16)) & 0xffff

    def lw(self, address):
        word = address >> 2
        if word not in self.memory:
            self.memory[word] = randrange(0, 1 << 32)
        return self.memory[word]

    def sb(self, address, data):
        self.memory_update = (1, address, int(data) & 0xFF)

    def sh(self, address, data):
        self.memory_update = (2, address, int(data) & 0xFFFF)

    def sw(self, address, data):
        self.memory_update = (4, address, int(data) & 0xFFFFFFFF)

    def __setattr__(self, key, value):
        if key is "pc" and "pc_update" in self.__dict__:
            self.pc_update.set(value)
        else:
            super().__setattr__(key, value)

    def __str__(self):
        return "{}".format(self.intreg)


class Model(object):
    def __init__(self, variant: Variant, *, golden = False, verbose = False):
        self.state = State(variant)
        self.golden = golden
        self.verbose = verbose

    def issue(self, insn):
        self.state.pc += 4
        insn.execute(self.state)
        if self.verbose:
            print("{:20} | {}".format(str(insn), self.state.changes()))
        self.state.commit()

    def execute(self, insn):
        if isinstance(insn, Program):
            insn = insn.insns
        elif not isinstance(insn, list):
            insn = [insn]

        for i in insn:
            self.issue(i)

    def randomize(self):
        self.state.randomize()

    def reset(self, pc: int = 0):
        self.state.reset(pc)
