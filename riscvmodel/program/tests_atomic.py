from riscvmodel.isa import *
from riscvmodel.insn import *
from riscvmodel.regnames import *
from riscvmodel.program import Program


class LRSCTest(Program):
    """Basic test of LR & SC instructions"""
    def __init__(self):
        super().__init__([
            # Perform load-reserved and acquire lock
            InstructionLR(rs1=x0, rd=x1, aq=1, rl=0),
            # Perform store-conditional and release lock (should succeed)
            InstructionSC(rs1=x0, rs2=x0, rd=x2, aq=0, rl=1),
            # Perform second store-conditional to same address (should fail)
            InstructionSC(rs1=x0, rs2=x0, rd=x3, aq=0, rl=1),
        ])

    def expects(self) -> dict:
        return {
            x0: 0,
            x2: 0, # Due to successful SC (2nd instruction)
            x3: 1, # Due to failed SC (3rd instruction)
        }

