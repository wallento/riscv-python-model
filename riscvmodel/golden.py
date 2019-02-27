from abc import ABCMeta, abstractmethod
from collections import deque

from .variant import Variant
from .model import Model, Memory
from .isa import InstructionNOP
from .program import Program
from .types import RVFISignals, TraceIntegerRegister, Register
from .code import decode


class GoldenException(Exception):
    pass


class GoldenProgramEndException(Exception):
    pass


class Golden(metaclass=ABCMeta):
    def __init__(self, variant: Variant):
        self.model = Model(variant)
        self.memory = Memory()
        self.program = None

    @abstractmethod
    def fetch(self, pc):
        pass


class GoldenUnbuffered(Golden):
    def __init__(self, variant: Variant, *, pc: int = 0):
        super().__init__(variant)
        self.reset(pc=pc)

    def fetch(self, pc):
        if self.pc != pc:
            raise GoldenException("Unexpected fetch PC: {}, expected {}".format(pc, self.pc))
        try:
            insn = self.program[pc >> 2]
        except IndexError:
            raise GoldenProgramEndException()
        self.issued.append(insn)
        self.pc += 4
        return insn

    def commit(self, trace, *, insn = None):
        if not isinstance(trace, list):
            trace = [trace]

        # Test if any other exceptions are issued and get in order
        try:
            exp = self.issued.popleft()
        except IndexError:
            # If not we may be able to verify this is a NOP, then its okay. If no NOP, its probably okay too..
            if insn is not None:
                if insn != InstructionNOP():
                    raise GoldenProgramEndException()
            raise GoldenProgramEndException()

        # If we got an instruction check if it matches
        if insn is not None:
            if exp != insn:
                raise GoldenException("Expected instruction: {}, expected {}".format(insn, exp))

        # Execute the expected instruction and verify the state is the same
        exp_trace = self.model.issue(exp)
        if not self.model.check(trace):
            raise GoldenException("Unexpected state change: {}, expected: {}".format(",".join([str(t) for t in trace]),
                                                                                     ",".join([str(t) for t in exp_trace])))

    def reset(self, *, pc: int = 0):
        self.model.reset(pc=pc)
        self.pc = pc
        self.issued = deque()

    def load_program(self, pgm: Program):
        self.program = pgm.insns


def traces_from_rvfi(rvfi: RVFISignals) -> list:
    insn = decode(rvfi.insn)
    if rvfi.valid != 1:
        return []
    t = []
    if rvfi.rd_addr == 0 and rvfi.rd_wdata != 0:
        raise ValueError("rd[0] cannot be written by core")
    if rvfi.rd_addr != 0:
        if "rd" in insn.__dict__:
            reg = Register(32)
            reg.set(rvfi.rd_wdata)
            t.append(TraceIntegerRegister(rvfi.rd_addr, reg))

    return t