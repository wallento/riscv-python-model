from riscvmodel.isa import *
from riscvmodel.regnames import *
from riscvmodel.program import Program


class ADDITest(Program):
    def __init__(self):
        insns = [
            InstructionADDI(x1, x0, x0),
            InstructionADDI(x1, x1, 1),
            InstructionADDI(x2, x1, -2),
        ]
        super().__init__(insns)

    def expects(self) -> dict:
        return {1: 1, 2: 0xFFFFFFFF}
