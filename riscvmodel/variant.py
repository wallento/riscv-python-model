from collections import namedtuple

Extensions = namedtuple("Extensions",
                        ["M", "A", "F", "D", "Q", "C"])
Extensions.__new__.__defaults__ = (False,) * len(Extensions._fields)

Variant = namedtuple("Variant",
                     ["intregs", "xlen", "extensions"])

RV32I = Variant(intregs=32, xlen=32, extensions = Extensions())
RV32E = Variant(intregs=16, xlen=32, extensions = Extensions())
RV32IC = Variant(intregs=32, xlen=32, extensions = Extensions(C=True))

