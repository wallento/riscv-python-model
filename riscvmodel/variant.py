from collections import namedtuple

Extensions = namedtuple("Extensions",
                        ["M", "A", "F", "D", "Q", "C"])
Extensions.__new__.__defaults__ = (False,) * len(Extensions._fields)

Variant = namedtuple("Variant",
                     ["intregs", "xlen", "extensions"])

RV32I = Variant(intregs=32, xlen=32, extensions = Extensions())
RV32E = Variant(intregs=16, xlen=32, extensions = Extensions())
RV32IC = Variant(intregs=32, xlen=32, extensions = Extensions(C=True))
RV32IM = Variant(intregs=32, xlen=32, extensions = Extensions(M=True))
RV32IMC = Variant(intregs=32, xlen=32, extensions = Extensions(M=True, C=True))
RV32IMAFD = Variant(intregs=32, xlen=32, extensions = Extensions(M=True, A=True, F=True, D=True))
RV32G = RV32IMAFD
RV32IMAFDC = Variant(intregs=32, xlen=32, extensions = Extensions(M=True, A=True, F=True, D=True, C=True))
RV32GC = RV32IMAFDC

RV64I = Variant(intregs=32, xlen=64, extensions = Extensions())
RV64IC = Variant(intregs=32, xlen=64, extensions = Extensions(C=True))
RV64IM = Variant(intregs=32, xlen=64, extensions = Extensions(M=True))
RV64IMC = Variant(intregs=32, xlen=64, extensions = Extensions(M=True, C=True))
RV64IMAFD = Variant(intregs=32, xlen=64, extensions = Extensions(M=True, A=True, F=True, D=True))
RV64G = RV64IMAFD
RV64IMAFDC = Variant(intregs=32, xlen=64, extensions = Extensions(M=True, A=True, F=True, D=True, C=True))
RV64GC = RV64IMAFDC
