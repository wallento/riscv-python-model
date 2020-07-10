from .model import Model, Memory
from .isa import TerminateException

import struct

class Simulator:
  def __init__(self, model):
    self.model = model
    self.program = []

  def load_program(self, program, *, address=0):
    self.program = [i for i in program]

  def load_data(self, data = "", *, address=0):
    mem = self.model.state.memory.memory
    for a in range(int(len(data)/4)):
      mem[a] = struct.unpack("<L", data[a*4:(a+1)*4])[0]

  def run(self, *, pc=0):
    self.model.reset(pc=pc)
    cnt = 0
    while True:
      try:
        self.model.issue(self.program[int(self.model.state.pc)>>2])
        cnt += 1
      except TerminateException as exc:
        assert exc.returncode == 0
        return cnt
      except IndexError:
        return cnt
    return cnt

  def dump_data(self, *, address=0, size=None):
    data = b""
    mem = self.model.state.memory.memory
    for a in mem:
      if a >= address and (size is None or a < address + size):
        data += struct.pack("<L", mem[a])
    return data
