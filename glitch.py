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

def OP_PUSH(stack, value):  # used internally
    del stack[0]
    stack.append(value)
    return stack

def OP_DROP(stack):
    stack.pop()
    stack.appendleft(0)
    return stack

def OP_MUL(stack):
    a = stack.pop()
    b = stack.pop()
    stack.append(b * a)
    stack.appendleft(0)
    return stack

def OP_DIV(stack):
    a = stack.pop()
    b = stack.pop()
    try:
        stack.append(b / a)
    except ZeroDivisionError:
        stack.append(0)
    stack.appendleft(0)
    return stack

def OP_ADD(stack):
    a = stack.pop()
    b = stack.pop()
    stack.append(b + a)
    stack.appendleft(0)
    return stack

def OP_SUB(stack):
    a = stack.pop()
    b = stack.pop()
    stack.append(b - a)
    stack.appendleft(0)
    return stack

def OP_MOD(stack):
    a = stack.pop()
    b = stack.pop()
    try:
        stack.append(b % a)
    except ZeroDivisionError:
        stack.append(0)
    stack.appendleft(0)
    return stack

def OP_NEG(stack):
    a = stack.pop()
    stack.append(-a)
    return stack

def OP_LSHIFT(stack):
    a = stack.pop()
    b = stack.pop()
    try:
        stack.append(b << a)
        stack.appendleft(0)
    except ValueError:  # negative shift count
        stack = OP_RSHIFT(stack)
    return stack
    
def OP_RSHIFT(stack):
    a = stack.pop()
    b = stack.pop()
    try:
        stack.append(b >> a)
        stack.appendleft(0)
    except ValueError:  # negative shift count
        stack = OP_LSHIFT(stack)
    return stack
    
def OP_AND(stack):
    a = stack.pop()
    b = stack.pop()
    stack.append(b & a)
    stack.appendleft(0)
    return stack

def OP_OR(stack):
    a = stack.pop()
    b = stack.pop()
    stack.append(b | a)
    stack.appendleft(0)
    return stack

def OP_XOR(stack):
    a = stack.pop()
    b = stack.pop()
    stack.append(b ^ a)
    stack.appendleft(0)
    return stack

def OP_NOT(stack):
    a = stack.pop()
    stack.append(~a)
    return stack

def OP_DUP(stack):
    del stack[0]
    stack.append(stack[-1])
    return stack

def OP_GET(stack):
    a = stack[-1] % 256
    b = stack[-a-1]
    stack.pop()
    stack.append(b)
    return stack

def OP_SWAP(stack):
    a = stack.pop()
    b = stack.pop()
    stack.append(a)
    stack.append(b)
    return stack

def OP_LT(stack):
    a = stack.pop()
    b = stack.pop()
    if (b < a):
        stack.append(0xFFFFFFFF)
    else:
        stack.append(0)
    stack.appendleft(0)
    return stack


def OP_GT(stack):
    a = stack.pop()
    b = stack.pop()
    if (b > a):
        stack.append(0xFFFFFFFF)
    else:
        stack.append(0)
    stack.appendleft(0)
    return stack
    
def OP_EQ(stack):
    a = stack.pop()
    b = stack.pop()
    if (b == a):
        stack.append(0xFFFFFFFF)
    else:
        stack.append(0)
    stack.appendleft(0)
    return stack


CHARMAP = {
    'c': OP_DROP,
    'd': OP_MUL,
    'e': OP_DIV,
    'f': OP_ADD,
    'g': OP_SUB,
    'h': OP_MOD,
    'i': OP_NEG,
    'j': OP_LSHIFT,
    'k': OP_RSHIFT,
    'l': OP_AND,
    'm': OP_OR,
    'n': OP_XOR,
    'o': OP_NOT,
    'p': OP_DUP,
    'q': OP_GET,
    'r': OP_SWAP,
    's': OP_LT,
    't': OP_GT,
    'u': OP_EQ,
}


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
        self.stack = deque([0] * 0x100)

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
                self.stack = OP_PUSH(self.stack, (int(token, 16)))
            elif (token == '.'):  # NOP
                pass
            elif (token == 'a'):  # OP_T
                self.stack = OP_PUSH(self.stack, t)
            else:
                try:
                    self.stack = CHARMAP[token](self.stack)
                except KeyError:
                    stderr.write(token + ' not implemented, ignored.\n')

        return self.stack[-1] & 0xFF

