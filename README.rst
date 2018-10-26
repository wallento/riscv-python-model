RISC-V Model
============

This is a python model of the RISC-V ISA. It is intended to be a resource for Python-based automated testing and verification.
It is under development and not very useful yet, but can be used to generate random assembler code.

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

Automatically test random assembler sequences
`````````````````````````````````````````````

You can directly test those sequences with your compiler:

::

    riscv-random-asm-check

It will by default use ``riscv32-unknown-elf-gcc``, but you can configure the tool with ``-c``, for example:

::

    riscv-random-asm-check -c clang

The automated tests will test all instructions, you can again restrict the number of instructions and the instructions:

::

    riscv-random-asm-check 1000 -i xor

Finally, you can run the checks for the individual instructions seperately (used in combination with the other options:

::

    riscv-random-asm-check -s


Disassemble machine code
````````````````````````

You can disassemble a machine code to the assembly code on instruction level:

::

    riscv-machinsn-decode 0x007938b3
    riscv-machinsn-decode 0xc9650993
