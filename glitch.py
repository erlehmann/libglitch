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

class RingBufferStack(deque):
    def __init__(self, size):
        deque.__init__(self)
        self.extend([0] * size)

        self.CHARMAP = {
        'b': self.OP_PUT,
        'c': self.OP_DROP,
        'd': self.OP_MUL,
        'e': self.OP_DIV,
        'f': self.OP_ADD,
        'g': self.OP_SUB,
        'h': self.OP_MOD,
        'i': self.OP_NEG,
        'j': self.OP_LSHIFT,
        'k': self.OP_RSHIFT,
        'l': self.OP_AND,
        'm': self.OP_OR,
        'n': self.OP_XOR,
        'o': self.OP_NOT,
        'p': self.OP_DUP,
        'q': self.OP_GET,
        'r': self.OP_SWAP,
        's': self.OP_LT,
        't': self.OP_GT,
        'u': self.OP_EQ,
        }

    def OP_POP(self):
        self.rotate(1)

    def OP_PUT(self):
        a = self[-1] % 256
        self[-a-1] = self[-2]
        self.rotate(1)

    def OP_DROP(self):
        self.rotate(-1)

    def OP_MUL(self):
        a = self[-1]
        b = self[-2]
        self.rotate(2)
        self.append(b * a)
        self.popleft()

    def OP_DIV(self):
        a = self[-1]
        b = self[-2]
        self.rotate(2)
        try:
            self.append(b / a)
        except ZeroDivisionError:
            self.append(0)
        self.popleft()

    def OP_ADD(self):
        a = self[-1]
        b = self[-2]
        self.rotate(2)
        self.append(b + a)
        self.popleft()

    def OP_SUB(self):
        a = self[-1]
        b = self[-2]
        self.rotate(2)
        self.append(b - a)
        self.popleft()

    def OP_MOD(self):
        a = self[-1]
        b = self[-2]
        self.rotate(2)
        try:
            self.append(b % a)
        except ZeroDivisionError:
            self.append(0)
        self.popleft()
        return self

    def OP_NEG(self):
        a = self[-1]
        self[-1] = -a

    def OP_LSHIFT(self):
        a = self[-1]
        b = self[-2]
        self.rotate(2)
        self.append(b << a)
        self.popleft()

    def OP_RSHIFT(self):
        a = self[-1]
        b = self[-2]
        self.rotate(2)
        self.append(b >> a)
        self.popleft()

    def OP_AND(self):
        a = self[-1]
        b = self[-2]
        self.rotate(2)
        self.append(b & a)
        self.popleft()
        return self

    def OP_OR(self):
        a = self.pop()
        b = self.pop()
        self.rotate(2)
        self.append(b | a)
        self.popleft()

    def OP_XOR(self):
        a = self.pop()
        b = self.pop()
        self.rotate(2)
        self.append(b ^ a)
        self.popleft()

    def OP_NOT(self):
        a = self[-1]
        self[-1] = (~a)

    def OP_DUP(self):
        a = self[-1]
        self.append(a)
        self.popleft()

    def OP_GET(self):
        a = self[-1] % 256
        b = self[-a-1]
        self.rotate(1)
        self.append(b)
        self.popleft()

    def OP_SWAP(self):
        a = self[-1]
        b = self[-2]
        self[-2] = a
        self[-1] = b
        return self

    def OP_LT(self):
        a = self[-1]
        b = self[-2]
        self.rotate(2)
        if (b < a):
            self.append(0xFFFFFFFF)
        else:
            self.append(0)
        self.popleft()
        return self


    def OP_GT(self):
        a = self[-1]
        b = self[-2]
        self.rotate(2)
        if (b > a):
            self.append(0xFFFFFFFF)
        else:
            self.append(0)
        self.popleft()
        return self

    def OP_EQ(self):
        a = self[-1]
        b = self[-2]
        if (b == a):
            self.append(0xFFFFFFFF)
        else:
            self.append(0)
        self.popleft()
        return self

    def tolist(self):
        return list(self)


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
        self.stack = RingBufferStack(256)

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

    def _compute_(self, t):
        for token in self.tokens:
            if not token in OPCODES:  # not an opcode, must be a number
                self.stack.append((int(token, 16)))
                self.stack.popleft()
            elif (token == '.'):  # NOP
                pass
            elif (token == 'a'):  # OP_T
                self.stack.append(t)
                self.stack.popleft()
            else:
                try:
                    self.stack.CHARMAP[token]()
                except KeyError:
                    stderr.write(token + ' not implemented, ignored.\n')

        result = self.stack[-1]
        self.stack.OP_POP()
        return result & 0xFF 

