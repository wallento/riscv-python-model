from enum import Enum
from random import randrange
from abc import ABCMeta, abstractmethod

from .variant import Variant
from .model import Model


class InstructionType(Enum):
    INVALID = 0
    R = 1
    I = 2
    S = 3
    B = 4
    U = 5
    J = 6


class Instruction(metaclass=ABCMeta):
    def __init__(self, mnemonic):
        self.type = InstructionType.INVALID
        self.mnemonic = mnemonic

    @abstractmethod
    def randomize(self, variant: Variant):
        pass

    @abstractmethod
    def execute(self, model: Model):
        pass


class InstructionRType(Instruction):
    def __init__(self, mnemonic, funct3, funct7):
        super(InstructionRType, self).__init__(mnemonic)
        self.rd = None
        self.rs1 = None
        self.rs2 = None
        self.funct3 = funct3
        self.funct7 = funct7

    def randomize(self, variant: Variant):
        self.rd = randrange(0, variant.intregs)
        self.rs1 = randrange(0, variant.intregs)
        self.rs2 = randrange(0, variant.intregs)

    def __str__(self):
        return "{} x{}, x{}, x{}".format(self.mnemonic, self.rd, self.rs1, self.rs2)


class InstructionIType(Instruction):
    def __init__(self, mnemonic, funct3):
        super(InstructionIType, self).__init__(mnemonic)
        self.rd = None
        self.rs1 = None
        self.imm = None
        self.funct3 = funct3

    def randomize(self, variant: Variant):
        self.rd = randrange(0, variant.intregs)
        self.rs1 = randrange(0, variant.intregs)
        self.imm = randrange(0, 1 << 12)

    def __str__(self):
        sign = (self.imm >> 11) & 1 == 1
        imm = self.imm & 0x7FF
        if sign:
            return "{} x{}, x{}, -0x{:03x}".format(self.mnemonic, self.rd, self.rs1, imm)
        else:
            return "{} x{}, x{}, 0x{:03x}".format(self.mnemonic, self.rd, self.rs1, imm)

class InstructionILType(Instruction):
    def __init__(self, mnemonic, funct3):
        super(InstructionILType, self).__init__(mnemonic)
        self.rd = None
        self.rs1 = None
        self.imm = None
        self.funct3 = funct3

    def randomize(self, variant: Variant):
        self.rd = randrange(0, variant.intregs)
        self.rs1 = randrange(0, variant.intregs)
        self.imm = randrange(0, 1 << 12)

    def __str__(self):
        sign = (self.imm >> 11) & 1 == 1
        imm = self.imm & 0x7FF
        if sign:
            return "{} x{}, -0x{:03x}(x{})".format(self.mnemonic, self.rd, imm, self.rs1)
        else:
            return "{} x{}, 0x{:03x}(x{})".format(self.mnemonic, self.rd, imm, self.rs1)

class InstructionISType(Instruction):
    def __init__(self, mnemonic, funct3, funct7):
        super(InstructionISType, self).__init__(mnemonic)
        self.rd = None
        self.rs1 = None
        self.shamt = None
        self.funct3 = funct3
        self.funct7 = funct7

    def randomize(self, variant: Variant):
        self.rd = randrange(0, variant.intregs)
        self.rs1 = randrange(0, variant.intregs)
        self.shamt = randrange(0, 1 << 5)

    def __str__(self):
        return "{} x{}, x{}, 0x{:02x}".format(self.mnemonic, self.rd, self.rs1, self.shamt)


class InstructionSType(Instruction):
    def __init__(self, mnemonic, funct3):
        super(InstructionSType, self).__init__(mnemonic)
        self.rs1 = None
        self.rs2 = None
        self.imm = None
        self.funct3 = funct3

    def randomize(self, variant: Variant):
        self.rs1 = randrange(0, variant.intregs)
        self.rs2 = randrange(0, variant.intregs)
        self.imm = randrange(0, 1 << 12)

    def __str__(self):
        sign = (self.imm >> 11) & 1 == 1
        imm = self.imm & 0x7ff
        if sign:
            return "{} x{}, -0x{:03x}(x{})".format(self.mnemonic, self.rs1, imm, self.rs2)
        else:
            return "{} x{}, 0x{:03x}(x{})".format(self.mnemonic, self.rs1, imm, self.rs2)

class InstructionBType(Instruction):
    def __init__(self, mnemonic, funct3):
        super(InstructionBType, self).__init__(mnemonic)
        self.rs1 = None
        self.rs2 = None
        self.imm = None
        self.funct3 = funct3

    def randomize(self, variant: Variant):
        self.rs1 = randrange(0, variant.intregs)
        self.rs2 = randrange(0, variant.intregs)
        self.imm = randrange(0, 1 << 12)

    def __str__(self):
        return "{} x{}, x{}, 0x{:05x}".format(self.mnemonic, self.rs1, self.rs2, self.imm)

class InstructionUType(Instruction):
    def __init__(self, mnemonic):
        super(InstructionUType, self).__init__(mnemonic)
        self.rd = None
        self.imm = None

    def randomize(self, variant: Variant):
        self.rd = randrange(0, variant.intregs)
        self.imm = randrange(0, 1 << 20)

    def __str__(self):
        return "{} x{}, 0x{:05x}".format(self.mnemonic, self.rd, self.imm)


class InstructionJType(Instruction):
    def __init__(self, mnenomic):
        super(InstructionJType, self).__init__(mnenomic)
        self.rd = None
        self.imm = None

    def randomize(self, variant: Variant):
        self.rd = randrange(0, variant.intregs)
        self.imm = randrange(0, 1 << 20)

    def __str__(self):
        return "{} x{}, 0x{:05x}".format(self.mnemonic, self.rd, self.imm)

def isa(mnemonic, funct3=None, funct7=None):
    def wrapper(wrapped):
        class WrappedClass(wrapped):
            _mnemonic = mnemonic
            def __init__(self):
                if funct3 is not None:
                    if funct7 is not None:
                        super(wrapped, self).__init__(mnemonic, funct3, funct7)
                    else:
                        super(wrapped, self).__init__(mnemonic, funct3)
                else:
                    super(wrapped, self).__init__(mnemonic)
        WrappedClass.__name__ = wrapped.__name__
        WrappedClass.__module__ = wrapped.__module__
        WrappedClass.__qualname__ = wrapped.__qualname__
        return WrappedClass
    return wrapper

def get_insns(cls):
    insns = []

    if "_mnemonic" in cls.__dict__.keys():
        insns = [cls]

    for subcls in cls.__subclasses__():
        insns += get_insns(subcls)

    return insns


def reverse_lookup_class(mnemonic: str, cls):
    if "_mnemonic" in cls.__dict__:
        if cls._mnemonic == mnemonic:
            return cls

    for sub in cls.__subclasses__():
        s = reverse_lookup_class(mnemonic, sub)
        if s is not None:
            return s

    return None

def reverse_lookup(mnemonic: str):
    return reverse_lookup_class(mnemonic, Instruction)


def get_mnenomics_class(cls):
    m = []
    if "_mnemonic" in cls.__dict__:
        m = [cls._mnemonic]
    for sub in cls.__subclasses__():
        m += get_mnenomics_class(sub)
    return m


def get_mnenomics():
    return get_mnenomics_class(Instruction)