import random
import argparse
import sys
from tempfile import mkstemp
import subprocess

from .variant import Variant, VariantRV32I
from .isa import *
from . import __version__


def random_instruction(variant: Variant, pool = None):
    if pool is None:
        pool = get_insns(Instruction)

    while True:
        c = random.choice(pool)
        i = c()
        i.randomize(variant)
        yield i

def random_asm(N, pool=None):
    v = VariantRV32I()
    for i in range(N):
        yield next(random_instruction(v, pool=pool))


def gen_asm(argv=None):
    parser = argparse.ArgumentParser(description='Generate sequence of assembler instructions.')
    parser.add_argument('N', nargs='?', default=10, type=int, help='Number of assembler instructions')
    parser.add_argument('-i', action='append', type=str, choices=get_mnenomics(), help='Restrict to instructions')
    parser.add_argument('--version', help='Display version', action='version', version=__version__)

    if argv is None:
        argv = sys.argv[1:]
    args = parser.parse_args(argv)

    if args.i is None:
        args.i = get_mnenomics()

    pool = [reverse_lookup(m) for m in args.i]

    for asm in random_asm(args.N, pool=pool):
        print(asm)

def check_asm_run(N, pool, compiler):
    print("Check {} instructions from {}".format(N, [i._mnemonic for i in pool]))

    temp = mkstemp(suffix='.S')
    tempout = mkstemp(suffix='.o')
    f = open(temp[1], "w")
    for a in random_asm(N, pool):
        f.write("{}\n".format(str(a)))
    f.close()

    subprocess.call([compiler, '-o', tempout[1], '-c', temp[1]])


def check_asm(argv=None):
    parser = argparse.ArgumentParser(description='Automatically test if sequences of assembler instructions compile.')
    parser.add_argument('N', nargs='?', default=100, type=int, help='Number of assembler instructions')
    parser.add_argument('-i', action='append', type=str, choices=get_mnenomics(), help='Restrict to instructions')
    parser.add_argument('-s', action='store_true', default=False, help='Test each mnemonic individually')
    parser.add_argument('-c', type=str, default="riscv32-unknown-elf-gcc", help='Compiler executable')
    parser.add_argument('--version', help='Display version', action='version', version=__version__)

    if argv is None:
        argv = sys.argv[1:]
    args = parser.parse_args(argv)

    if args.i is None:
        args.i = get_mnenomics()

    pool = [reverse_lookup(m) for m in args.i]

    if (args.s):
        for i in pool:
            check_asm_run(args.N, [i], args.c)
    else:
        check_asm_run(args.N, pool, args.c)

if __name__ == "__main__":
    if sys.argv[1] == "random_asm":
        gen_asm(sys.argv[2:])
    elif sys.argv[1] == "check_asm":
        check_asm(sys.argv[2:])
