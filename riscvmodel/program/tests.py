from riscvmodel.isa import *
from riscvmodel.regnames import *
from riscvmodel.program import Program


class LUITest(Program):
    """Basic test of LUI instruction"""
    def __init__(self):
        insns = [
            InstructionLUI(x1, 0),
            InstructionLUI(x2, 1),
            InstructionLUI(x3, 0x80000),
            InstructionLUI(x4, 0xfffff),
            InstructionLUI(x0, 0xfffff),
        ]
        super().__init__(insns)
    def expects(self) -> dict:
        return {0: 0, 1: 0, 2: 1, 3: 0x80000000, 4: 0xfffff000}


class AUIPCTest(Program):
    """Basic test of AUIPC instruction"""
    def __init__(self):
        insns = [
            InstructionAUIPC(x1, 0),
            InstructionAUIPC(x2, 1),
            InstructionAUIPC(x3, 0x80000),
            InstructionAUIPC(x4, 0xfffff),
            InstructionAUIPC(x0, 0xfffff),
        ]
        super().__init__(insns)


class ADDITest(Program):
    """Basic test of ADDI instruction"""
    def __init__(self):
        insns = [
            InstructionADDI(x1, x0, x0),
            InstructionADDI(x1, x1, 1),
            InstructionADDI(x2, x1, -2),
        ]
        super().__init__(insns)

    def expects(self) -> dict:
        return {1: 1, 2: 0xFFFFFFFF}


class SLTITest(Program):
    """Basic test of SLTI instruction"""
    def __init__(self):
        insns = [
            InstructionSLTI(x1, x0, 0),  # x1=0
            InstructionSLTI(x2, x1, 0),  # x2=0
            InstructionSLTI(x3, x0, 1),  # x3=1
            InstructionSLTI(x4, x3, 1),  # x4=0
            InstructionLUI(x5, 0x80000),
            InstructionSLTI(x6, x5, 0),  # x6=1
        ]
        super().__init__(insns)


class SLTIUTest(Program):
    """Basic test of SLTIU instruction"""
    def __init__(self):
        insns = [
            InstructionSLTIU(x1, x0, 0),
            InstructionSLTIU(x2, x1, 0),
            InstructionSLTIU(x3, x0, 1),
            InstructionSLTIU(x4, x3, 1),
            InstructionLUI(x5, 0x80000),
            InstructionSLTIU(x6, x5, 0),
        ]
        super().__init__(insns)


class XORITest(Program):
    """Basic test of XORI instruction"""
    def __init__(self):
        insns = [
            InstructionXORI(x1, x0, 0x7ff),
            InstructionXORI(x2, x1, 0x001),
            InstructionXORI(x3, x0, -0x800),
        ]
        super().__init__(insns)


class ORITest(Program):
    """Basic test of ORI instruction"""
    def __init__(self):
        insns = [
            InstructionORI(x1, x0, 0x7ff),
            InstructionORI(x2, x1, 0x001),
            InstructionORI(x3, x0, -0x800),
        ]
        super().__init__(insns)


class ANDITest(Program):
    """Basic test of ANDI instruction"""
    def __init__(self):
        insns = [
            InstructionANDI(x1, x0, 0x7ff),
            InstructionANDI(x2, x1, 0x001),
            InstructionANDI(x3, x0, -0x800),
        ]
        super().__init__(insns)


class SLLITest(Program):
    """Basic test of SLLI instruction"""
    def __init__(self):
        insns = [
            InstructionLUI(x1, 0xfebed),
            InstructionSLLI(x2, x1, 12),
            InstructionSLLI(x3, x1, 2),
            InstructionSLLI(x4, x3, 10),
        ]
        super().__init__(insns)


class SRLITest(Program):
    """Basic test of SRLI instruction"""
    def __init__(self):
        insns = [
            InstructionLUI(x1, 0xfebed),
            InstructionSRLI(x2, x1, 12),
            InstructionSRLI(x3, x1, 2),
            InstructionSRLI(x4, x3, 10),
        ]
        super().__init__(insns)


class SRAITest(Program):
    """Basic test of SRAI instruction"""
    def __init__(self):
        insns = [
            InstructionLUI(x1, 0xfebed),
            InstructionSRAI(x2, x1, 12),
            InstructionSRAI(x3, x1, 2),
            InstructionSRAI(x4, x3, 10),
        ]
        super().__init__(insns)


class ADDTest(Program):
    """Basic test of ADD instruction"""
    def __init__(self):
        insns = [
            InstructionLUI(x1, 0xfebed),
            InstructionADD(x2, x0, x1),
            InstructionADD(x3, x1, x1),
        ]
        super().__init__(insns)


class SUBTest(Program):
    """Basic test of SUB instruction"""
    def __init__(self):
        insns = [
            InstructionLUI(x1, 0xfebed),
            InstructionSUB(x2, x0, x1),
            InstructionSUB(x3, x1, x1),
        ]
        super().__init__(insns)


class SLLTest(Program):
    """Basic test of SLL instruction"""
    def __init__(self):
        insns = [
            InstructionLUI(x1, 0xfebed),
            InstructionSLL(x2, x1, x1),
            InstructionORI(x3, x0, 7),
            InstructionSLL(x4, x1, x3),
        ]
        super().__init__(insns)


class SLTTest(Program):
    """Basic test of SLT instruction"""
    def __init__(self):
        insns = [
        ]
        super().__init__(insns)


class SLTUTest(Program):
    """Basic test of SLTU instruction"""
    def __init__(self):
        insns = [
        ]
        super().__init__(insns)


class XORTest(Program):
    """Basic test of XOR instruction"""
    def __init__(self):
        insns = [
        ]
        super().__init__(insns)


class SRLTest(Program):
    """Basic test of SRL instruction"""
    def __init__(self):
        insns = [
        ]
        super().__init__(insns)


class SRATest(Program):
    """Basic test of SRA instruction"""
    def __init__(self):
        insns = [
        ]
        super().__init__(insns)


class ORTest(Program):
    """Basic test of OR instruction"""
    def __init__(self):
        insns = [
        ]
        super().__init__(insns)


class ANDTest(Program):
    """Basic test of AND instruction"""
    def __init__(self):
        insns = [
        ]
        super().__init__(insns)


RV32ITests = [LUITest, AUIPCTest, ADDITest, SLTITest, SLTIUTest, XORITest, ORITest, ANDITest, SLLITest, SRLITest,
              SRAITest, ADDTest, SUBTest, SLLTest, SLTTest, SLTUTest, XORTest, SRLTest, SRATest, ORTest, ANDTest]