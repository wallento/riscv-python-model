from riscvmodel.insn import *

@isa("lui", 0x37)
class InstructionLUI(InstructionUType):
    def execute(self, model: Model):
        model.intreg[self.rd] = (model.intreg[self.rd] & 0xFFF) | (self.imm << 12)


@isa("auipc", 0x17)
class InstructionAUIPC(InstructionUType):
    def execute(self, model: Model):
        pass


@isa("jal", 0x6F)
class InstructionJAL(InstructionJType):
    def execute(self, model: Model):
        pass


@isa("jalr", 0x67, 0)
class InstructionJALR(InstructionIType):
    def execute(self, model: Model):
        pass


@isa("beq", 0x63, 0)
class InstructionBEQ(InstructionBType):
    def execute(self, model: Model):
        if model.intreg[self.rs1] == model.intreg[self.rs2]:
            model.pc = model.pc + self.imm


@isa("bne", 0x63, 1)
class InstructionBNE(InstructionBType):
    def execute(self, model: Model):
        if model.intreg[self.rs1] != model.intreg[self.rs2]:
            model.pc = model.pc + self.imm


@isa("blt", 0x63, 4)
class InstructionBLT(InstructionBType):
    def execute(self, model: Model):
        if model.intreg[self.rs1] < model.intreg[self.rs2]:
            model.pc = model.pc + self.imm


@isa("bge", 0x63, 5)
class InstructionBGE(InstructionBType):
    def execute(self, model: Model):
        if model.intreg[self.rs1] >= model.intreg[self.rs2]:
            model.pc = model.pc + self.imm


@isa("bltu", 0x63, 6)
class InstructionBLTU(InstructionBType):
    def execute(self, model: Model):
        if model.intreg[self.rs1] < model.intreg[self.rs2]:
            model.pc = model.pc + self.imm


@isa("bgeu", 0x63, 7)
class InstructionBGEU(InstructionBType):
    def execute(self, model: Model):
        if model.intreg[self.rs1] >= model.intreg[self.rs2]:
            model.pc = model.pc + self.imm


@isa("lb", 0x03, 0)
class InstructionLB(InstructionILType):
    def execute(self, model: Model):
        model.intreg[self.rd] = model.lb(model.intreg[self.rs1] + self.imm)


@isa("lh", 0x03, 1)
class InstructionLH(InstructionILType):
    def execute(self, model: Model):
        model.intreg[self.rd] = model.lh(model.intreg[self.rs1] + self.imm)


@isa("lw", 0x03, 2)
class InstructionLW(InstructionILType):
    def execute(self, model: Model):
        model.intreg[self.rd] = model.lw(model.intreg[self.rs1] + self.imm)


@isa("lbu", 0x03, 4)
class InstructionLBU(InstructionILType):
    def execute(self, model: Model):
        pass


@isa("lhu", 0x03, 5)
class InstructionLHU(InstructionILType):
    def execute(self, model: Model):
        pass


@isa("sb", 0x23, 0)
class InstructionSB(InstructionSType):
    def execute(self, model: Model):
        pass


@isa("sh", 0x23, 1)
class InstructionSH(InstructionSType):
    def execute(self, model: Model):
        pass


@isa("sw", 0x23, 2)
class InstructionSW(InstructionSType):
    def execute(self, model: Model):
        pass


@isa("addi", 0x13, 0)
class InstructionADDI(InstructionIType):
    def execute(self, model: Model):
        pass


@isa("slti", 0x13, 2)
class InstructionSLTI(InstructionIType):
    def execute(self, model: Model):
        pass


@isa("sltiu", 0x13, 3)
class InstructionSLTIU(InstructionIType):
    def execute(self, model: Model):
        pass


@isa("xori", 0x13, 4)
class InstructionXORI(InstructionIType):
    def execute(self, model: Model):
        pass


@isa("ori", 0x13, 6)
class InstructionORI(InstructionIType):
    def execute(self, model: Model):
        pass


@isa("andi", 0x13, 7)
class InstructionANDI(InstructionIType):
    def execute(self, model: Model):
        pass


@isa("slli", 0x13, 1, 0x00)
class InstructionSLLI(InstructionISType):
    def execute(self, model: Model):
        pass


@isa("srli", 0x13, 5, 0x00)
class InstructionSRLI(InstructionISType):
    def execute(self, model: Model):
        pass


@isa("srai", 0x13, 5, 0x20)
class InstructionSRAI(InstructionISType):
    def execute(self, model: Model):
        pass


@isa("add", 0x33, 0, 0x00)
class InstructionADD(InstructionRType):
    def execute(self, model: Model):
        model.intreg[self.rd] = model.intreg[self.rs1] + model.intreg[self.rs2]


@isa("sub", 0x33, 0, 0x20)
class InstructionSUB(InstructionRType):
    def execute(self, model: Model):
        model.intreg[self.rd] = model.intreg[self.rs1] - model.intreg[self.rs2]


@isa("sll", 0x33, 1, 0x00)
class InstructionSLL(InstructionRType):
    def execute(self, model: Model):
        model.intreg[self.rd] = model.intreg[self.rs1] << model.intreg[self.rs2]


@isa("slt", 0x33, 2, 0x00)
class InstructionSLT(InstructionRType):
    def execute(self, model: Model):
        if model.intreg[self.rs1] < model.intreg[self.rs2]:
            model.intreg[self.rd] = 1
        else:
            model.intreg[self.rd] = 0


@isa("sltu", 0x33, 3, 0x00)
class InstructionSLTU(InstructionRType):
    def execute(self, model: Model):
        if model.intreg[self.rs1] < model.intreg[self.rs2]:
            model.intreg[self.rd] = 1
        else:
            model.intreg[self.rd] = 0


@isa("xor", 0x33, 4, 0x00)
class InstructionXOR(InstructionRType):
    def execute(self, model: Model):
        model.intreg[self.rd] = model.intreg[self.rs1] ^ model.intreg[self.rs2]


@isa("srl", 0x33, 5, 0x00)
class InstructionSRL(InstructionRType):
    def execute(self, model: Model):
        model.intreg[self.rd] = model.intreg[self.rs1] >> model.intreg[self.rs2]


@isa("sra", 0x33, 5, 0x20)
class InstructionSRA(InstructionRType):
    def execute(self, model: Model):
        model.intreg[self.rd] = model.intreg[self.rs1] >> model.intreg[self.rs2]


@isa("or", 0x33, 6, 0x00)
class InstructionOR(InstructionRType):
    def execute(self, model: Model):
        model.intreg[self.rd] = model.intreg[self.rs1] | model.intreg[self.rs2]


@isa("and", 0x33, 7, 0x00)
class InstructionAND(InstructionRType):
    def execute(self, model: Model):
        model.intreg[self.rd] = model.intreg[self.rs1] & model.intreg[self.rs2]
