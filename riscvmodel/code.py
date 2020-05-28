import argparse
from tempfile import mkstemp
import subprocess

from .isa import *
from . import __version__

class MachineDecodeError(Exception):
    pass

def decode(machinecode: int):
    if machinecode & 0x3 != 3:
        # compact
        for icls in get_insns(cls=InstructionCType):
            if icls._match(machinecode):
                i = icls()
                i.decode(machinecode)
                return i
        raise MachineDecodeError("Cannot decode {:04x}".format(machinecode))
    opcode = machinecode & 0x7F
    for icls in get_insns():
        if icls._opcode == opcode and icls._match(machinecode):
            i = icls()
            i.decode(machinecode)
            return i
    raise MachineDecodeError()


def read_from_binary(fname: str):
    with open(fname, "rb") as f:
        insn = f.read(4)
        while insn:
            yield decode(int.from_bytes(insn, 'little'))
            insn = f.read(4)

def machinsn_decode():
    parser = argparse.ArgumentParser(description='Disassemble a machine instruction.')
    parser.add_argument('--version', help='Display version', action='version', version=__version__)
    subparsers = parser.add_subparsers()
    parser_cmdline = subparsers.add_parser('hexstring', help='From commandline hexstrings')
    parser_cmdline.add_argument('insn', type=str, nargs='+', help='Instruction(s) as hexstring (0x...)')
    parser_file = subparsers.add_parser('objfile', help='Read from object file')
    parser_file.add_argument('filename', type=str, help='Filename')
    parser.add_argument('--objcopy', type=str, default="riscv32-unknown-elf-objcopy", help='objcopy executable')
    args = parser.parse_args()

    if "insn" in args:
        for i in args.insn:
            try:
                print(decode(int(i,16)))
            except MachineDecodeError:
                print("Cannot decode {:08x}, invalid instruction".format(int(i,16)))
    elif "filename" in args:
        temp = mkstemp(suffix='.bin')
        subprocess.call([args.objcopy, '-O', 'binary', args.filename, temp[1]])

        for i in read_from_binary(temp[1]):
            print(i)
    else:
        parser.print_help()
