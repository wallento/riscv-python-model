import random
import argparse
import sys
from tempfile import mkstemp
import subprocess

from .isa import *
from .insn import get_insns
from .variant import Variant, RV32I
from .code import read_from_binary
from .model import Model
from . import __version__


def random_instruction(variant: Variant, pool = None):
    if pool is None:
        pool = get_insns()

    while True:
        c = random.choice(pool)
        i = c()
        i.randomize(variant)
        yield i


def random_asm(N, pool=None):
    v = RV32I
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

def check_asm_run(N, pool, compiler, objcopy):
    print("Check {} instructions from {}".format(N, [i._mnemonic for i in pool]))

    scoreboard = []

    asm = mkstemp(suffix='.S')
    objfile = mkstemp(suffix='.o')
    f = open(asm[1], "w")
    for a in random_asm(N, pool):
        scoreboard.append(a)
        f.write("{}\n".format(str(a)))
    f.close()

    subprocess.call([compiler, '-o', objfile[1], '-c', asm[1]])

    binfile = mkstemp(suffix='.bin')
    subprocess.call([objcopy, '-O', 'binary', objfile[1], binfile[1]])

    j = 0
    for i in read_from_binary(binfile[1]):
        if str(i) != str(scoreboard[j]):
            print("Check failed: {} {}".format(N, [i._mnemonic for i in pool]))
            print("{} != {}".format(i, scoreboard[j]))
            return

        j += 1
    print("Check passed: {} {}".format(N, [i._mnemonic for i in pool]))


def check_asm(argv=None):
    parser = argparse.ArgumentParser(description='Automatically test if sequences of assembler instructions compile.')
    parser.add_argument('N', nargs='?', default=100, type=int, help='Number of assembler instructions')
    parser.add_argument('-i', action='append', type=str, choices=get_mnenomics(), help='Restrict to instructions')
    parser.add_argument('-s', action='store_true', default=False, help='Test each mnemonic individually')
    parser.add_argument('--cc', type=str, default="riscv32-unknown-elf-gcc", help='Compiler executable')
    parser.add_argument('--objcopy', type=str, default="riscv32-unknown-elf-objcopy", help='objcopy executable')
    parser.add_argument('--version', help='Display version', action='version', version=__version__)

    if argv is None:
        argv = sys.argv[1:]
    args = parser.parse_args(argv)

    if args.i is None:
        args.i = get_mnenomics()

    pool = [reverse_lookup(m) for m in args.i]

    if (args.s):
        for i in pool:
            check_asm_run(args.N, [i], args.cc, args.objcopy)
    else:
        check_asm_run(args.N, pool, args.cc, args.objcopy)


if __name__ == "__main__":
    if sys.argv[1] == "random_asm":
        gen_asm(sys.argv[2:])
    elif sys.argv[1] == "check_asm":
        check_asm(sys.argv[2:])
