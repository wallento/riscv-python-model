from enum import Enum
from random import randrange
from abc import ABCMeta, abstractmethod

from .variant import Variant
from .model import Model


class Instruction(metaclass=ABCMeta):

    @abstractmethod
    def randomize(self, variant: Variant):
        pass

    @abstractmethod
    def execute(self, model: Model):
        pass

    @abstractmethod
    def __str__(self):
        pass

class InstructionRType(Instruction):
    def __init__(self):
        super(InstructionRType, self).__init__()
        self.rd = None
        self.rs1 = None
        self.rs2 = None

    def randomize(self, variant: Variant):
        self.rd = randrange(0, variant.intregs)
        self.rs1 = randrange(0, variant.intregs)
        self.rs2 = randrange(0, variant.intregs)

    def __str__(self):
        return "{} x{}, x{}, x{}".format(self._mnemonic, self.rd, self.rs1, self.rs2)


class InstructionIType(Instruction):
    def __init__(self):
        super(InstructionIType, self).__init__()
        self.rd = None
        self.rs1 = None
        self.imm = None

    def randomize(self, variant: Variant):
        self.rd = randrange(0, variant.intregs)
        self.rs1 = randrange(0, variant.intregs)
        self.imm = randrange(0, 1 << 12)

    def __str__(self):
        sign = (self.imm >> 11) & 1 == 1
        imm = self.imm & 0x7FF
        if sign:
            return "{} x{}, x{}, -0x{:03x}".format(self._mnemonic, self.rd, self.rs1, imm)
        else:
            return "{} x{}, x{}, 0x{:03x}".format(self._mnemonic, self.rd, self.rs1, imm)

class InstructionILType(Instruction):
    def __init__(self):
        super(InstructionILType, self).__init__()
        self.rd = None
        self.rs1 = None
        self.imm = None

    def randomize(self, variant: Variant):
        self.rd = randrange(0, variant.intregs)
        self.rs1 = randrange(0, variant.intregs)
        self.imm = randrange(0, 1 << 12)

    def __str__(self):
        sign = (self.imm >> 11) & 1 == 1
        imm = self.imm & 0x7FF
        if sign:
            return "{} x{}, -0x{:03x}(x{})".format(self._mnemonic, self.rd, imm, self.rs1)
        else:
            return "{} x{}, 0x{:03x}(x{})".format(self._mnemonic, self.rd, imm, self.rs1)

class InstructionISType(Instruction):
    def __init__(self):
        super(InstructionISType, self).__init__()
        self.rd = None
        self.rs1 = None
        self.shamt = None

    def randomize(self, variant: Variant):
        self.rd = randrange(0, variant.intregs)
        self.rs1 = randrange(0, variant.intregs)
        self.shamt = randrange(0, 1 << 5)

    def __str__(self):
        return "{} x{}, x{}, 0x{:02x}".format(self._mnemonic, self.rd, self.rs1, self.shamt)


class InstructionSType(Instruction):
    def __init__(self):
        super(InstructionSType, self).__init__()
        self.rs1 = None
        self.rs2 = None
        self.imm = None

    def randomize(self, variant: Variant):
        self.rs1 = randrange(0, variant.intregs)
        self.rs2 = randrange(0, variant.intregs)
        self.imm = randrange(0, 1 << 12)

    def __str__(self):
        sign = (self.imm >> 11) & 1 == 1
        imm = self.imm & 0x7ff
        if sign:
            return "{} x{}, -0x{:03x}(x{})".format(self._mnemonic, self.rs1, imm, self.rs2)
        else:
            return "{} x{}, 0x{:03x}(x{})".format(self._mnemonic, self.rs1, imm, self.rs2)

class InstructionBType(Instruction):
    def __init__(self):
        super(InstructionBType, self).__init__()
        self.rs1 = None
        self.rs2 = None
        self.imm = None

    def randomize(self, variant: Variant):
        self.rs1 = randrange(0, variant.intregs)
        self.rs2 = randrange(0, variant.intregs)
        self.imm = randrange(0, 1 << 12)

    def __str__(self):
        return "{} x{}, x{}, 0x{:05x}".format(self._mnemonic, self.rs1, self.rs2, self.imm)

class InstructionUType(Instruction):
    def __init__(self):
        super(InstructionUType, self).__init__()
        self.rd = None
        self.imm = None

    def randomize(self, variant: Variant):
        self.rd = randrange(0, variant.intregs)
        self.imm = randrange(0, 1 << 20)

    def __str__(self):
        return "{} x{}, 0x{:05x}".format(self._mnemonic, self.rd, self.imm)


class InstructionJType(Instruction):
    def __init__(self):
        super(InstructionJType, self).__init__()
        self.rd = None
        self.imm = None

    def randomize(self, variant: Variant):
        self.rd = randrange(0, variant.intregs)
        self.imm = randrange(0, 1 << 20)

    def __str__(self):
        return "{} x{}, 0x{:05x}".format(self._mnemonic, self.rd, self.imm)


def isa(mnemonic, opcode, funct3=None, funct7=None):
    def wrapper(wrapped):
        class WrappedClass(wrapped):
            _mnemonic = mnemonic
            _opcode = opcode
            _funct3 = funct3
            _funct7 = funct7
        WrappedClass.__name__ = wrapped.__name__
        WrappedClass.__module__ = wrapped.__module__
        WrappedClass.__qualname__ = wrapped.__qualname__
        return WrappedClass
    return wrapper


def get_insns(cls = None):
    insns = []

    if cls is None:
        cls = Instruction

    if "_mnemonic" in cls.__dict__.keys():
        insns = [cls]

    for subcls in cls.__subclasses__():
        insns += get_insns(subcls)

    return insns


def reverse_lookup(mnemonic: str):
    for i in get_insns():
        if "_mnemonic" in i.__dict__ and i._mnemonic == mnemonic:
            return i

    return None


def get_mnenomics():
    return [i._mnemonic for i in get_insns()]
