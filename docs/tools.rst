Command line tools and utilities
--------------------------------

A couple of command line tools and utilities help you working with RISC-V and
can serve as entry point for extending this package.

Discover RISC-V ISA Variants: ``riscv-describe-isa-variant``
************************************************************

.. argparse::
   :module: riscvmodel.variant
   :func: describe_argparser
   :prog: riscv-describe-isa-variant

    Describe a RISC-V ISA variant in a human-readable way.

Usage Example:

.. code:: console

    $ riscv-describe-isa-variant RV64GC
    RV64GC
    XLEN=64, 32 integer registers (I)
    Extensions:
        A        Atomics
        C        16-bit Compressed Instructions
        D        Double-Precision Floating-Point
        F        Single-Precision Floating-Point
        M        Integer Multiplication and Division
        Zicsr    Control and Status Register Access
        Zifencei Instruction-Fetch Fence

Generate a random instruction stream: ``riscv-random-asm``
**********************************************************

.. argparse::
   :module: riscvmodel.random
   :func: gen_asm_parser
   :prog: riscv-random-asm

    Generate a stream of random RISC-V instructions. Those sequences are valid
    instruction but not necessarily valid programs, in particular they don't
    have actual control flow.

Usage Example to generate 2 random RV32I instructions:

.. code:: console

    $ riscv-random-asm -v RV32I 2
    sb x30, 943(x1)
    sra x0, x7, x7

Or restrict to one particular instruction:

.. code:: console

    $ riscv-random-asm -i or 5
    or x0, x12, x11
    or x13, x18, x0
    or x8, x10, x30
    or x2, x4, x2
    or x0, x2, x27
