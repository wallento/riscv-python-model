from riscvmodel.insn import *

@isa("lui")
class InstructionLUI(InstructionUType):
    def execute(self, model: Model):
        model.intreg[self.rd] = (model.intreg[self.rd] & 0xFFF) | (self.imm << 12)


@isa("auipc")
class InstructionAUIPC(InstructionUType):
    def execute(self, model: Model):
        pass


@isa("jal")
class InstructionJAL(InstructionJType):
    def execute(self, model: Model):
        pass


@isa("jalr", 0)
class InstructionJALR(InstructionIType):
    def execute(self, model: Model):
        pass


@isa("beq", 0)
class InstructionBEQ(InstructionBType):
    def execute(self, model: Model):
        if model.intreg[self.rs1] == model.intreg[self.rs2]:
            model.pc = model.pc + self.imm


@isa("bne", 1)
class InstructionBNE(InstructionBType):
    def execute(self, model: Model):
        if model.intreg[self.rs1] != model.intreg[self.rs2]:
            model.pc = model.pc + self.imm


@isa("blt", 4)
class InstructionBLT(InstructionBType):
    def execute(self, model: Model):
        if model.intreg[self.rs1] < model.intreg[self.rs2]:
            model.pc = model.pc + self.imm


@isa("bge", 5)
class InstructionBGE(InstructionBType):
    def execute(self, model: Model):
        if model.intreg[self.rs1] >= model.intreg[self.rs2]:
            model.pc = model.pc + self.imm


@isa("bltu", 6)
class InstructionBLTU(InstructionBType):
    def execute(self, model: Model):
        if model.intreg[self.rs1] < model.intreg[self.rs2]:
            model.pc = model.pc + self.imm


@isa("bgeu", 7)
class InstructionBGEU(InstructionBType):
    def execute(self, model: Model):
        if model.intreg[self.rs1] >= model.intreg[self.rs2]:
            model.pc = model.pc + self.imm


@isa("lb", 0)
class InstructionLB(InstructionILType):
    def execute(self, model: Model):
        model.intreg[self.rd] = model.lb(model.intreg[self.rs1] + self.imm)


@isa("lh", 1)
class InstructionLH(InstructionILType):
    def execute(self, model: Model):
        model.intreg[self.rd] = model.lh(model.intreg[self.rs1] + self.imm)


@isa("lw", 2)
class InstructionLW(InstructionILType):
    def execute(self, model: Model):
        model.intreg[self.rd] = model.lw(model.intreg[self.rs1] + self.imm)


@isa("lbu", 4)
class InstructionLBU(InstructionILType):
    def execute(self, model: Model):
        pass


@isa("lhu", 5)
class InstructionLHU(InstructionILType):
    def execute(self, model: Model):
        pass


@isa("sb", 0)
class InstructionSB(InstructionSType):
    def execute(self, model: Model):
        pass


@isa("sh", 0)
class InstructionSH(InstructionSType):
    def execute(self, model: Model):
        pass


@isa("sw", 0)
class InstructionSW(InstructionSType):
    def execute(self, model: Model):
        pass


@isa("addi", 0)
class InstructionADDI(InstructionIType):
    def execute(self, model: Model):
        pass


@isa("slti", 2)
class InstructionSLTI(InstructionIType):
    def execute(self, model: Model):
        pass


@isa("sltiu", 3)
class InstructionSLTIU(InstructionIType):
    def execute(self, model: Model):
        pass


@isa("xori", 4)
class InstructionXORI(InstructionIType):
    def execute(self, model: Model):
        pass


@isa("ori", 6)
class InstructionORI(InstructionIType):
    def execute(self, model: Model):
        pass


@isa("andi", 7)
class InstructionANDI(InstructionIType):
    def execute(self, model: Model):
        pass


@isa("slli", 1, 0x00)
class InstructionSLLI(InstructionISType):
    def execute(self, model: Model):
        pass


@isa("srli", 5, 0x00)
class InstructionSRLI(InstructionISType):
    def execute(self, model: Model):
        pass


@isa("srai", 5, 0x20)
class InstructionSRAI(InstructionISType):
    def execute(self, model: Model):
        pass


@isa("add", 0, 0x00)
class InstructionADD(InstructionRType):
    def execute(self, model: Model):
        model.intreg[self.rd] = model.intreg[self.rs1] + model.intreg[self.rs2]


@isa("sub", 0, 0x20)
class InstructionSUB(InstructionRType):
    def execute(self, model: Model):
        model.intreg[self.rd] = model.intreg[self.rs1] - model.intreg[self.rs2]


@isa("sll", 1, 0x00)
class InstructionSLL(InstructionRType):
    def execute(self, model: Model):
        model.intreg[self.rd] = model.intreg[self.rs1] << model.intreg[self.rs2]


@isa("slt", 2, 0x00)
class InstructionSLT(InstructionRType):
    def execute(self, model: Model):
        if model.intreg[self.rs1] < model.intreg[self.rs2]:
            model.intreg[self.rd] = 1
        else:
            model.intreg[self.rd] = 0


@isa("sltu", 3, 0x00)
class InstructionSLTU(InstructionRType):
    def execute(self, model: Model):
        if model.intreg[self.rs1] < model.intreg[self.rs2]:
            model.intreg[self.rd] = 1
        else:
            model.intreg[self.rd] = 0


@isa("xor", 4, 0x00)
class InstructionXOR(InstructionRType):
    def execute(self, model: Model):
        model.intreg[self.rd] = model.intreg[self.rs1] ^ model.intreg[self.rs2]


@isa("srl", 5, 0x00)
class InstructionSRL(InstructionRType):
    def execute(self, model: Model):
        model.intreg[self.rd] = model.intreg[self.rs1] >> model.intreg[self.rs2]


@isa("sra", 5, 0x20)
class InstructionSRA(InstructionRType):
    def execute(self, model: Model):
        model.intreg[self.rd] = model.intreg[self.rs1] >> model.intreg[self.rs2]


@isa("or", 6, 0x00)
class InstructionOR(InstructionRType):
    def execute(self, model: Model):
        model.intreg[self.rd] = model.intreg[self.rs1] | model.intreg[self.rs2]


@isa("and", 7, 0x00)
class InstructionAND(InstructionRType):
    def execute(self, model: Model):
        model.intreg[self.rd] = model.intreg[self.rs1] & model.intreg[self.rs2]
