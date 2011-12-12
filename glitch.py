#!/usr/bin/python
# -*- coding: utf-8 -*-

#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from sys import stderr
from collections import deque

OPCODES = '.abcdefghijklmnopqrstuvwxyzGHIJKLMNOPQRSTUVWXYZ'
HEXDIGITS = '0123456789ABCDEF'
MAXINT = 0xFFFFFFFF

class Melody:
    def __init__(self, melody):
        """
        A Melody consists of lines signifying opcodes and hexadecimal numbers.
        [a-z] and [G-Z] denote opcodes, while [1-9] and [A-F] denote numbers.
        """

        assert(type(melody) == str)

        self.lines = melody.split('!')
        self.title = self.lines[0]
        self.tokens = self._tokenize_(self.lines[1:])
        self._reset_()

    def __repr__(self):
        lines = []
        for i in range(len(self.lines)):  # Strips NOPs from end of lines for readability.
            lines.append(self.lines[i].strip('.'))

        leadchar = ''
        if not self.title:
            leadchar = '!'
        return leadchar + '!'.join(lines).strip('!')

    def _reset_(self):
        self.stack = deque([0] * 256)

    def _tokenize_(self, lines):
        tokens = []

        for line in lines:
            assert(len(line) <= 16)  # only 16 characters per line allowed
            for char in line:
                try:
                    if (char in HEXDIGITS) and (
                        (tokens[-1] in HEXDIGITS) or
                        (tokens[-1][-1] in HEXDIGITS)
                    ):
                        tokens[-1] += char
                    else:
                        tokens.append(char)
                except IndexError:  # first character is HEXDIGIT
                    tokens.append(char)

        return tokens

    def _expand_(self, lines):
        """
            Appends NOPs to eight lines for easy editing.
        """
        for i in range(9):
            try:
                self.lines[i] = (self.lines[i] + (16*'.'))[:16]
            except IndexError:
                self.lines.append(16*'.')

    def _compute_(self, t, count=1):
        stack = self.stack
        for token in self.tokens:
            if not token in OPCODES:  # not an opcode, must be a number
                stack.append((int(token, 16)))
                stack.popleft()

            elif (token == '.'):  # NOP
                pass

            elif (token == 'a'):  # OP_T
                stack.append(t & MAXINT)
                stack.popleft()

            elif (token == 'b'):  # OP_PUT
                a = stack[-1] % 256
                stack[-a-1] = stack[-2]
                stack.rotate(1)

            elif (token == 'c'):  # OP_DROP
                stack.rotate(1)

            elif (token == 'd'):  # OP_MUL
                a = stack.pop()
                b = stack[-1]
                stack.rotate(1)
                stack.append((b * a) & MAXINT)

            elif (token == 'e'):  # OP_DIV
                a = stack.pop()
                b = stack[-1]
                stack.rotate(1)
                try:
                    stack.append((b / a) & MAXINT)
                except ZeroDivisionError:
                    stack.append(0)

            elif (token == 'f'):  # OP_ADD
                a = stack.pop()
                b = stack[-1]
                stack.rotate(1)
                stack.append((b + a) & MAXINT)

            elif (token == 'g'):  # OP_SUB
                a = stack.pop()
                b = stack[-1]
                stack.rotate(1)
                stack.append((b - a) & MAXINT)

            elif (token == 'h'):  # OP_MOD
                a = stack.pop()
                b = stack[-1]
                stack.rotate(1)
                try:
                    stack.append((b % a) & MAXINT)
                except ZeroDivisionError:
                    stack.append(0)

            elif (token == 'j'):  # OP_LSHIFT
                a = stack.pop()
                b = stack[-1]
                stack.rotate(1)
                stack.append((b << a) & MAXINT)

            elif (token == 'k'):  # OP_RSHIFT
                a = stack.pop()
                b = stack[-1]
                stack.rotate(1)
                stack.append((b >> a) & MAXINT)

            elif (token == 'l'):  # OP_AND
                a = stack.pop()
                b = stack[-1]
                stack.rotate(1)
                stack.append((b & a) & MAXINT)

            elif (token == 'm'):  # OP_OR
                a = stack.pop()
                b = stack[-1]
                stack.rotate(1)
                stack.append((b | a) & MAXINT)

            elif (token == 'n'):  # OP_XOR
                a = stack.pop()
                b = stack[-1]
                stack.rotate(1)
                stack.append((b ^ a) & MAXINT)

            elif (token == 'o'):  # OP_NOT
                stack[-1] = (~stack[-1] & MAXINT)

            elif (token == 'p'):  # OP_DUP
                stack.append(stack[-1])
                stack.popleft()

            elif (token == 'q'):  # OP_PICK
                # 0 OP_PICK is equivalent to OP_DUP
                # 0xFF OP_PICK is equivalent to 0xFF
                a = stack[-1]
                stack[-1] = stack[-((a-254) % 256)]

            elif (token == 'r'):  # OP_SWAP
                stack[-1], stack[-2] = stack[-2], stack[-1]

            elif (token == 's'):  # OP_LT
                a = stack.pop()
                b = stack[-1]
                stack.rotate(1)
                if (b < a):
                    stack.append(MAXINT)
                else:
                    stack.append(0)

            elif (token == 't'):  # OP_GT
                a = stack.pop()
                b = stack[-1]
                stack.rotate(1)
                if (b > a):
                    stack.append(MAXINT)
                else:
                    stack.append(0)

            elif (token == 'u'):  # OP_EQ
                a = stack.pop()
                b = stack[-1]
                stack.rotate(1)
                if (b == a):
                    stack.append(MAXINT)
                else:
                    stack.append(0)

        result = stack[-1]
        stack.rotate(1)  # implied OP_DROP
        return result & 0xFF 

