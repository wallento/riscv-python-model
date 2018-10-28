from random import randrange
from abc import ABCMeta, abstractmethod

from .variant import Variant
from .model import Model
from .types import Immediate


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
    def decode(self, machinecode: int):
        """
        Decode a machine code and configure this instruction from it.

        :param machinecode: Machine code as 32-bit integer
        :type machinecode: int
        """
        pass

    def encode(self) -> int:
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
    R-type instructions are 3-register instructions which use two source registers and write one output register.

    :param rd: Destination register
    :type rd: int
    :param rs1: Source register 1
    :type rs1: int
    :param rs2: Source register 2
    :type rs2: int
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

    def encode(self) -> int:
        x = self._opcode | (self._funct3 << 12) | (self._funct7 << 25)
        x |= (self.rd << 7) | (self.rs1 << 15) | (self.rs2 << 20)
        return x

    def __str__(self):
        return "{} x{}, x{}, x{}".format(self._mnemonic, self.rd, self.rs1, self.rs2)


class InstructionIType(Instruction):
    """
    I-type instructions are registers that use one source register and an immediate to produce a new value for the
    destination register.

    Two specialization exist for this class: :class:`InstructionILType` for load instructions and
    :class:`InstructionISType` for instructions that shift by an immediate value.

    :param rd: Destination register
    :type rd: int
    :param rs1: Source register 1
    :type rs1: int
    :param imm: 12-bit signed immediate
    :type imm: int
    """
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

    def encode(self) -> int:
        x = self._opcode | (self._funct3 << 12)
        x |= (self.rd << 7) | (self.rs1 << 15) | (self.imm.unsigned() << 20)
        return x

    def __str__(self):
        return "{} x{}, x{}, {}".format(self._mnemonic, self.rd, self.rs1, self.imm)


class InstructionILType(InstructionIType):
    """
    I-type instruction specialization for stores. The produce a different assembler than the base class

    :param rd: Destination register
    :type rd: int
    :param rs1: Source register 1
    :type rs1: int
    :param imm: 12-bit signed immediate
    :type rs2: int
    """
    def __str__(self):
        return "{} x{}, {}(x{})".format(self._mnemonic, self.rd, self.imm, self.rs1)

class InstructionISType(InstructionIType):
    """
    I-Type instruction specialization for shifts by immediate. The immediate differs here (5-bit unsigned).

    :param rd: Destination register
    :type rd: int
    :param rs1: Source register 1
    :type rs1: int
    :param imm: 12-bit signed immediate
    :type rs2: int
    """
    def __init__(self, rd: int = None, rs1: int = None, shamt: int = None):
        super(InstructionISType, self).__init__()
        self.rd = rd
        self.rs1 = rs1
        self.shamt = Immediate(bits=5)

    def decode(self, machinecode: int):
        self.rd = (machinecode >> 7) & 0x1f
        self.rs1 = (machinecode >> 15) & 0x1f
        self.shamt.set_from_bits((machinecode >> 20) & 0x1f)

    def encode(self) -> int:
        x = self._opcode | (self._funct3 << 12) | (self._funct7 << 25)
        x |= (self.rd << 7) | (self.rs1 << 15) | (self.shamt.unsigned() << 20)
        return x

    def randomize(self, variant: Variant):
        self.rd = randrange(0, variant.intregs)
        self.rs1 = randrange(0, variant.intregs)
        self.shamt.randomize()

    def __str__(self):
        return "{} x{}, x{}, 0x{:02x}".format(self._mnemonic, self.rd, self.rs1, self.shamt)


class InstructionSType(Instruction):
    """
    S-type instructions are used for stores. They don't have a destination register, but two source registers.

    :param rs1: Source register for base address
    :type rs1: int
    :param rs2: Source register for data
    :type rs2: int
    :param imm: Offset of store, for calculation of address relative to rs1
    :type imm: int
    """
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

    def encode(self) -> int:
        imm5 = self.imm.unsigned() & 0x1f
        imm7 = (self.imm.unsigned() >> 5) & 0x7f
        x = self._opcode | (self._funct3 << 12) | (self.rs1 << 15) | (self.rs2 << 20)
        x |= (imm7 << 25) | (imm5 << 7)
        return x

    def __str__(self):
        return "{} x{}, {}(x{})".format(self._mnemonic, self.rs2, self.imm, self.rs1)


class InstructionBType(Instruction):
    """
    B-type instructions encode branches. Branches have two source registers that are compared. They then change the
    program counter by the immediate value.

    :param rs1: Source 1 for comparison
    :type rs1: int
    :param rs2: Source 2 for comparison
    :type rs2: int
    :param imm: Immediate for branch destination address calculation (13-bit, signed, 16-bit aligned)
    :type imm: int
    """
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

    def encode(self) -> int:
        imm12 = (self.imm.unsigned() >> 12) & 0x1
        imm11 = (self.imm.unsigned() >> 11) & 0x1
        imm1to4 = (self.imm.unsigned() >> 1) & 0xf
        imm5to10 = (self.imm.unsigned() >> 5) & 0x3f
        x = self._opcode | (self._funct3 << 12) | (self.rs1 << 15) | (self.rs2 << 20)
        x |= (imm12 << 31) | (imm5to10 << 25) | (imm1to4 << 8) | (imm11 << 7)
        return x

    def __str__(self):
        return "{} x{}, x{}, .{:+}".format(self._mnemonic, self.rs1, self.rs2, self.imm)


class InstructionUType(Instruction):
    """
    U-type instructions are used for constant formation and set the upper bits of a register.

    :param rd: Destination register
    :type rd: int
    :param imm: Immediate (20-bit, unsigned)
    :type imm: int
    """
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

    def encode(self):
        return self._opcode | (self.rd << 7) | (self.imm.unsigned() << 12)

    def __str__(self):
        return "{} x{}, {}".format(self._mnemonic, self.rd, self.imm)


class InstructionJType(Instruction):
    """
    J-type instruction are used for jump and link instructions.

    :param rd: Destination register
    :type rd: int
    :param imm: Immediate for the jump (21-bit, signed, 16-bit aligned)
    :type imm: int
    """
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

    def encode(self):
        imm20 = (self.imm.unsigned() >> 20) & 0x1
        imm12to19 = (self.imm.unsigned() >> 12) & 0xff
        imm11 = (self.imm.unsigned() >> 11) & 0x1
        imm1to10 = (self.imm.unsigned() >> 1) & 0x3ff
        x = self._opcode | (self.rd << 7)
        x |= (imm20 << 31) | (imm1to10 << 21) | (imm11 << 20) | (imm12to19 << 12)
        return x

    def __str__(self):
        return "{} x{}, .{:+}".format(self._mnemonic, self.rd, self.imm)


def isa(mnemonic: str, opcode: int, funct3: int=None, funct7: int=None):
    """
    Decorator for the instructions. The decorator contains the static information for the instructions, in particular
    the encoding parameters and the assembler mnemonic.

    :param mnemonic: Assembler mnemonic
    :param opcode: Opcode of this instruction
    :param funct3: 3 bit function code on bits 14 to 12 (R-, I-, S- and B-type)
    :param funct7: 7 bit function code on bits 31 to 25 (R-type)
    :return: Wrapper class that overwrites the actual definition and contains static data
    """
    def wrapper(wrapped):
        """Get wrapper"""
        class WrappedClass(wrapped):
            """Generic wrapper class"""
            _mnemonic = mnemonic
            _opcode = opcode
            _funct3 = funct3
            _funct7 = funct7

            @staticmethod
            def _match(machinecode: int):
                """Try to match a machine code to this instruction"""
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
    """
    Get all Instructions. This is based on all known subclasses of `cls`. If non is given, all Instructions are returned.
    Only such instructions are returned that can be generated, i.e., that have a mnemonic, opcode, etc. So other
    classes in the hierarchy are not matched.

    :param cls: Base class to get list
    :type cls: Instruction
    :return: List of instructions
    """
    insns = []

    if cls is None:
        cls = Instruction

    if "_mnemonic" in cls.__dict__.keys():
        insns = [cls]

    for subcls in cls.__subclasses__():
        insns += get_insns(subcls)

    return insns


def reverse_lookup(mnemonic: str):
    """
    Find instruction that matches the mnemonic.

    :param mnemonic: Mnemonic to match
    :return: :class:`Instruction` that matches or None
    """
    for i in get_insns():
        if "_mnemonic" in i.__dict__ and i._mnemonic == mnemonic:
            return i

    return None


def get_mnenomics():
    """
    Get all known mnemonics

    :return: List of all known mnemonics
    :rtype: List[str]
    """
    return [i._mnemonic for i in get_insns()]
