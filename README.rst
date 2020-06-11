RISC-V Model
============

This is a python model of the RISC-V ISA. It is intended to be a resource for Python-based automated testing and verification.
It is under development and not very useful yet, but can be used to generate random assembler code.

Documentation: https://riscv-python-model.readthedocs.io/en/latest/

Quick Start
-----------

First install it:

::

    pip3 install riscv-model

Create random assembler sequences
`````````````````````````````````

Create a random assembler sequence:

::

    riscv-random-asm

You can tweak the assembler output:

::

    usage: riscv-random-asm [-h]
                            [-i {add,sub,sll,slt,sltu,xor,srl,sra,or,and,jalr,addi,slti,sltiu,xori,ori,andi,lb,lh,lw,lbu,lhu,slli,srli,srai,sb,sh,sw,beq,bne,blt,bge,bltu,bgeu,lui,auipc,jal}]
                            [--version]
                            [N]

    Generate sequence of assembler instructions.

    positional arguments:
      N                     Number of assembler instructions

    optional arguments:
      -h, --help            show this help message and exit
      -i {add,sub,sll,slt,sltu,xor,srl,sra,or,and,jalr,addi,slti,sltiu,xori,ori,andi,lb,lh,lw,lbu,lhu,slli,srli,srai,sb,sh,sw,beq,bne,blt,bge,bltu,bgeu,lui,auipc,jal}
                            Restrict to instructions
      --version             Display version

For example to generate 100 assembler instructions only with ``add``, ``or`` and ``slti`` instructions:

::

    riscv-random-asm 100 -i add -i or -i slti

Disassemble machine code
````````````````````````

You can disassemble a machine code to the assembly code on instruction level:

::

    riscv-machinsn-decode hexstring 0x007938b3 0xc9650993

You can also directly disassemble object files:

::

    riscv-machinsn-decode objfile file.o


Automatically test random assembler sequences
`````````````````````````````````````````````

``riscv-random-asm-check`` generates random assembler sequences, compiles them, reads back the machine codes and matches them.
You can use that to test your compiler, but it is also used as sanity check for riscv-model itself.

::

    riscv-random-asm-check

It will by default use ``riscv32-unknown-elf-gcc`` and ``riscv32-unknown-elf-objcopy``, but you can configure the tools with ``--compiler`` and ``--objcopy``.

The automated tests will test all instructions, you can again restrict the number of instructions and the instructions:

::

    riscv-random-asm-check 1000 -i xor

Finally, you can run the checks for the individual instructions seperately (used in combination with the other options:

::

    riscv-random-asm-check -s
