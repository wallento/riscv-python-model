
class Variant(object):
    def __init__(self):
        self.intregs = None


class VariantRV32I(Variant):
    def __init__(self):
        super(VariantRV32I, self).__init__()
        self.intregs = 32