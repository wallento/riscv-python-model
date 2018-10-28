
class Variant(object):
    def __init__(self):
        self.intregs = None
        self.xlen = None


class BaseRV32I(Variant):
    def __init__(self):
        super(BaseRV32I, self).__init__()
        self.intregs = 32
        self.xlen = 32


class BaseRV32E(Variant):
    def __init__(self):
        super().__init__()
        self.intregs = 16
        self.xlen = 32


class BaseRV64I(Variant):
    def __init__(self):
        super().__init__()
        self.intregs = 32
        self.xlen = 64

