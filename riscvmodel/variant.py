# Copyright Stefan Wallentowitz
# Licensed under the MIT License, see LICENSE for details.
# SPDX-License-Identifier: MIT
'''
TODO: Description
'''

import argparse
import re
from collections import namedtuple

Extension = namedtuple("Extension", ["name", "description", "implies"])


class Variant:
    '''
    RISC-V ISA Variants
    '''
    stdext = {
        "M": Extension("M", "Integer Multiplication and Division", []),
        "A": Extension("A", "Atomics", []),
        "F": Extension("F", "Single-Precision Floating-Point", ["Zicsr"]),
        "D": Extension("D", "Double-Precision Floating-Point", ["F"]),
        "C": Extension("C", "16-bit Compressed Instructions", [])
    }
    stdextZ = {
        "Zicsr": Extension("Zicsr", "Control and Status Register Access", []),
        "Zifencei": Extension("Zifencei", "Instruction-Fetch Fence", [])
    }
    regex = re.compile(
        r"^RV(32|64|128)(I|E|G)({})*((?:(?:Z|X).+)(?:_(?:(?:Z|X).*))*)?$".
        format("|".join(list(stdext.keys()) + ["G"])))
    G_expand = ["I", "M", "A", "F", "D", "Zicsr", "Zifencei"]

    def __init__(self, name: str, *, custext=None):
        self.custext = {}
        for ext in custext or []:
            self.custext[ext.name] = ext
        self.name = name
        match = self.regex.match(name.upper())
        assert match, "Invalid variant string '{}'".format(name)
        self.extensions = set()
        self.xlen = int(match.group(1))
        self.baseint = match.group(2)
        if self.baseint == "G":
            self.extensions |= set(Variant.G_expand)
            self.baseint = "I"
        assert (self.baseint == "I"
                or self.xlen == 32), "E base integer is only valid for 32-bit"
        if match.group(3):
            for ext in match.group(3):
                if ext == "G":
                    assert (self.baseint == "I"), "G is not defined for I"
                    self.extensions |= set(Variant.G_expand)
                else:
                    self.extensions |= set([ext] + Variant.stdext[ext].implies)
        if match.group(4):
            for ext in match.group(4).split("_"):
                if ext[0] == "Z":
                    self.extensions |= set(
                        [ext] + Variant.stdextZ["Z" + ext[1:].lower()].implies)
                elif ext[0] == "X":
                    self.extensions |= set(
                        [ext] + self.custext["X" + ext[1:].lower()].implies)

    def __str__(self):
        return self.name

    def describe(self):
        '''
        Describe what this RISC-V ISA Variant defines
        '''
        desc = self.name + "\n"
        desc += "  XLEN={}, {} integer registers ({})\n".format(
            self.xlen, "16" if self.baseint == "E" else "32", self.baseint)
        desc += "  Extensions:\n"
        if len(self.extensions) == 0:
            desc += "    None\n"
        else:
            for entry in sorted(self.extensions):
                ext = None
                if entry in Variant.stdext:
                    ext = Variant.stdext[entry]
                elif "Z" + entry[1:].lower() in Variant.stdextZ:
                    ext = Variant.stdextZ["Z" + entry[1:].lower()]
                elif "X" + entry[1:].lower() in self.custext:
                    ext = self.custext["X" + entry[1:].lower()]
                assert ext, "Cannot find extension {}".format(entry)
                desc += "    {:8} {}\n".format(ext.name, ext.description)
        return desc

    def __eq__(self, other):
        '''
        Check if two Variants are equal
        '''
        return (self.xlen == other.xlen and self.baseint == other.baseint
                and self.extensions == other.extensions)

    def __le__(self, other):
        '''
        Check if Variant is a subset of another
        '''
        return (self.xlen == other.xlen and self.baseint == other.baseint
                and self.extensions <= other.extensions)

    def __add__(self, other):
        '''
        Add extensions to a Variant
        '''
        if isinstance(other, str):
            self.extensions.add(other)
        else:
            if isinstance(other, Extension):
                other = [other]
            assert isinstance(other,
                              list), "Requires Extension or list of Extension"
            for ext in other:
                self.custext[ext.name] = ext
                self.extensions.add(ext.name)
                for i in ext.implies:
                    self.extensions.add(i)
        return self


# Convenience
RV32I = Variant("RV32I")
RV32E = Variant("RV32E")
RV32IZicsr = Variant("RV32IZicsr")
RV32IM = Variant("RV32IM")
RV32IC = Variant("RV32IC")
RV64I = Variant("RV64I")
RV64G = Variant("RV64G")
RV64GC = Variant("RV64GC")
RV128I = Variant("RV128I")


def describe_argparser():
    """
    Return an argument parser for the describe function
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("variant", help="Variant to describe, example: RV64GC")
    return parser


def describe():
    '''
    Function called by command line tool

    Describe a RISC-V ISA Variant based on the name
    '''
    parser = describe_argparser()
    args = parser.parse_args()
    variant = Variant(args.variant)

    print(variant.describe())
