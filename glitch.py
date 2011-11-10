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

OPCODES = '.abcdefghijklmnopqrstuvwxyzGHIJKLMNOPQRSTUVWXYZ'
HEXDIGITS = '0123456789ABCDEF'

def OP_DROP(stack):
    stack.pop()
    return stack

def OP_MUL(stack):
    a = stack.pop()
    b = stack.pop()
    stack.append(b * a)
    return stack

def OP_DIV(stack):
    a = stack.pop()
    b = stack.pop()
    stack.append(b / a)
    return stack

def OP_ADD(stack):
    a = stack.pop()
    b = stack.pop()
    stack.append(b + a)
    return stack

def OP_SUB(stack):
    a = stack.pop()
    b = stack.pop()
    stack.append(b - a)
    return stack

def OP_MOD(stack):
    a = stack.pop()
    b = stack.pop()
    stack.append(b % a)
    return stack

def OP_NEG(stack):
    a = stack.pop()
    stack.append(-a)
    return stack

def OP_LSHIFT(stack):
    a = stack.pop()
    b = stack.pop()
    stack.append(b << a)
    return stack
    
def OP_RSHIFT(stack):
    a = stack.pop()
    b = stack.pop()
    stack.append(b >> a)
    return stack
    
def OP_AND(stack):
    a = stack.pop()
    b = stack.pop()
    stack.append(b & a)
    return stack

def OP_OR(stack):
    a = stack.pop()
    b = stack.pop()
    stack.append(b | a)
    return stack

def OP_XOR(stack):
    a = stack.pop()
    b = stack.pop()
    stack.append(b ^ a)
    return stack

def OP_NOT(stack):
    a = stack.pop()
    stack.append(~a)
    return stack

def OP_DUP(stack):
    stack.append(stack[-1])
    return stack

def OP_PEEK(stack):
    raise NotImplementedError

def OP_SWAP(stack):
    a = stack.pop()
    b = stack.pop()
    stack.append(a)
    stack.append(b)
    return stack

def OP_LT(stack):
    raise NotImplementedError

def OP_GT(stack):
    raise NotImplementedError
    
def OP_EQ(stack):
    raise NotImplementedError

def OP_COUNT(stack):
    raise NotImplementedError


CHARMAP = {
    'b': OP_DROP,
    'c': OP_MUL,
    'd': OP_DIV,
    'e': OP_ADD,
    'f': OP_SUB,
    'g': OP_MOD,
    'h': OP_NEG,
    'i': OP_LSHIFT,
    'j': OP_RSHIFT,
    'k': OP_AND,
    'l': OP_OR,
    'm': OP_XOR,
    'n': OP_NOT,
    'o': OP_DUP,
    'p': OP_PEEK,
    'q': OP_SWAP,
    'r': OP_LT,
    's': OP_GT,
    't': OP_EQ,
}


class Melody:
    def __init__(self, melody):
        """
        A Melody consists of lines signifying opcodes and hexadecimal numbers.
        [a-z] and [G-Z] denote opcodes, while [1-9] and [A-F] denote numbers.
        """

        assert(type(melody) == str)

        self.melody = melody
        self.tokens = self._tokenize_(melody)

    def __repr__(self):
        return str(self.tokens) + '\n'

    def _tokenize_(self, string):
        tokens = []

        for char in string:
            try:
                if (char in HEXDIGITS) and (tokens[-1] in HEXDIGITS):
                    tokens[-1] += char
                else:
                    tokens.append(char)
            except IndexError:
                pass  # first character

        return tokens

    def _compute_(self, t):
        self.stack = [0] * 0xFF     

        for token in self.tokens:
            if not token in OPCODES:  # not an opcode, must be a number
                self.stack.append(int(token, 16))
            elif (token == '.'):  # NOP
                pass
            elif (token == 'a'):  # OP_T
                self.stack.append(t)
            else:
                try:
                    self.stack = CHARMAP[token](self.stack)
                except KeyError:
                    stderr.write(token + ' not implemented, ignored.\n')

        return self.stack.pop() & 0xFF

