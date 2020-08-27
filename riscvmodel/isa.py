# Copyright Stefan Wallentowitz
# Licensed under the MIT License, see LICENSE for details.
# SPDX-License-Identifier: MIT
"""
This is the basic ISA definition. It describes the instruction formats and base
classes. Actual instructions are implemented in the insn module.
"""

from random import randrange
from abc import ABCMeta, abstractmethod
from collections import namedtuple

from .variant import Variant
from .model import Model
from .types import Immediate, Register
from .variant import RV32I

Field = namedtuple("Field", ["name", "base", "size", "offset", "description", "static", "value"])
Field.__new__.__defaults__ = (None, None, None, 0, None, False, None)

class Instruction(metaclass=ABCMeta):
    """
    Base class for instructions

    This is the abstract base class for all instruction. They are derived via
    their instruction type.
    """

    # Class members starting with "field_" are defined by the ISA
    field_opcode = Field(name="opcode", base=0, size=7, description="", static=True)

    # Class members starting with "isa_" are defined by the ISA and describe and
    # identify an instruction
    mnemonic = None
    coding = None
    isa_variant = None

    isa_format_id = None

    asm_arg_signature = ""

    @classmethod
    def asm_signature(cls):
        signature = cls.mnemonic
        if len(cls.asm_arg_signature) > 0:
            signature += " " + cls.asm_arg_signature
        return signature

    @classmethod
    def extract_field(cls, field, word):
        fname = "field_{}".format(field)
        base = getattr(cls, fname).base
        size = getattr(cls, fname).size
        if not isinstance(base, list):
            base = [base]
            size = [size]
        off = 0
        value = 0
        for part in range(len(base)):
            value |= ((word >> base[part]) & (2**size[part] - 1)) << off
            off += size[part]
        return value << getattr(cls, fname).offset

    @classmethod
    def set_field(cls, field, word, value):
        fname = "field_{}".format(field)
        base = getattr(cls, fname).base
        size = getattr(cls, fname).size
        if not isinstance(base, list):
            base = [base]
            size = [size]
        off = getattr(cls, fname).offset
        for part in range(len(base)):
            word |= (((value >> off) & (2**size[part] - 1)) << base[part])
            off += size[part]
        return word

    @classmethod
    def get_fields(cls):
        return [getattr(cls, member) for member in dir(cls) if member.startswith("field_")]

    @classmethod
    def get_static_fields(cls):
        return [field for field in cls.get_fields() if field.static]

    @classmethod
    def get_isa_format(cls, *, asdict: bool=False):
        fields = [getattr(cls, attr) for attr in dir(cls) if attr.startswith("field_")]
        if asdict:
            fields = [field._asdict() for field in fields]
        return {"id": cls.isa_format_id, "fields": fields}

    @classmethod
    def match(cls, word: int):
        """Try to match a machine code to this instruction"""
        for field in cls.get_static_fields():
            if cls.extract_field(field.name, word) != field.value:
                return False
        return True

    def ops_from_string(self, ops: str):
        """
        Extract operands from string
        """
        self.ops_from_list(ops.split(","))

    def ops_from_list(self, ops: list):
        """
        Extract operands from list of string
        """

    def randomize(self, variant: Variant):
        """
        Randomize this instruction

        This function randomizes the instance of an instruction according to the
        given variant.

        :param variant: RISC-V ISA variant :return: nothing
        """

    @abstractmethod
    def execute(self, model: Model):
        """
        Execute this instruction

        Execute the instruction on the given model

        :param model: RISC-V core model
        :return: nothing
        """

    def decode(self, word: int):
        """
        Decode a machine code and configure this instruction from it.

        :param word: Machine code as 32-bit integer
        :type word: int
        """
        for field in self.get_fields():
            if field.static:
                assert self.extract_field(field.name, word) == field.value
            else:
                attr = getattr(self, field.name)
                value = self.extract_field(field.name, word)
                if isinstance(attr, Register):
                    attr.set(value)
                elif isinstance(attr, Immediate):
                    attr.set_from_bits(value)
                else:
                    setattr(self, field.name, value)

    def encode(self) -> int:
        """
        TODO: document
        """
        word = 0
        for field in self.get_fields():
            if field.value is not None:
                word = self.set_field(field.name, word, field.value)
            else:
                value = getattr(self, field.name)
                if isinstance(value, Immediate):
                    word = self.set_field(field.name, word, value.unsigned())
                elif isinstance(value, bool):
                    word = self.set_field(field.name, word, 1 if value else 0)
                else:
                    word = self.set_field(field.name, word, value)
        return word

    def __str__(self):
        """
        Generate assembler code

        Generate the assembler code for this instruction

        :return: Assembly string
        """
        return str(self.mnemonic)

    # pylint: disable=R0201,W0613
    def inopstr(self, model) -> str:
        """
        TODO: document
        """
        return ""

    # pylint: disable=R0201,W0613
    def outopstr(self, model) -> str:
        """
        TODO: document
        """
        return ""

    def __setattr__(self, key, value):
        if key in self.__dict__ and isinstance(self.__dict__[key], Immediate):
            raise AttributeError(
                "Instruction does not allow to overwrite immediates, use set() on them"
            )
        super().__setattr__(key, value)

    def __eq__(self, other):
        for field in self.get_fields():
            if field.static:
                if getattr(self, field) != getattr(other, field):
                    return False
            else:
                if getattr(self, field[6:]) != getattr(other, field[6:]):
                    return False
        return True

class InstructionFunct3Type(Instruction, metaclass=ABCMeta):
    field_funct3 = Field(name="funct3", base=12, size=3, description="", static=True)

class InstructionFunct5Type(Instruction, metaclass=ABCMeta):
    field_funct5 = Field(name="funct5", base=27, size=5, description="", static=True)

class InstructionFunct7Type(Instruction, metaclass=ABCMeta):
    field_funct7 = Field(name="funct7", base=25, size=7, description="", static=True)

class InstructionRType(InstructionFunct3Type, InstructionFunct7Type, metaclass=ABCMeta):
    """
    R-type instructions are 3-register instructions which use two source
    registers and write one output register.

    :param rd: Destination register
    :type rd: int
    :param rs1: Source register 1
    :type rs1: int
    :param rs2: Source register 2
    :type rs2: int
    """

    isa_format_id = "R"
    asm_arg_signature = "<rd>, <rs1>, <rs2>"

    field_rd = Field(name="rd", base=7, size=5, description="")
    field_rs1 = Field(name="rs1", base=15, size=5, description="")
    field_rs2 = Field(name="rs2", base=20, size=5, description="")

    def __init__(self, rd: int = None, rs1: int = None, rs2: int = None):
        super(InstructionRType, self).__init__()
        # pylint: disable=C0103
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2

    def ops_from_list(self, ops):
        (self.rd, self.rs1, self.rs2) = [int(op[1:]) for op in ops]

    def randomize(self, variant: Variant):
        self.rd = randrange(0, variant.xlen)
        self.rs1 = randrange(0, variant.xlen)
        self.rs2 = randrange(0, variant.xlen)

    def inopstr(self, model):
        opstr = "{:>3}={}, ".format("x{}".format(self.rs1),
                                    model.state.intreg[self.rs1])
        opstr += "{:>3}={} ".format("x{}".format(self.rs2),
                                    model.state.intreg[self.rs2])
        return opstr

    def outopstr(self, model):
        return "{:>3}={} ".format("x{}".format(self.rd),
                                  model.state.intreg[self.rd])

    def __str__(self):
        return "{} x{}, x{}, x{}".format(self.mnemonic, self.rd, self.rs1,
                                         self.rs2)


class InstructionIType(InstructionFunct3Type, metaclass=ABCMeta):
    """
    I-type instructions are registers that use one source register and an
    immediate to produce a new value for the destination register.

    Two specialization exist for this class: :class:`InstructionILType` for load
    instructions and :class:`InstructionISType` for instructions that shift by
    an immediate value.

    :param rd: Destination register
    :type rd: int
    :param rs1: Source register 1
    :type rs1: int
    :param imm: 12-bit signed immediate
    :type imm: int
    """

    isa_format_id = "I"
    asm_arg_signature = "<rd>, <rs1>, <imm>"

    field_rd = Field(name="rd", base=7, size=5, description="")
    field_rs1 = Field(name="rs1", base=15, size=5, description="")
    field_imm = Field(name="imm", base=20, size=12, description="")

    def __init__(self, rd: int = None, rs1: int = None, imm: int = None):
        super(InstructionIType, self).__init__()
        self.rd = rd  # pylint: disable=C0103
        self.rs1 = rs1
        self.imm = Immediate(bits=12, signed=True)
        if imm is not None:
            self.imm.set(imm)

    def ops_from_list(self, ops):
        if len(ops) == 0: # ecall
            return
        self.rd = int(ops[0][1:])
        if ops[1][0] == "x":
            self.rs1 = int(ops[1][1:])
            self.imm.set(int(ops[2], 0))
        else: # Load
            self.rs1 = int(ops[2][1:])
            self.imm.set(int(ops[1], 0))

    def randomize(self, variant: Variant):
        self.rd = randrange(0, variant.xlen)
        self.rs1 = randrange(0, variant.xlen)
        self.imm.randomize()

    def inopstr(self, model) -> str:
        return "{:>3}={} ".format("x{}".format(self.rs1),
                                  model.state.intreg[self.rs1])

    def outopstr(self, model) -> str:
        return "{:>3}={} ".format("x{}".format(self.rd),
                                  model.state.intreg[self.rd])

    def __str__(self) -> str:
        return "{} x{}, x{}, {}".format(self.mnemonic, self.rd, self.rs1,
                                        self.imm)

class InstructionILType(InstructionIType, metaclass=ABCMeta):
    """
    I-type instruction specialization for stores. The produce a different
    assembler than the base class

    :param rd: Destination register
    :type rd: int
    :param rs1: Source register 1
    :type rs1: int
    :param imm: 12-bit signed immediate
    :type rs2: int
    """
    def __str__(self):
        return "{} x{}, {}(x{})".format(self.mnemonic, self.rd, self.imm,
                                        self.rs1)


class InstructionISType(InstructionFunct3Type,InstructionFunct7Type, metaclass=ABCMeta):
    """
    Similar to R-Type instruction specialization for shifts by immediate.

    :param rd: Destination register
    :type rd: int
    :param rs1: Source register 1
    :type rs1: int
    :param imm: 12-bit signed immediate
    :type imm: int
    """

    isa_format_id = "IS"

    field_rd = Field(name="rd", base=7, size=5, description="")
    field_rs1 = Field(name="rs1", base=15, size=5, description="")
    field_shamt = Field(name="shamt", base=20, size=5, description="")

    asm_arg_signature = "<rd>, <rs1>, <shamt>"

    def __init__(self, rd: int = None, rs1: int = None, shamt: int = None):
        super(InstructionISType, self).__init__()
        self.rd = rd
        self.rs1 = rs1
        self.shamt = Immediate(bits=5, init=shamt)

    def ops_from_list(self, ops):
        self.rd = int(ops[0][1:])
        self.rs1 = int(ops[1][1:])
        self.shamt.set(int(ops[2], 0))

    def randomize(self, variant: Variant):
        self.rd = randrange(0, variant.xlen)
        self.rs1 = randrange(0, variant.xlen)
        self.shamt.randomize()

    def inopstr(self, model):
        return "{:>3}={} ".format("x{}".format(self.rs1),
                                  model.state.intreg[self.rs1])

    def __str__(self):
        return "{} x{}, x{}, 0x{:02x}".format(self.mnemonic, self.rd, self.rs1,
                                              self.shamt)


class InstructionSType(InstructionFunct3Type, metaclass=ABCMeta):
    """
    S-type instructions are used for stores. They don't have a destination
    register, but two source registers.

    :param rs1: Source register for base address
    :type rs1: int
    :param rs2: Source register for data
    :type rs2: int
    :param imm: Offset of store, for calculation of address relative to rs1
    :type imm: int
    """

    isa_format_id = "S"

    field_rs1 = Field(name="rs1", base=15, size=5, description="")
    field_rs2 = Field(name="rs2", base=20, size=5, description="")
    field_imm = Field(name="imm", base=[7, 25], size=[5, 7], description="")

    asm_arg_signature = "<rs2>, <imm>(<rs1>)"

    def __init__(self, rs1: int = None, rs2: int = None, imm: int = None):
        super(InstructionSType, self).__init__()
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = Immediate(bits=12, signed=True, init=imm)

    def ops_from_list(self, ops):
        self.rs1 = int(ops[2][1:])
        self.rs2 = int(ops[0][1:])
        self.imm.set(int(ops[1], 0))

    def randomize(self, variant: Variant):
        self.rs1 = randrange(0, variant.xlen)
        self.rs2 = randrange(0, variant.xlen)
        self.imm.randomize()

    def inopstr(self, model):
        opstr = "{:>3}={}, ".format("x{}".format(self.rs1),
                                    model.state.intreg[self.rs1])
        opstr += "{:>3}={}".format("x{}".format(self.rs2),
                                   model.state.intreg[self.rs2])
        return opstr

    def __str__(self):
        return "{} x{}, {}(x{})".format(self.mnemonic, self.rs2, self.imm,
                                        self.rs1)

class InstructionBType(InstructionFunct3Type, metaclass=ABCMeta):
    """
    B-type instructions encode branches. Branches have two source registers that
    are compared. They then change the program counter by the immediate value.

    :param rs1: Source 1 for comparison
    :type rs1: int
    :param rs2: Source 2 for comparison
    :type rs2: int
    :param imm: Immediate for branch destination address calculation (13-bit, signed,
           16-bit aligned)
    :type imm: int
    """

    isa_format_id = "B"

    field_rs1 = Field(name="rs1", base=15, size=5, description="")
    field_rs2 = Field(name="rs2", base=20, size=5, description="")
    field_imm = Field(name="imm", base=[7, 25], size=[5, 7], offset=1, description="")

    asm_arg_signature = "<rs1>, <rs2>, <imm>"

    def __init__(self, rs1: int = None, rs2: int = None, imm: int = None):
        super(InstructionBType, self).__init__()
        self.rs1 = rs1
        self.rs2 = rs2
        self.imm = Immediate(bits=13, signed=True, lsb0=True, init=imm)

    def ops_from_list(self, ops):
        self.rs1 = int(ops[0][1:])
        self.rs2 = int(ops[1][1:])
        self.imm.set(int(ops[2], 0))

    def randomize(self, variant: Variant):
        self.rs1 = randrange(0, variant.xlen)
        self.rs2 = randrange(0, variant.xlen)
        self.imm.randomize()

    def inopstr(self, model):
        opstr = "{:>3}={}, ".format("x{}".format(self.rs1),
                                    model.state.intreg[self.rs1])
        opstr += "{:>3}={}".format("x{}".format(self.rs2),
                                   model.state.intreg[self.rs2])
        return opstr

    def __str__(self):
        return "{} x{}, x{}, .{:+}".format(self.mnemonic, self.rs1, self.rs2,
                                           self.imm)

class InstructionUType(Instruction, metaclass=ABCMeta):
    """
    U-type instructions are used for constant formation and set the upper bits of a register.

    :param rd: Destination register
    :type rd: int
    :param imm: Immediate (20-bit, unsigned)
    :type imm: int
    """

    field_rd = Field(name="rd", base=7, size=5, description="")
    field_imm = Field(name="imm", base=12, size=20, description="")

    def __init__(self, rd: int = None, imm: int = None):
        super(InstructionUType, self).__init__()
        self.rd = rd  # pylint: disable=invalid-name
        self.imm = Immediate(bits=20, init=imm)

    def ops_from_list(self, ops):
        self.rd = int(ops[0][1:])
        self.imm.set(int(ops[1], 0))

    def randomize(self, variant: Variant):
        self.rd = randrange(0, variant.xlen)
        self.imm.randomize()

    def outopstr(self, model):
        return "{:>3}={} ".format("x{}".format(self.rd),
                                  model.state.intreg[self.rd])

    def __str__(self):
        return "{} x{}, {}".format(self.mnemonic, self.rd, self.imm)


class InstructionJType(Instruction, metaclass=ABCMeta):
    """
    J-type instruction are used for jump and link instructions.

    :param rd: Destination register
    :type rd: int
    :param imm: Immediate for the jump (21-bit, signed, 16-bit aligned)
    :type imm: int
    """

    field_rd = Field(name="rd", base=7, size=5, description="")
    field_imm = Field(name="imm", base=[21,20,12,31], size=[10,1,8,1], description="", offset=1)

    def __init__(self, rd: int = None, imm: int = None):
        super(InstructionJType, self).__init__()
        self.rd = rd  # pylint: disable=invalid-name
        self.imm = Immediate(bits=21, signed=True, lsb0=True)
        if imm is not None:
            self.imm.set(imm)

    def ops_from_list(self, ops):
        self.rd = int(ops[0][1:])
        self.imm.set(int(ops[1]))

    def randomize(self, variant: Variant):
        self.rd = randrange(0, variant.xlen)
        self.imm.randomize()

    def outopstr(self, model):
        return "{:>3}={} ".format("x{}".format(self.rd),
                                  model.state.intreg[self.rd])

    def __str__(self):
        return "{} x{}, .{:+}".format(self.mnemonic, self.rd, self.imm)


class InstructionCType(Instruction, metaclass=ABCMeta):
    """
    Compact instructions
    """
    @abstractmethod
    def expand(self):
        """
        Expand to full instruction
        """


class InstructionCBType(InstructionCType, metaclass=ABCMeta):
    """
    TODO: document
    """
    def __init__(self, rd: int = None, imm: int = None):
        super(InstructionCBType, self).__init__()
        self.rd = rd  # pylint: disable=invalid-name
        if self.rd is not None:
            self.rd = rd + 8
        self.imm = Immediate(bits=6, signed=True, lsb0=True)
        if imm is not None:
            self.imm.set(imm)

    def decode(self, machinecode: int):
        self.rd = machinecode

    def __str__(self):
        return "{} x{}, {}".format(self.mnemonic, self.rd, self.imm)


class InstructionCRType(InstructionCType, metaclass=ABCMeta):
    """
    TODO: document
    """
    def __init__(self, rd: int = None, rs: int = None):
        super(InstructionCRType, self).__init__()
        self.rd = rd  # pylint: disable=invalid-name
        self.rs = rs  # pylint: disable=invalid-name

    def randomize(self, variant: Variant):
        self.rd = randrange(8, 16)
        self.rs = randrange(8, 16)

    def __str__(self):
        return "{} x{}, x{}".format(self.mnemonic, self.rd, self.rs)


class InstructionCIType(InstructionCType, metaclass=ABCMeta):
    """
    TODO: document
    """
    def __init__(self, rd: int = None, imm: int = None):
        super(InstructionCIType, self).__init__()
        self.rd = rd  # pylint: disable=invalid-name
        self.imm = Immediate(bits=6, signed=True, lsb0=True)
        if imm is not None:
            self.imm.set(imm)

    def randomize(self, variant: Variant):
        self.rd = randrange(0, 16)
        self.imm.randomize()

    def decode(self, machinecode: int):
        self.rd = (machinecode >> 7) & 0x1F
        imm12 = (machinecode >> 12) & 0x1
        imm6to2 = (machinecode >> 2) & 0x1F
        self.imm.set_from_bits((imm12 << 5) | imm6to2)

    def __str__(self):
        return "{} x{}, {}".format(self.mnemonic, self.rd, self.imm)


class InstructionCSSType(InstructionCType, metaclass=ABCMeta):
    """
    TODO: document
    """
    def __init__(self, rs: int = None, imm: int = None):
        super(InstructionCSSType, self).__init__()
        self.rs = rs  # pylint: disable=invalid-name
        self.imm = Immediate(bits=6, signed=True, lsb0=True)
        if imm is not None:
            self.imm.set(imm)

    def __str__(self):
        return "{} x{}, {}(x2)".format(self.mnemonic, self.rs, self.imm)

    def randomize(self, variant: Variant):
        self.rs = randrange(0, 16)
        self.imm.randomize()


class InstructionAMOType(InstructionFunct3Type, InstructionFunct5Type, metaclass=ABCMeta):
    """
    AMO-type instructions used a modified version of the R-type instruction.
    These are also 3-register instructions (use 2 source, write 1 output) but
    have additional flags for controlling acquisition (aq) and release (rl) of
    locks on target addresses.

    :param rd: Destination register
    :type rd: int
    :param rs1: Source register 1
    :type rs1: int
    :param rs2: Source register 2
    :type rs2: int
    :param rl: Lock release flag
    :type rl: int
    :param aq: Lock acquisition flag
    :type aq: int
    """

    isa_format_id     = "R"
    asm_arg_signature = "<rd>, <rs1>, <rs2>, <rl>, <aq>"

    field_rd  = Field(name="rd", base=7, size=5, description="")
    field_rs1 = Field(name="rs1", base=15, size=5, description="")
    field_rs2 = Field(name="rs2", base=20, size=5, description="")
    field_rl  = Field(name="rl",  base=25, size=1, description="Lock release")
    field_aq  = Field(name="aq",  base=26, size=1, description="Lock acquire")

    def __init__(
        self,
        rd: int = None,
        rs1: int = None,
        rs2: int = None,
        rl: int = None,
        aq: int = None,
    ):
        super(InstructionAMOType, self).__init__()
        self.rd  = rd
        self.rs1 = rs1
        self.rs2 = rs2
        self.rl  = rl
        self.aq  = aq

    def ops_from_list(self, ops):
        (self.rd, self.rs1, self.rs2, self.rl, self.aq) = [int(op[1:]) for ops in ops]

    def randomize(self, variant: Variant):
        self.rd  = randrange(0, variant.xlen)
        self.rs1 = randrange(0, variant.xlen)
        self.rs2 = randrange(0, variant.xlen)
        self.rl  = randrange(0, variant.xlen)
        self.aq  = randrange(0, variant.xlen)

    def inopstr(self, model):
        opstr = "{:>3}={}, ".format(
            "x{}".format(self.rs1), model.state.intreg[self.rs1]
        )
        opstr += "{:>3}={} ".format(
            "x{}".format(self.rs2), model.state.intreg[self.rs2]
        )
        return opstr

    def outopstr(self, model):
        return "{:>3}={} ".format(
            "x{}".format(self.rd), model.state.intreg[self.rd]
        )

    def __str__(self):
        return "{} x{}, x{}, x{}, {}, {}".format(
            self.mnemonic, self.rd, self.rs1, self.rs2, self.rl, self.aq
        )


def isa(mnemonic: str,
        variant: Variant,
        *,
        opcode: int,
        **kwargs
        ):
    """
    Decorator for the instructions. The decorator contains the static information for the
    instructions, in particular the encoding parameters and the assembler mnemonic.

    :param mnemonic: Assembler mnemonic
    :param opcode: Opcode of this instruction
    :return: Wrapper class that overwrites the actual definition and contains static data
    """
    def wrapper(wrapped):
        wrapped.field_opcode = wrapped.field_opcode._replace(value=opcode)

        wrapped.mnemonic = mnemonic
        wrapped.variant = variant

        for field in kwargs:
            fid = "field_"+field
            assert fid in dir(wrapped), "Invalid field {} for {}".format(fid, wrapped.__name__)
            setattr(wrapped, fid, getattr(wrapped, fid)._replace(value=kwargs[field]))

        return wrapped
    return wrapper


def isa_c(mnemonic: str,
          variant: Variant,
          *,
          opcode: int,
          funct3=None,
          funct4=None,
          funct6=None):
    """
    Decorator for the instructions. The decorator contains the static information for the
    instructions, in particular the encoding parameters and the assembler mnemonic.

    :param mnemonic: Assembler mnemonic
    :return: Wrapper class that overwrites the actual definition and contains static data
    """
    def wrapper(wrapped):
        """Get wrapper"""
        class WrappedClass(wrapped):  # pylint: disable=too-few-public-methods
            """Generic wrapper class"""

        WrappedClass.__name__ = wrapped.__name__
        WrappedClass.__module__ = wrapped.__module__
        WrappedClass.__qualname__ = wrapped.__qualname__
        WrappedClass.__doc__ = wrapped.__doc__
        return WrappedClass

    return wrapper


def isa_pseudo():
    """
    TODO: documentation
    """
    def wrapper(wrapped):
        class WrappedClass(wrapped):  # pylint: disable=too-few-public-methods
            """
            Wrapper class
            """

            _pseudo = True

        WrappedClass.__name__ = wrapped.__name__
        WrappedClass.__module__ = wrapped.__module__
        WrappedClass.__qualname__ = wrapped.__qualname__
        WrappedClass.__doc__ = wrapped.__doc__
        return WrappedClass

    return wrapper


def get_insns(*, cls=None, variant: Variant = RV32I):
    """
    Get all Instructions. This is based on all known subclasses of `cls`. If non
    is given, all Instructions are returned. Only such instructions are returned
    that can be generated, i.e., that have a mnemonic, opcode, etc. So other
    classes in the hierarchy are not matched.

    :param cls: Base class to get list :type cls: Instruction :return: List of
    instruction classes
    """
    insns = []

    if cls is None:
        cls = Instruction

    # This filters out abstract classes
    if cls.mnemonic:
        if variant is None or cls.variant <= variant:
            insns = [cls]

    for subcls in cls.__subclasses__():
        insns += get_insns(cls=subcls, variant=variant)

    insns = list(dict.fromkeys(insns)) # Remove duplicates
    return insns


def reverse_lookup(mnemonic: str, variant: Variant = None):
    """
    Find instruction that matches the mnemonic.

    :param mnemonic: Mnemonic to match
    :return: :class:`Instruction` that matches or None
    """
    for i in get_insns(variant=variant):
        if i.mnemonic == mnemonic:
            return i

    return None


def get_mnemomics():
    """
    Get all known mnemonics

    :return: List of all known mnemonics
    :rtype: List[str]
    """
    return [i.mnemonic for i in get_insns()]

