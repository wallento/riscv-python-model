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
        model.state.pc = self.imm


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
        model.state.intreg[
            self.rd] = model.state.intreg[self.rs1] >> model.state.intreg[self.rs2]


@isa("sra", RV32I, opcode=0b0110011, funct3=0b101, funct7=0b0100000)
class InstructionSRA(InstructionRType):
    def execute(self, model: Model):
        model.state.intreg[
            self.rd] = model.state.intreg[self.rs1] >> model.state.intreg[self.rs2]


@isa("or", RV32I, opcode=0b0110011, funct3=0b110, funct7=0b0000000)
class InstructionOR(InstructionRType):
    def execute(self, model: Model):
        model.state.intreg[self.rd] = model.state.intreg[self.rs1] | model.state.intreg[self.rs2]


@isa("and", RV32I, opcode=0b0110011, funct3=0b111, funct7=0b0000000)
class InstructionAND(InstructionRType):
    def execute(self, model: Model):
        model.state.intreg[self.rd] = model.state.intreg[self.rs1] & model.state.intreg[self.rs2]


@isa("fence", RV32I, opcode=0b0001111, funct3=0b000, funct7=0b0000000)
class InstructionFENCE(Instruction):
    def execute(self, model: Model):
        pass


@isa("fence.i", RV32I, opcode=0b0001111, funct3=0b001, funct7=0b0000000)
class InstructionFENCEI(Instruction):
    def execute(self, model: Model):
        pass


@isa("ecall", RV32I, opcode=0b1110011, funct3=0b000, funct12=0b000000000000)
class InstructionECALL(Instruction):
    def execute(self, model: Model):
        model.environment.call(model.state)

    def __str__(self):
        return "ecall"


@isa("wfi", RV32I, opcode=0b1110011, funct3=0b000, funct12=0b000100000101)
class InstructionWFI(Instruction):
    def execute(self, model: Model):
        pass


@isa("ebreak", RV32I, opcode=0b1110011, funct3=0b000)
class InstructionEBREAK(Instruction):
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
class InstructionCSRRC(Instruction):
    def execute(self, model: Model):
        pass


@isa("csrrwi", RV32IZicsr, opcode=0b1110011, funct3=0b101)
class InstructionCSRRWI(Instruction):
    def execute(self, model: Model):
        pass


@isa("csrrsi", RV32IZicsr, opcode=0b1110011, funct3=0b110)
class InstructionCSRRSI(Instruction):
    def execute(self, model: Model):
        pass


@isa("csrrci", RV32IZicsr, opcode=0b1110011, funct3=0b111)
class InstructionCSRRCI(Instruction):
    def execute(self, model: Model):
        pass


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


@isaC("c.addi", RV32IC, opcode=1, funct3=0b000)
class InstructionCADDI(InstructionCIType):
    def expand(self):
        pass

    def execute(self, model: Model):
        model.state.intreg[self.rd] = model.state.intreg[self.rd] + self.imm


@isaC("c.andi", RV32IC, opcode=1, funct3=0b100)
class InstructionCANDI(InstructionCBType):
    def expand(self):
        pass

    def execute(self, model: Model):
        pass


@isaC("c.swsp", RV32IC, opcode=2, funct3=6)
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


@isaC("c.li", RV32IC, opcode=1, funct3=2)
class InstructionCLI(InstructionCIType):
    def expand(self):
        pass

    def execute(self, model: Model):
        model.state.intreg[self.rd] = self.imm


@isaC("c.mv", RV32IC, opcode=2, funct4=8)
class InstructionCMV(InstructionCRType):
    def expand(self):
        pass

    def execute(self, model: Model):
        model.state.intreg[self.rd] = model.state.intreg[self.rs]
