from random import randrange, randint
from abc import ABCMeta, abstractmethod

from .variant import Variant
from .model import Model


class InvalidImmediateException(Exception):
    pass

class Immediate(object):
    def __init__(self, *, bits: int, signed: bool = False, lsb0: bool = False):
        self.bits = bits
        self.signed = signed
        self.lsb0 = lsb0
        self.value = 0
        self.tcmask = 1 << (self.bits - 1)

    def max(self):
        if self.signed:
            return (1 << (self.bits - 1)) - 1
        else:
            return (1 << self.bits) - 1

    def min(self):
        if self.signed:
            return -(1 << (self.bits - 1))
        else:
            return 0

    def exception(self, msg):
        message = "Immediate(bits={}, signed={}, lsb0={}) {}".format(self.bits, self.signed, self.lsb0, msg)
        return InvalidImmediateException(message)

    def set(self, value: int):
        if not isinstance(value, int):
            raise self.exception("{} is not an integer".format(value))
        if self.lsb0 and self.value % 2 == 1:
            raise self.exception("{} not power of two".format(value))
        if not self.signed and value < 0:
            raise self.exception("{} cannot be negative".format(value))
        if value < self.min() or value > self.max():
            raise self.exception("{} not in allowed range {}-{}".format(value, self.min(), self.max()))

        self.value = value

    def set_from_bits(self, value: int):
        if self.signed:
            value = -(value & self.tcmask) + (value & ~self.tcmask)
        self.set(value)

    def randomize(self):
        self.value = randint(self.min(), self.max())
        if self.lsb0:
            self.value = self.value - (self.value % 2)

    def __int__(self):
        return self.value.__int__()

    def __str__(self):
        return self.value.__str__()

    def __format__(self, format_spec):
        return self.value.__format__(format_spec)


class Instruction(metaclass=ABCMeta):
    """
    Base class for instructions

    This is the abstract base class for all instruction. They are derived via their instruction type.
    """

    @abstractmethod
    def randomize(self, variant: Variant):
        """
        Randomize this instruction

        This function randomizes the instance of an instruction according to the given variant.

        :param variant: RISC-V ISA variant
        :return: nothing
        """
        pass

    @abstractmethod
    def execute(self, model: Model):
        """
        Execute this instruction

        Execute the instruction on the given model

        :param model: RISC-V core model
        :return: nothing
        """
        pass

    @abstractmethod
    def __str__(self):
        """
        Generate assembler code

        Generate the assembler code for this instruction

        :return: Assembly string
        """
        pass

    def __setattr__(self, key, value):
        if key in self.__dict__ and isinstance(self.__dict__[key], Immediate):
            raise AttributeError("Instruction does not allow to overwrite immediates, use set() on them")
        super().__setattr__(key, value)

class InstructionRType(Instruction):
    """
    R-Type instructions

    Those are 3-register instructions which use two source registers and write one output register.
    """
    def __init__(self, rd: int = None, rs1: int = None, rs2: int = None):
        super(InstructionRType, self).__init__()
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2

    def randomize(self, variant: Variant):
        self.rd = randrange(0, variant.intregs)
        self.rs1 = randrange(0, variant.intregs)
        self.rs2 = randrange(0, variant.intregs)

    def decode(self, machinecode: int):
        self.rd = (machinecode >> 7) & 0x1f
        self.rs1 = (machinecode >> 15) & 0x1f
        self.rs2 = (machinecode >> 20) & 0x1f

    def __str__(self):
        return "{} x{}, x{}, x{}".format(self._mnemonic, self.rd, self.rs1, self.rs2)


class InstructionIType(Instruction):
    def __init__(self, rd: int = None, rs1: int = None, imm: int = None):
        super(InstructionIType, self).__init__()
        self.rd = rd
        self.rs1 = rs1
        self.imm = Immediate(bits=12, signed=True)
        if imm is not None:
            self.imm.set(imm)

    def randomize(self, variant: Variant):
        self.rd = randrange(0, variant.intregs)
        self.rs1 = randrange(0, variant.intregs)
        self.imm.randomize()

    def decode(self, machinecode: int):
        self.rd = (machinecode >> 7) & 0x1f
        self.rs1 = (machinecode >> 15) & 0x1f
        self.imm.set_from_bits((machinecode >> 20) & 0xfff)

    def __str__(self):
        return "{} x{}, x{}, {}".format(self._mnemonic, self.rd, self.rs1, self.imm)

class InstructionILType(InstructionIType):
    def __str__(self):
        return "{} x{}, {}(x{})".format(self._mnemonic, self.rd, self.imm, self.rs1)

class InstructionISType(InstructionIType):
    def __init__(self, rd: int = None, rs1: int = None, shamt: int = None):
        super(InstructionISType, self).__init__()
        self.rd = rd
        self.rs1 = rs1
        self.shamt = shamt

    def decode(self, machinecode: int):
        self.rd = (machinecode >> 7) & 0x1f
        self.rs1 = (machinecode >> 15) & 0x1f
        self.shamt = (machinecode >> 20) & 0x1f

    def randomize(self, variant: Variant):
        self.rd = randrange(0, variant.intregs)
        self.rs1 = randrange(0, variant.intregs)
        self.shamt = randrange(0, 1 << 5)

    def __str__(self):
        return "{} x{}, x{}, 0x{:02x}".format(self._mnemonic, self.rd, self.rs1, self.shamt)


class InstructionSType(Instruction):
    def __init__(self, rs1: int = None, rs2: int = None, imm: int = None):
        super(InstructionSType, self).__init__()
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = Immediate(bits=12, signed=True)
        if imm is not None:
            self.imm.set(imm)

    def randomize(self, variant: Variant):
        self.rs1 = randrange(0, variant.intregs)
        self.rs2 = randrange(0, variant.intregs)
        self.imm.randomize()

    def decode(self, machinecode: int):
        self.rs1 = (machinecode >> 15) & 0x1f
        self.rs2 = (machinecode >> 20) & 0x1f
        imm5 = (machinecode >> 7) & 0x1f
        imm7 = (machinecode >> 25) & 0x7f
        self.imm.set_from_bits((imm7 << 5) | imm5)

    def __str__(self):
        return "{} x{}, {}(x{})".format(self._mnemonic, self.rs2, self.imm, self.rs1)


class InstructionBType(Instruction):
    def __init__(self, rs1: int = None, rs2: int = None, imm: int = None):
        super(InstructionBType, self).__init__()
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = Immediate(bits=13, signed=True, lsb0=True)
        if imm is not None:
            self.imm.set(imm)

    def randomize(self, variant: Variant):
        self.rs1 = randrange(0, variant.intregs)
        self.rs2 = randrange(0, variant.intregs)
        self.imm.randomize()

    def decode(self, machinecode: int):
        self.rs1 = (machinecode >> 15) & 0x1f
        self.rs2 = (machinecode >> 20) & 0x1f
        imm11 = (machinecode >> 7) & 0x1
        imm1to4 = (machinecode >> 8) & 0xf
        imm5to10 = (machinecode >> 25) & 0x3f
        imm12 = (machinecode >> 31) & 0x1
        self.imm.set_from_bits((imm12 << 12) | (imm11 << 11) | (imm5to10 << 5) | (imm1to4 << 1))

    def __str__(self):
        return "{} x{}, x{}, .{:+}".format(self._mnemonic, self.rs1, self.rs2, self.imm)


class InstructionUType(Instruction):
    def __init__(self, rd: int = None, imm: int = None):
        super(InstructionUType, self).__init__()
        self.rd = rd
        self.imm = Immediate(bits=20)
        if imm is not None:
            self.imm.set(imm)

    def randomize(self, variant: Variant):
        self.rd = randrange(0, variant.intregs)
        self.imm.randomize()

    def decode(self, machinecode: int):
        self.rd = (machinecode >> 7) & 0x1f
        self.imm.set_from_bits((machinecode >> 12) & 0xfffff)

    def __str__(self):
        return "{} x{}, {}".format(self._mnemonic, self.rd, self.imm)


class InstructionJType(Instruction):
    def __init__(self, rd: int = None, imm: int = None):
        super(InstructionJType, self).__init__()
        self.rd = rd
        self.imm = Immediate(bits=21,signed=True,lsb0=True)
        if imm is not None:
            self.imm.set(imm)

    def randomize(self, variant: Variant):
        self.rd = randrange(0, variant.intregs)
        self.imm.randomize()

    def decode(self, machinecode: int):
        self.rd = (machinecode >> 7) & 0x1f
        imm12to19 = (machinecode >> 12) & 0xff
        imm11 = (machinecode >> 20) & 0x1
        imm1to10 = (machinecode >> 21) & 0x3ff
        imm20 = (machinecode >> 31) & 0x1
        self.imm.set_from_bits((imm20 << 20) | (imm12to19 << 12) | (imm11 << 11) | (imm1to10 << 1))

    def __str__(self):
        return "{} x{}, .{:+}".format(self._mnemonic, self.rd, self.imm)


def isa(mnemonic, opcode, funct3=None, funct7=None):
    def wrapper(wrapped):
        class WrappedClass(wrapped):
            _mnemonic = mnemonic
            _opcode = opcode
            _funct3 = funct3
            _funct7 = funct7

            @staticmethod
            def _match(machinecode: int):
                f3 = (machinecode >> 12) & 0x7
                f7 = (machinecode >> 25) & 0x7f
                if funct3 is not None and f3 != funct3:
                    return False
                if funct7 is not None and f7 != funct7:
                    return False
                return True

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
