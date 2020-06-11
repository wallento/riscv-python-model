from .insn import *
from .variant import RV64I,Extensions


@isa("lui", opcode=0b0110111)
class InstructionLUI(InstructionUType):
    """
    The Load Upper Immediate (LUI) instruction loads the given immediate (unsigned 20 bit) to the upper 20 bit
    of the destination register. The lower bits are set to zero in the destination register. This instruction
    can be used to efficiently form constants, as a sequence of LUI and ORI for example.
    """
    def execute(self, model: State):
        model.intreg[self.rd] = (self.imm << 12)


@isa("auipc", opcode=0b0010111)
class InstructionAUIPC(InstructionUType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.pc + (self.imm << 12)


@isa("jal", opcode=0b1101111)
class InstructionJAL(InstructionJType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.pc + 4
        model.pc = self.imm


@isa("jalr", opcode=0b1100111, funct3=0b000)
class InstructionJALR(InstructionIType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.pc + 4
        model.pc = model.intreg[self.rs1] + self.imm


@isa("beq", opcode=0b1100011, funct3=0b000)
class InstructionBEQ(InstructionBType):
    def execute(self, model: State):
        # todo: problem with __cmp__
        if model.intreg[self.rs1].value == model.intreg[self.rs2].value:
            model.pc = model.pc + self.imm


@isa("bne", opcode=0b1100011, funct3=0b001)
class InstructionBNE(InstructionBType):
    def execute(self, model: State):
        if model.intreg[self.rs1].value != model.intreg[self.rs2].value:
            model.pc = model.pc + self.imm


@isa("blt", opcode=0b1100011, funct3=0b100)
class InstructionBLT(InstructionBType):
    def execute(self, model: State):
        if model.intreg[self.rs1].value < model.intreg[self.rs2].value:
            model.pc = model.pc + self.imm


@isa("bge", opcode=0b1100011, funct3=0b101)
class InstructionBGE(InstructionBType):
    def execute(self, model: State):
        if model.intreg[self.rs1].value >= model.intreg[self.rs2].value:
            model.pc = model.pc + self.imm


@isa("bltu", opcode=0b1100011, funct3=0b110)
class InstructionBLTU(InstructionBType):
    def execute(self, model: State):
        if model.intreg[self.rs1].unsigned() < model.intreg[self.rs2].unsigned():
            model.pc = model.pc + self.imm


@isa("bgeu", opcode=0b1100011, funct3=0b111)
class InstructionBGEU(InstructionBType):
    def execute(self, model: State):
        if model.intreg[self.rs1].unsigned() >= model.intreg[self.rs2].unsigned():
            model.pc = model.pc + self.imm


@isa("lb", opcode=0b0000011, funct3=0b000)
class InstructionLB(InstructionILType):
    def execute(self, model: State):
        data = model.memory.lb((model.intreg[self.rs1] + self.imm).unsigned())
        if (data >> 7) & 0x1:
            data |= 0xFFFFFF00
        model.intreg[self.rd] = data

@isa("lh", opcode=0b0000011, funct3=0b001)
class InstructionLH(InstructionILType):
    def execute(self, model: State):
        data = model.memory.lh((model.intreg[self.rs1] + self.imm).unsigned())
        if (data >> 15) & 0x1:
            data |= 0xFFFF0000
        model.intreg[self.rd] = data

@isa("lw", opcode=0b0000011, funct3=0b010)
class InstructionLW(InstructionILType):
    def execute(self, model: State):
        data = model.memory.lw((model.intreg[self.rs1] + self.imm).unsigned())
        model.intreg[self.rd] = data


@isa("lbu", opcode=0b0000011, funct3=0b100)
class InstructionLBU(InstructionILType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.memory.lb((model.intreg[self.rs1] + self.imm).unsigned())


@isa("lhu", opcode=0b0000011, funct3=0b101)
class InstructionLHU(InstructionILType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.memory.lh((model.intreg[self.rs1] + self.imm).unsigned())


@isa("sb", opcode=0b0100011, funct3=0b000)
class InstructionSB(InstructionSType):
    def execute(self, model: State):
        model.memory.sb((model.intreg[self.rs1] + self.imm).unsigned(), model.intreg[self.rs2])


@isa("sh", opcode=0b0100011, funct3=0b001)
class InstructionSH(InstructionSType):
    def execute(self, model: State):
        model.memory.sh((model.intreg[self.rs1] + self.imm).unsigned(), model.intreg[self.rs2])


@isa("sw", opcode=0b0100011, funct3=0b010)
class InstructionSW(InstructionSType):
    def execute(self, model: State):
        model.memory.sw((model.intreg[self.rs1] + self.imm).unsigned(), model.intreg[self.rs2])


@isa("addi", opcode=0b0010011, funct3=0b000)
class InstructionADDI(InstructionIType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] + self.imm


@isa("slti", opcode=0b0010011, funct3=0b010)
class InstructionSLTI(InstructionIType):
    def execute(self, model: State):
        if model.intreg[self.rs1] < self.imm:
            model.intreg[self.rd] = 1
        else:
            model.intreg[self.rd] = 0


@isa("sltiu", opcode=0b0010011, funct3=0b011)
class InstructionSLTIU(InstructionIType):
    def execute(self, model: State):
        if model.intreg[self.rs1].unsigned() < int(self.imm):
            model.intreg[self.rd] = 1
        else:
            model.intreg[self.rd] = 0


@isa("xori", opcode=0b0010011, funct3=0b100)
class InstructionXORI(InstructionIType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] ^ self.imm


@isa("ori", opcode=0b0010011, funct3=0b110)
class InstructionORI(InstructionIType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] | self.imm


@isa("andi", opcode=0b0010011, funct3=0b111)
class InstructionANDI(InstructionIType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] & self.imm


@isa("slli", opcode=0b0010011, funct3=0b001, funct7=0b0000000)
class InstructionSLLI(InstructionISType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] << self.shamt


@isa("srli", opcode=0b0010011, funct3=0b101, funct7=0b0000000)
class InstructionSRLI(InstructionISType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1].unsigned() >> int(self.shamt)


@isa("srai", opcode=0b0010011, funct3=0b101, funct7=0b0100000)
class InstructionSRAI(InstructionISType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] >> self.shamt


@isa("add", opcode=0b0110011, funct3=0b000, funct7=0b0000000)
class InstructionADD(InstructionRType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] + model.intreg[self.rs2]


@isa("sub", opcode=0b0110011, funct3=0b000, funct7=0b0100000)
class InstructionSUB(InstructionRType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] - model.intreg[self.rs2]


@isa("sll", opcode=0b0110011, funct3=0b001, funct7=0b0000000)
class InstructionSLL(InstructionRType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] << (model.intreg[self.rs2] & 0x1f)


@isa("slt", opcode=0b0110011, funct3=0b010, funct7=0b0000000)
class InstructionSLT(InstructionRType):
    def execute(self, model: State):
        if model.intreg[self.rs1] < model.intreg[self.rs2]:
            model.intreg[self.rd] = 1
        else:
            model.intreg[self.rd] = 0


@isa("sltu", opcode=0b0110011, funct3=0b011, funct7=0b0000000)
class InstructionSLTU(InstructionRType):
    def execute(self, state: State):
        if state.intreg[self.rs1].unsigned() < state.intreg[self.rs2].unsigned():
            state.intreg[self.rd] = 1
        else:
            state.intreg[self.rd] = 0


@isa("xor", opcode=0b0110011, funct3=0b100, funct7=0b0000000)
class InstructionXOR(InstructionRType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] ^ model.intreg[self.rs2]


@isa("srl", opcode=0b0110011, funct3=0b101, funct7=0b0000000)
class InstructionSRL(InstructionRType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] >> model.intreg[self.rs2]


@isa("sra", opcode=0b0110011, funct3=0b101, funct7=0b0100000)
class InstructionSRA(InstructionRType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] >> model.intreg[self.rs2]


@isa("or", opcode=0b0110011, funct3=0b110, funct7=0b0000000)
class InstructionOR(InstructionRType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] | model.intreg[self.rs2]


@isa("and", opcode=0b0110011, funct3=0b111, funct7=0b0000000)
class InstructionAND(InstructionRType):
    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs1] & model.intreg[self.rs2]


@isa("fence", opcode=0b0001111, funct3=0b000, funct7=0b0000000)
class InstructionFENCE(Instruction):
    def execute(self, model: State):
        pass

@isa("fence.i", opcode=0b0001111, funct3=0b001, funct7=0b0000000)
class InstructionFENCEI(Instruction):
    def execute(self, model: State):
        pass


@isa("ecall", opcode=0b1110011, funct3=0b000, funct12=0b000000000000)
class InstructionECALL(Instruction):
    def execute(self, model: State):
        pass
    def __str__(self):
        return "ecall"

@isa("wfi", opcode=0b1110011, funct3=0b000, funct12=0b000100000101)
class InstructionWFI(Instruction):
    def execute(self, model: State):
        pass


@isa("ebreak", opcode=0b1110011, funct3=0b000)
class InstructionEBREAK(Instruction):
    def execute(self, model: State):
        pass
    def __str__(self):
        return "ebreak"


@isa("csrrw", opcode=0b1110011, funct3=0b001)
class InstructionCSRRW(InstructionIType):
    def execute(self, model: State):
        pass


@isa("csrrs", opcode=0b1110011, funct3=0b010)
class InstructionCSRRS(InstructionIType):
    def execute(self, model: State):
        pass


@isa("csrrc", opcode=0b1110011, funct3=0b011)
class InstructionCSRRC(Instruction):
    pass


@isa("csrrwi", opcode=0b1110011, funct3=0b101)
class InstructionCSRRWI(Instruction):
    pass


@isa("csrrsi", opcode=0b1110011, funct3=0b110)
class InstructionCSRRSI(Instruction):
    pass


@isa("csrrci", opcode=0b1110011, funct3=0b111)
class InstructionCSRRCI(Instruction):
    pass


@isa("lwu", opcode=0b0000011, funct3=0b110, variant=RV64I)
class InstructionLWU(InstructionIType):
    pass


@isa("ld", opcode=0b0000011, funct3=0b011, variant=RV64I)
class InstructionLD(InstructionIType):
    pass


@isa("sd", opcode=0b0100011, funct3=0b011, variant=RV64I)
class InstructionSD(InstructionISType):
    pass


@isa_pseudo()
class InstructionNOP(InstructionADDI):
    def __init__(self):
        super().__init__(0, 0, 0)
    def __str__(self):
        return "nop"

@isaC("c.addi", 1, funct3=0b000)
class InstructionCADDI(InstructionCIType):
    def expand(self):
        pass

    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rd] + self.imm


@isaC("c.andi", 1, funct3=0b100)
class InstructionCANDI(InstructionCBType):
    def expand(self):
        pass


@isaC("c.swsp", 2, funct3=6)
class InstructionCSWSP(InstructionCSSType):
    def expand(self):
        pass

    def decode(self, machinecode: int):
        self.rs = (machinecode >> 2) & 0x1f
        imm12to9 = (machinecode >> 9) & 0xf
        imm8to7 = (machinecode >> 7) & 0x3
        self.imm.set_from_bits((imm8to7 << 4) | imm12to9)

    def execute(self, model: State):
        pass

@isaC("c.li", 1, funct3=2)
class InstructionCLI(InstructionCIType):
    def expand(self):
        pass

    def execute(self, model: State):
        model.intreg[self.rd] = self.imm


@isaC("c.mv", 2, funct4=8)
class InstructionCMV(InstructionCRType):
    def expand(self):
        pass

    def execute(self, model: State):
        model.intreg[self.rd] = model.intreg[self.rs]
