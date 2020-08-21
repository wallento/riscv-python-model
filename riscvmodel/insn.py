# Copyright Stefan Wallentowitz
# Licensed under the MIT License, see LICENSE for details.
# SPDX-License-Identifier: MIT
"""
Instructions
"""

from .isa import *
from .variant import *
from .model import State

@isa("lui", RV32I, opcode=0b0110111)
class InstructionLUI(InstructionUType):
    """
    The Load Upper Immediate (LUI) instruction loads the given immediate (unsigned 20 bit) to the upper 20 bit
    of the destination register. The lower bits are set to zero in the destination register. This instruction
    can be used to efficiently form constants, as a sequence of LUI and ORI for example.
    """
    def execute(self, model: Model):
        model.state.intreg[self.rd] = (self.imm << 12)


@isa("auipc", RV32I, opcode=0b0010111)
class InstructionAUIPC(InstructionUType):
    def execute(self, model: Model):
        model.state.intreg[self.rd] = model.state.pc + (self.imm << 12)


@isa("jal", RV32I, opcode=0b1101111)
class InstructionJAL(InstructionJType):
    def execute(self, model: Model):
        model.state.intreg[self.rd] = model.state.pc + 4
        model.state.pc += self.imm


@isa("jalr", RV32I, opcode=0b1100111, funct3=0b000)
class InstructionJALR(InstructionIType):
    def execute(self, model: Model):
        model.state.intreg[self.rd] = model.state.pc + 4
        model.state.pc = model.state.intreg[self.rs1] + self.imm


@isa("beq", RV32I, opcode=0b1100011, funct3=0b000)
class InstructionBEQ(InstructionBType):
    def execute(self, model: Model):
        # todo: problem with __cmp__
        if model.state.intreg[self.rs1].value == model.state.intreg[self.rs2].value:
            model.state.pc = model.state.pc + self.imm


@isa("bne", RV32I, opcode=0b1100011, funct3=0b001)
class InstructionBNE(InstructionBType):
    def execute(self, model: Model):
        if model.state.intreg[self.rs1].value != model.state.intreg[self.rs2].value:
            model.state.pc = model.state.pc + self.imm


@isa("blt", RV32I, opcode=0b1100011, funct3=0b100)
class InstructionBLT(InstructionBType):
    def execute(self, model: Model):
        if model.state.intreg[self.rs1].value < model.state.intreg[self.rs2].value:
            model.state.pc = model.state.pc + self.imm


@isa("bge", RV32I, opcode=0b1100011, funct3=0b101)
class InstructionBGE(InstructionBType):
    def execute(self, model: Model):
        if model.state.intreg[self.rs1].value >= model.state.intreg[self.rs2].value:
            model.state.pc = model.state.pc + self.imm


@isa("bltu", RV32I, opcode=0b1100011, funct3=0b110)
class InstructionBLTU(InstructionBType):
    def execute(self, model: Model):
        if model.state.intreg[self.rs1].unsigned() < model.state.intreg[
                self.rs2].unsigned():
            model.state.pc = model.state.pc + self.imm


@isa("bgeu", RV32I, opcode=0b1100011, funct3=0b111)
class InstructionBGEU(InstructionBType):
    def execute(self, model: Model):
        if model.state.intreg[self.rs1].unsigned() >= model.state.intreg[
                self.rs2].unsigned():
            model.state.pc = model.state.pc + self.imm


@isa("lb", RV32I, opcode=0b0000011, funct3=0b000)
class InstructionLB(InstructionILType):
    def execute(self, model: Model):
        data = model.state.memory.lb((model.state.intreg[self.rs1] + self.imm).unsigned())
        if (data >> 7) & 0x1:
            data |= 0xFFFFFF00
        model.state.intreg[self.rd] = data


@isa("lh", RV32I, opcode=0b0000011, funct3=0b001)
class InstructionLH(InstructionILType):
    def execute(self, model: Model):
        data = model.state.memory.lh((model.state.intreg[self.rs1] + self.imm).unsigned())
        if (data >> 15) & 0x1:
            data |= 0xFFFF0000
        model.state.intreg[self.rd] = data


@isa("lw", RV32I, opcode=0b0000011, funct3=0b010)
class InstructionLW(InstructionILType):
    def execute(self, model: Model):
        data = model.state.memory.lw((model.state.intreg[self.rs1] + self.imm).unsigned())
        model.state.intreg[self.rd] = data


@isa("lbu", RV32I, opcode=0b0000011, funct3=0b100)
class InstructionLBU(InstructionILType):
    def execute(self, model: Model):
        model.state.intreg[self.rd] = model.state.memory.lb(
            (model.state.intreg[self.rs1] + self.imm).unsigned())


@isa("lhu", RV32I, opcode=0b0000011, funct3=0b101)
class InstructionLHU(InstructionILType):
    def execute(self, model: Model):
        model.state.intreg[self.rd] = model.state.memory.lh(
            (model.state.intreg[self.rs1] + self.imm).unsigned())


@isa("sb", RV32I, opcode=0b0100011, funct3=0b000)
class InstructionSB(InstructionSType):
    def execute(self, model: Model):
        model.state.memory.sb((model.state.intreg[self.rs1] + self.imm).unsigned(),
                        model.state.intreg[self.rs2])


@isa("sh", RV32I, opcode=0b0100011, funct3=0b001)
class InstructionSH(InstructionSType):
    def execute(self, model: Model):
        model.state.memory.sh((model.state.intreg[self.rs1] + self.imm).unsigned(),
                        model.state.intreg[self.rs2])


@isa("sw", RV32I, opcode=0b0100011, funct3=0b010)
class InstructionSW(InstructionSType):
    def execute(self, model: Model):
        model.state.memory.sw((model.state.intreg[self.rs1] + self.imm).unsigned(),
                        model.state.intreg[self.rs2])


@isa("addi", RV32I, opcode=0b0010011, funct3=0b000)
class InstructionADDI(InstructionIType):
    def execute(self, model: Model):
        model.state.intreg[self.rd] = model.state.intreg[self.rs1] + self.imm


@isa("slti", RV32I, opcode=0b0010011, funct3=0b010)
class InstructionSLTI(InstructionIType):
    def execute(self, model: Model):
        if model.state.intreg[self.rs1] < self.imm:
            model.state.intreg[self.rd] = 1
        else:
            model.state.intreg[self.rd] = 0


@isa("sltiu", RV32I, opcode=0b0010011, funct3=0b011)
class InstructionSLTIU(InstructionIType):
    def execute(self, model: Model):
        if model.state.intreg[self.rs1].unsigned() < int(self.imm):
            model.state.intreg[self.rd] = 1
        else:
            model.state.intreg[self.rd] = 0


@isa("xori", RV32I, opcode=0b0010011, funct3=0b100)
class InstructionXORI(InstructionIType):
    def execute(self, model: Model):
        model.state.intreg[self.rd] = model.state.intreg[self.rs1] ^ self.imm


@isa("ori", RV32I, opcode=0b0010011, funct3=0b110)
class InstructionORI(InstructionIType):
    def execute(self, model: Model):
        model.state.intreg[self.rd] = model.state.intreg[self.rs1] | self.imm


@isa("andi", RV32I, opcode=0b0010011, funct3=0b111)
class InstructionANDI(InstructionIType):
    def execute(self, model: Model):
        model.state.intreg[self.rd] = model.state.intreg[self.rs1] & self.imm


@isa("slli", RV32I, opcode=0b0010011, funct3=0b001, funct7=0b0000000)
class InstructionSLLI(InstructionISType):
    def execute(self, model: Model):
        model.state.intreg[self.rd] = model.state.intreg[self.rs1] << self.shamt


@isa("srli", RV32I, opcode=0b0010011, funct3=0b101, funct7=0b0000000)
class InstructionSRLI(InstructionISType):
    def execute(self, model: Model):
        model.state.intreg[self.rd] = model.state.intreg[self.rs1].unsigned() >> int(
            self.shamt)


@isa("srai", RV32I, opcode=0b0010011, funct3=0b101, funct7=0b0100000)
class InstructionSRAI(InstructionISType):
    def execute(self, model: Model):
        model.state.intreg[self.rd] = model.state.intreg[self.rs1] >> self.shamt


@isa("add", RV32I, opcode=0b0110011, funct3=0b000, funct7=0b0000000)
class InstructionADD(InstructionRType):
    def execute(self, model: Model):
        model.state.intreg[self.rd] = model.state.intreg[self.rs1] + model.state.intreg[self.rs2]


@isa("sub", RV32I, opcode=0b0110011, funct3=0b000, funct7=0b0100000)
class InstructionSUB(InstructionRType):
    def execute(self, model: Model):
        model.state.intreg[self.rd] = model.state.intreg[self.rs1] - model.state.intreg[self.rs2]


@isa("sll", RV32I, opcode=0b0110011, funct3=0b001, funct7=0b0000000)
class InstructionSLL(InstructionRType):
    def execute(self, model: Model):
        model.state.intreg[self.rd] = model.state.intreg[self.rs1] << (
            model.state.intreg[self.rs2] & 0x1f)


@isa("slt", RV32I, opcode=0b0110011, funct3=0b010, funct7=0b0000000)
class InstructionSLT(InstructionRType):
    def execute(self, model: Model):
        if model.state.intreg[self.rs1] < model.state.intreg[self.rs2]:
            model.state.intreg[self.rd] = 1
        else:
            model.state.intreg[self.rd] = 0


@isa("sltu", RV32I, opcode=0b0110011, funct3=0b011, funct7=0b0000000)
class InstructionSLTU(InstructionRType):
    def execute(self, state: State):
        if state.intreg[self.rs1].unsigned() < state.intreg[
                self.rs2].unsigned():
            state.intreg[self.rd] = 1
        else:
            state.intreg[self.rd] = 0


@isa("xor", RV32I, opcode=0b0110011, funct3=0b100, funct7=0b0000000)
class InstructionXOR(InstructionRType):
    def execute(self, model: Model):
        model.state.intreg[self.rd] = model.state.intreg[self.rs1] ^ model.state.intreg[self.rs2]


@isa("srl", RV32I, opcode=0b0110011, funct3=0b101, funct7=0b0000000)
class InstructionSRL(InstructionRType):
    def execute(self, model: Model):
        src = model.state.intreg[self.rs1]
        shift = model.state.intreg[self.rs2] & 0x1f
        model.state.intreg[self.rd] = src >> shift


@isa("sra", RV32I, opcode=0b0110011, funct3=0b101, funct7=0b0100000)
class InstructionSRA(InstructionRType):
    def execute(self, model: Model):
        usrc = model.state.intreg[self.rs1].unsigned()
        shift = model.state.intreg[self.rs2].unsigned() & 0x1f
        if usrc >> 31:
            to_clear = 32 - shift
            sign_mask = (((1 << 32) - 1) >> to_clear) << to_clear
        else:
            sign_mask = 0

        model.state.intreg[self.rd] = sign_mask | (usrc >> shift)


@isa("or", RV32I, opcode=0b0110011, funct3=0b110, funct7=0b0000000)
class InstructionOR(InstructionRType):
    def execute(self, model: Model):
        model.state.intreg[self.rd] = model.state.intreg[self.rs1] | model.state.intreg[self.rs2]


@isa("and", RV32I, opcode=0b0110011, funct3=0b111, funct7=0b0000000)
class InstructionAND(InstructionRType):
    def execute(self, model: Model):
        model.state.intreg[self.rd] = model.state.intreg[self.rs1] & model.state.intreg[self.rs2]


@isa("fence", RV32I, opcode=0b0001111, funct3=0b000)
class InstructionFENCE(InstructionIType):
    isa_format_id = "FENCE"

    def execute(self, model: Model):
        pass


@isa("fence.i", RV32IZifencei, opcode=0b0001111, funct3=0b001)
class InstructionFENCEI(InstructionIType):
    def execute(self, model: Model):
        pass


@isa("ecall", RV32I, opcode=0b1110011, funct3=0b000, imm=0b000000000000, rd=0b00000, rs1=0b00000)
class InstructionECALL(InstructionIType):
    def execute(self, model: Model):
        model.environment.call(model.state)

    def __str__(self):
        return "ecall"


@isa("uret", RV32I, opcode=0b1110011, funct3=0b000, imm=0b000000000010, rs1=0b00000, rd=0b00000)
class InstructionURET(InstructionIType):
    """ Machine level exception return """
    def execute(self, model: Model):
        # TODO: implement
        pass


@isa("sret", RV32I, opcode=0b1110011, funct3=0b000, imm=0b000100000010, rs1=0b00000, rd=0b00000)
class InstructionSRET(InstructionIType):
    """ Machine level exception return """
    def execute(self, model: Model):
        # TODO: implement
        pass


@isa("hret", RV32I, opcode=0b1110011, funct3=0b000, imm=0b001000000010, rs1=0b00000, rd=0b00000)
class InstructionHRET(InstructionIType):
    """ Machine level exception return """
    def execute(self, model: Model):
        # TODO: implement
        pass


@isa("mret", RV32I, opcode=0b1110011, funct3=0b000, imm=0b001100000010, rs1=0b00000, rd=0b00000)
class InstructionMRET(InstructionIType):
    """ Machine level exception return """
    def execute(self, model: Model):
        # TODO: implement
        pass


@isa("wfi", RV32I, opcode=0b1110011, funct3=0b000, imm=0b000100000101, rs1=0b00000, rd=0b00000)
class InstructionWFI(InstructionIType):
    def execute(self, model: Model):
        pass


@isa("ebreak", RV32I, opcode=0b1110011, funct3=0b000, imm=0b000000000001)
class InstructionEBREAK(InstructionIType):
    def execute(self, model: Model):
        pass

    def __str__(self):
        return "ebreak"


@isa("csrrw", RV32IZicsr, opcode=0b1110011, funct3=0b001)
class InstructionCSRRW(InstructionIType):
    def execute(self, model: Model):
        pass


@isa("csrrs", RV32IZicsr, opcode=0b1110011, funct3=0b010)
class InstructionCSRRS(InstructionIType):
    def execute(self, model: Model):
        pass


@isa("csrrc", RV32IZicsr, opcode=0b1110011, funct3=0b011)
class InstructionCSRRC(InstructionIType):
    def execute(self, model: Model):
        pass


#@isa("csrrwi", RV32IZicsr, opcode=0b1110011, funct3=0b101)
#class InstructionCSRRWI(Instruction):
#    def execute(self, model: Model):
#        pass


#@isa("csrrsi", RV32IZicsr, opcode=0b1110011, funct3=0b110)
#class InstructionCSRRSI(Instruction):
#    def execute(self, model: Model):
#        pass


#@isa("csrrci", RV32IZicsr, opcode=0b1110011, funct3=0b111)
#class InstructionCSRRCI(Instruction):
#    def execute(self, model: Model):
#        pass


@isa("lwu", RV64I, opcode=0b0000011, funct3=0b110)
class InstructionLWU(InstructionIType):
    def execute(self, model: Model):
        pass


@isa("ld", RV64I, opcode=0b0000011, funct3=0b011)
class InstructionLD(InstructionIType):
    def execute(self, model: Model):
        pass


@isa("sd", RV64I, opcode=0b0100011, funct3=0b011)
class InstructionSD(InstructionISType):
    def execute(self, model: Model):
        pass


@isa_pseudo()
class InstructionNOP(InstructionADDI):
    def __init__(self):
        super().__init__(0, 0, 0)

    def __str__(self):
        return "nop"


@isa("mul", RV32IM, opcode=0b0110011, funct3=0b000, funct7=0b0000001)
class InstructionMUL(InstructionRType):
    def execute(self, model: Model):
        model.state.intreg[self.rd] = model.state.intreg[self.rs1] * model.state.intreg[self.rs2]


@isa("mulh", RV32IM, opcode=0b0110011, funct3=0b001, funct7=0b0000001)
class InstructionMULH(InstructionRType):
    def execute(self, model: Model):
        # TODO: implement
        pass


@isa("mulhsu", RV32IM, opcode=0b0110011, funct3=0b010, funct7=0b0000001)
class InstructionMULHSU(InstructionRType):
    def execute(self, model: Model):
        # TODO: implement
        pass


@isa("mulhu", RV32IM, opcode=0b0110011, funct3=0b011, funct7=0b0000001)
class InstructionMULHU(InstructionRType):
    def execute(self, model: Model):
        # TODO: implement
        pass


@isa("div", RV32IM, opcode=0b0110011, funct3=0b100, funct7=0b0000001)
class InstructionDIV(InstructionRType):
    def execute(self, model: Model):
        # TODO: implement
        pass


@isa("divu", RV32IM, opcode=0b0110011, funct3=0b101, funct7=0b0000001)
class InstructionDIVU(InstructionRType):
    def execute(self, model: Model):
        # TODO: implement
        pass


@isa("rem", RV32IM, opcode=0b0110011, funct3=0b110, funct7=0b0000001)
class InstructionREM(InstructionRType):
    def execute(self, model: Model):
        # TODO: implement
        pass


@isa("remu", RV32IM, opcode=0b0110011, funct3=0b111, funct7=0b0000001)
class InstructionREMU(InstructionRType):
    def execute(self, model: Model):
        # TODO: implement
        pass


@isa_c("c.addi", RV32IC, opcode=1, funct3=0b000)
class InstructionCADDI(InstructionCIType):
    def expand(self):
        pass

    def execute(self, model: Model):
        model.state.intreg[self.rd] = model.state.intreg[self.rd] + self.imm


@isa_c("c.andi", RV32IC, opcode=1, funct3=0b100)
class InstructionCANDI(InstructionCBType):
    def expand(self):
        pass

    def execute(self, model: Model):
        pass


@isa_c("c.swsp", RV32IC, opcode=2, funct3=6)
class InstructionCSWSP(InstructionCSSType):
    def expand(self):
        pass

    def decode(self, machinecode: int):
        self.rs = (machinecode >> 2) & 0x1f
        imm12to9 = (machinecode >> 9) & 0xf
        imm8to7 = (machinecode >> 7) & 0x3
        self.imm.set_from_bits((imm8to7 << 4) | imm12to9)

    def execute(self, model: Model):
        pass


@isa_c("c.li", RV32IC, opcode=1, funct3=2)
class InstructionCLI(InstructionCIType):
    def expand(self):
        pass

    def execute(self, model: Model):
        model.state.intreg[self.rd] = self.imm


@isa_c("c.mv", RV32IC, opcode=2, funct4=8)
class InstructionCMV(InstructionCRType):
    def expand(self):
        pass

    def execute(self, model: Model):
        model.state.intreg[self.rd] = model.state.intreg[self.rs]


@isa("lr", RV32A, opcode=0b0101111, funct5=0b00010, funct3=0b010)
class InstructionLR(InstructionAMOType):
    """ Load reserved """
    def execute(self, model: Model):
        # Perform a normal load
        data = model.state.memory.lw(model.state.intreg[self.rs1].unsigned())
        model.state.intreg[self.rd] = data
        # Perform correct lock or release actions
        if self.rl: model.state.atomic_release(model.state.intreg[self.rs1])
        elif self.aq: model.state.atomic_acquire(model.state.intreg[self.rs1])


@isa("sc", RV32A, opcode=0b0101111, funct5=0b00011, funct3=0b010)
class InstructionSC(InstructionAMOType):
    """ Store conditional """
    def execute(self, model: Model):
        # Check if this address is reserved
        if model.state.atomic_reserved(model.state.intreg[self.rs1]):
            model.state.memory.sw(
                model.state.intreg[self.rs1].unsigned(),
                model.state.intreg[self.rs2]
            )
            model.state.intreg[self.rd] = 0
        else:
            model.state.intreg[self.rd] = 1
        # Perform correct lock or release actions
        if self.rl: model.state.atomic_release(model.state.intreg[self.rs1])
        elif self.aq: model.state.atomic_acquire(model.state.intreg[self.rs1])


@isa("amoadd", RV32A, opcode=0b0101111, funct5=0b00000, funct3=0b010)
class InstructionAMOADD(InstructionAMOType):
    """ Atomic add operation """
    def execute(self, model: Model):
        # This models a single HART with 1 stage pipeline, so will always succeed
        model.state.intreg[self.rd] = model.state.memory.lw(
            model.state.intreg[self.rs1].unsigned()
        )
        model.state.memory.sw(
            model.state.intreg[self.rs1].unsigned(),
            (model.state.intreg[self.rs2] + model.state.intreg[self.rd])
        )
        # Perform correct lock or release actions
        if self.rl: model.state.atomic_release(model.state.intreg[self.rs1])
        elif self.aq: model.state.atomic_acquire(model.state.intreg[self.rs1])


@isa("amoxor", RV32A, opcode=0b0101111, funct5=0b00100, funct3=0b010)
class InstructionAMOXOR(InstructionAMOType):
    """ Atomic XOR operation """
    def execute(self, model: Model):
        # This models a single HART with 1 stage pipeline, so will always succeed
        model.state.intreg[self.rd] = model.state.memory.lw(
            model.state.intreg[self.rs1].unsigned()
        )
        model.state.memory.sw(
            model.state.intreg[self.rs1].unsigned(),
            (model.state.intreg[self.rs2] ^ model.state.intreg[self.rd])
        )
        # Perform correct lock or release actions
        if self.rl: model.state.atomic_release(model.state.intreg[self.rs1])
        elif self.aq: model.state.atomic_acquire(model.state.intreg[self.rs1])


@isa("amoor",   RV32A, opcode=0b0101111, funct5=0b01000, funct3=0b010)
class InstructionAMOOR(InstructionAMOType):
    """ Atomic OR operation """
    def execute(self, model: Model):
        # This models a single HART with 1 stage pipeline, so will always succeed
        model.state.intreg[self.rd] = model.state.memory.lw(
            model.state.intreg[self.rs1].unsigned()
        )
        model.state.memory.sw(
            model.state.intreg[self.rs1].unsigned(),
            (model.state.intreg[self.rs2] | model.state.intreg[self.rd])
        )
        # Perform correct lock or release actions
        if self.rl: model.state.atomic_release(model.state.intreg[self.rs1])
        elif self.aq: model.state.atomic_acquire(model.state.intreg[self.rs1])


@isa("amoand", RV32A, opcode=0b0101111, funct5=0b01100, funct3=0b010)
class InstructionAMOAND(InstructionAMOType):
    """ Atomic AND operation """
    def execute(self, model: Model):
        # This models a single HART with 1 stage pipeline, so will always succeed
        model.state.intreg[self.rd] = model.state.memory.lw(
            model.state.intreg[self.rs1].unsigned()
        )
        model.state.memory.sw(
            model.state.intreg[self.rs1].unsigned(),
            (model.state.intreg[self.rs2] & model.state.intreg[self.rd])
        )
        # Perform correct lock or release actions
        if self.rl: model.state.atomic_release(model.state.intreg[self.rs1])
        elif self.aq: model.state.atomic_acquire(model.state.intreg[self.rs1])


@isa("amomin", RV32A, opcode=0b0101111, funct5=0b10000, funct3=0b010)
class InstructionAMOMIN(InstructionAMOType):
    """ Atomic minimum operation """
    def execute(self, model: Model):
        # This models a single HART with 1 stage pipeline, so will always succeed
        model.state.intreg[self.rd] = model.state.memory.lw(
            model.state.intreg[self.rs1].unsigned()
        )
        model.state.memory.sw(
            model.state.intreg[self.rs1].unsigned(),
            min(model.state.intreg[self.rs2], model.state.intreg[self.rd])
        )
        # Perform correct lock or release actions
        if self.rl: model.state.atomic_release(model.state.intreg[self.rs1])
        elif self.aq: model.state.atomic_acquire(model.state.intreg[self.rs1])


@isa("amomax", RV32A, opcode=0b0101111, funct5=0b10100, funct3=0b010)
class InstructionAMOMAX(InstructionAMOType):
    """ Atomic maximum operation """
    def execute(self, model: Model):
        # This models a single HART with 1 stage pipeline, so will always succeed
        model.state.intreg[self.rd] = model.state.memory.lw(
            model.state.intreg[self.rs1].unsigned()
        )
        model.state.memory.sw(
            model.state.intreg[self.rs1].unsigned(),
            max(model.state.intreg[self.rs2], model.state.intreg[self.rd])
        )
        # Perform correct lock or release actions
        if self.rl: model.state.atomic_release(model.state.intreg[self.rs1])
        elif self.aq: model.state.atomic_acquire(model.state.intreg[self.rs1])


@isa("amominu", RV32A, opcode=0b0101111, funct5=0b11000, funct3=0b010)
class InstructionAMOMINU(InstructionAMOType):
    """ Atomic unsigned minimum operation """
    def execute(self, model: Model):
        # This models a single HART with 1 stage pipeline, so will always succeed
        model.state.intreg[self.rd] = model.state.memory.lw(
            model.state.intreg[self.rs1].unsigned()
        )
        model.state.memory.sw(
            model.state.intreg[self.rs1].unsigned(),
            min(
                model.state.intreg[self.rs2].unsigned(),
                model.state.intreg[self.rd].unsigned()
            )
        )
        # Perform correct lock or release actions
        if self.rl: model.state.atomic_release(model.state.intreg[self.rs1])
        elif self.aq: model.state.atomic_acquire(model.state.intreg[self.rs1])


@isa("amomaxu", RV32A, opcode=0b0101111, funct5=0b11100, funct3=0b010)
class InstructionAMOMAXU(InstructionAMOType):
    """ Atomic unsigned maximum operation """
    def execute(self, model: Model):
        # This models a single HART with 1 stage pipeline, so will always succeed
        model.state.intreg[self.rd] = model.state.memory.lw(
            model.state.intreg[self.rs1].unsigned()
        )
        model.state.memory.sw(
            model.state.intreg[self.rs1].unsigned(),
            max(
                model.state.intreg[self.rs2].unsigned(),
                model.state.intreg[self.rd].unsigned()
            )
        )
        # Perform correct lock or release actions
        if self.rl: model.state.atomic_release(model.state.intreg[self.rs1])
        elif self.aq: model.state.atomic_acquire(model.state.intreg[self.rs1])


@isa("amoswap", RV32A, opcode=0b0101111, funct5=0b00001, funct3=0b010)
class InstructionAMOSWAP(InstructionAMOType):
    """ Atomic swap operation """
    def execute(self, model: Model):
        # This models a single HART with 1 stage pipeline, so will always succeed
        model.state.intreg[self.rd] = model.state.memory.lw(
            model.state.intreg[self.rs1].unsigned()
        )
        model.state.memory.sw(
            model.state.intreg[self.rs1].unsigned(),
            model.state.intreg[self.rs2]
        )
        # Perform correct lock or release actions
        if self.rl: model.state.atomic_release(model.state.intreg[self.rs1])
        elif self.aq: model.state.atomic_acquire(model.state.intreg[self.rs1])
