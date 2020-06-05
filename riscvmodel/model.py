from random import randrange

from .variant import *
from .types import Register, RegisterFile, TracePC, TraceIntegerRegister, TraceMemory
from .program import Program

# todo: raise exception on memory misalignment
class State(object):
    def __init__(self, variant: Variant):
        self.variant = variant
        self.intreg = RegisterFile(variant.intregs, 32, {0: 0x0})
        self.pc = Register(32)
        self.pc_update = Register(32)
        self.memory = Memory()
        self.initialized = True

    def randomize(self):
        self.intreg.randomize()

    def changes(self):
        c = self.intreg.changes()
        if self.pc_update.value != self.pc.value + 4:
            c.append(TracePC(self.pc_update.value))
        c += self.memory.changes()
        return c

    def commit(self):
        self.intreg.commit()
        self.pc.set(self.pc_update.value)
        self.memory.commit()

    def reset(self, pc = 0):
        self.pc.set(pc)

    def __setattr__(self, key, value):
        if key is "pc" and "pc_update" in self.__dict__:
            self.pc_update.set(value)
        else:
            super().__setattr__(key, value)

    def __str__(self):
        return "{}".format(self.intreg)


class Memory(object):
    def __init__(self, *, base: int = 0, size: int = 2^32):
        self.base = base
        self.size = size
        self.memory = {}
        self.memory_updates = []

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
        self.memory_updates.append(TraceMemory(TraceMemory.GRANULARITY.BYTE, address, int(data) & 0xFF))

    def sh(self, address, data):
        self.memory_updates.append(TraceMemory(TraceMemory.GRANULARITY.HALFWORD, address, int(data) & 0xFFFF))

    def sw(self, address, data):
        self.memory_updates.append(TraceMemory(TraceMemory.GRANULARITY.WORD, address, int(data) & 0xFFFFFFFF))

    def changes(self):
        return self.memory_updates

    def commit(self):
        for update in self.memory_updates:
            address = update.addr
            base = address >> 2
            offset = address & 0x3
            if base not in self.memory:
                self.memory[base] = randrange(0, 1 << 32)
            data = update.data
            if update.gran == TraceMemory.GRANULARITY.BYTE:
                mask = ~(0xFF << (offset*8)) & 0xFFFFFFFF
                data = (self.memory[base] & mask) | (data << (offset*8))
            self.memory[base] = data

        self.memory_updates = []


class Model(object):
    def __init__(self, variant: Variant, *, verbose = False):
        self.state = State(variant)
        self.verbose = verbose

    def issue(self, insn):
        self.state.pc += 4
        expected_pc = self.state.pc
        insn.execute(self.state)
        trace = self.state.changes()
        if self.verbose:
            print("{:20} | {}".format(str(insn), trace))
        self.state.commit()
        return trace

    def execute(self, insn):
        if isinstance(insn, Program):
            insn = insn.insns
        elif not isinstance(insn, list):
            insn = [insn]

        for i in insn:
            self.issue(i)

    def randomize(self):
        self.state.randomize()

    def reset(self, *, pc: int = 0):
        self.state.reset(pc)

    def check(self, traces, exp=None):
        for t in traces:
            if isinstance(t, TraceIntegerRegister):
                if int(self.state.intreg[t.id]) != int(t.value):
                    return False
        return True
