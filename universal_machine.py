"""
Author:
Tristan Garwood

This script was written to solve a coding challenge given to me by a potential employer. The goal of the challenge was
to implement the included um-spec.txt file and get the codex.umz bytecode file running. The UniversalMachine (UM) class
is a bytecode interpreter that interprets the language specified in the um-spec.txt file. After instantiating a UM
object by passing in the path to the codex, the codex can then be interpreted by calling the UM's public method:
interpret_program_scroll.

"""

import sys
from argparse import ArgumentParser


class UniversalMachine(object):
    def __init__(self, program_scroll_path):
        self._OPERATOR_NUMBER_MAP = [
            self._move,
            self._index,
            self._amend,
            self._add,
            self._mult,
            self._div,
            self._nand,
            self._halt,
            self._malloc,
            self._free,
            self._out,
            self._in,
            self._load,
            self._orth,
        ]

        self._scroll_list = [[platter for platter in self._read_scroll(program_scroll_path)]]

        self._register = [0] * 8

        self._free_mem = []

        self._platter_pointer = 0

    def _read_scroll(self, scroll_path):
        with open(scroll_path, 'rb') as scroll_f_in:
            while 1:
                current_platter = scroll_f_in.read(4)
                if current_platter == '':
                    break
                yield self._concat_bytes(
                    current_platter[0],
                    current_platter[1],
                    current_platter[2],
                    current_platter[3],
                )

    def _concat_bytes(self, a, b, c, d):
        return (ord(a) << 24) | (ord(b) << 16) | (ord(c) << 8) | ord(d)

    def interpret_program_scroll(self):
        while 1:
            current_platter = self._scroll_list[0][self._platter_pointer]
            self._platter_pointer += 1

            operator_num, register_nums = self._extract_platter_info(current_platter)

            self._OPERATOR_NUMBER_MAP[operator_num](*register_nums)

    def _extract_platter_info(self, platter):
        platter_bin = bin(platter)[2:]
        operator_num = platter >> 28

        if operator_num == 13:
            register_nums = [
                int(platter_bin[4:7], 2),
                int(platter_bin[7:], 2)
            ]
        else:
            register_nums = [
                int(platter_bin[-9:-6], 2),
                int(platter_bin[-6:-3], 2),
                int(platter_bin[-3:], 2)
            ]
        return operator_num, register_nums

    def _move(self, a, b, c):
        if self._register[c] != 0:
            self._register[a] = self._register[b]

    def _index(self, a, b, c):
        self._register[a] = self._scroll_list[self._register[b]][self._register[c]]

    def _amend(self, a, b, c):
        self._scroll_list[self._register[a]][self._register[b]] = self._register[c]

    def _add(self, a, b, c):
        self._register[a] = (self._register[b] + self._register[c]) & 0xFFFFFFFF

    def _mult(self, a, b, c):
        self._register[a] = (self._register[b] * self._register[c]) & 0xFFFFFFFF

    def _div(self, a, b, c):
        self._register[a] = (self._register[b] / self._register[c]) & 0xFFFFFFFF

    def _nand(self, a, b, c):
        self._register[a] = (~(self._register[b] & self._register[c])) & 0xFFFFFFFF

    def _halt(self, a, b, c):
        sys.exit('Halt operation executed.')

    def _malloc(self, a, b, c):
        if len(self._free_mem) > 0:
            scroll_num = self._free_mem.pop()
            self._scroll_list[scroll_num] = [0] * self._register[c]
            self._register[b] = scroll_num
        else:
            self._scroll_list.append([0] * self._register[c])
            self._register[b] = len(self._scroll_list) - 1

    def _free(self, a, b, c):
        self._scroll_list[self._register[c]] = []
        self._free_mem.append(self._register[c])

    def _out(self, a, b, c):
        char_out = chr(self._register[c])
        sys.stdout.write(chr(self._register[c]))
        if char_out == '\n':
            sys.stdout.flush()

    def _in(self, a, b, c):
        platter_in = sys.stdin.read(1)
        if platter_in == '':
            self._register[c] = 0xFFFFFFFF
        else:
            self._register[c] = ord(platter_in)

    def _load(self, a, b, c):
        if self._register[b] != 0:
            self._scroll_list[0] = list(self._scroll_list[self._register[b]])
        self._platter_pointer = self._register[c]

    def _orth(self, a, val):
        self._register[a] = val


if __name__ == '__main__':
    arg_parser = ArgumentParser()
    arg_parser.add_argument('codex', help='Path to program codex bytecode to be interpreted.', type=str)

    args = arg_parser.parse_args()

    um = UniversalMachine(args.codex)

    um.interpret_program_scroll()
