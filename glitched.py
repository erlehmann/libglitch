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

from sys import argv, stderr, stdout
from time import time

import pygame
import glitch

HEIGHT = 8
WIDTH = 16

TILESIZE = 11
SCALE = 4
GRID = TILESIZE * SCALE

TILEMAP = {
    '0': (0, 0),
    '1': (1, 0),
    '2': (2, 0),
    '3': (3, 0),
    '4': (4, 0),
    '5': (5, 0),
    '6': (6, 0),
    '7': (7, 0),
    '8': (0, 1),
    '9': (1, 1),
    'A': (2, 1),
    'B': (3, 1),
    'C': (4, 1),
    'D': (5, 1),
    'E': (6, 1),
    'F': (7, 1),
    'a': (0, 2),
    'b': (0, 1),
    'c': (2, 2),
    'd': (3, 2),
    'e': (4, 2),
    'f': (5, 2),
    'g': (6, 2),
    'h': (7, 2),
    'i': (0, 3),
    'j': (1, 3),
    'k': (2, 3),
    'l': (3, 3),
    'm': (4, 3),
    'n': (5, 3),
    'o': (6, 3),
    'p': (7, 3),
    'q': (0, 4),
    'r': (1, 4),
    's': (2, 4),
    't': (3, 4),
    'u': (4, 4),
    '.': (6, 6),
    'CURSOR': (7, 6)
}

KEYORDER = '0123456789ABCDEFacdefghijklmnopqrstu.'

if len(argv) != 2:
    stderr.write('Usage: glitched.py [glitchfile]\n')
    exit(1)

with open(argv[1]) as f:
    input = f.read().replace('\n', '')
    m = glitch.Melody(input)

m._expand_(m.lines)

pygame.init()

screen = pygame.display.set_mode((WIDTH*GRID, HEIGHT*GRID), pygame.RESIZABLE)
tileset = pygame.transform.scale(
    pygame.image.load('tileset.png'),
    (8*GRID, 7*GRID)
)

curpos = [0, 0]

def tile(char):
    tile = pygame.Surface((GRID, GRID), pygame.SRCALPHA)
    x = GRID * TILEMAP[char][0]
    y = GRID * TILEMAP[char][1]
    tile.blit(tileset, (0, 0), (x, y, GRID, GRID))
    return tile

def redraw():
    for i in range(HEIGHT):
        for j in range(WIDTH):
            screen.blit(tile('.'), (j*GRID, i*GRID))

    for i, line in enumerate(m.lines[1:]):
        for j, char in enumerate(line):
            screen.blit(tile(char), (j*GRID, i*GRID))

    screen.blit(tile('CURSOR'), (curpos[0]*GRID, curpos[1]*GRID))

redraw()

starttime = time()
i = 0
running = True
while running:
    if ((time() - starttime)*8000 > i):  # no excess output
        for k in range(40):
            stdout.write(chr(m._compute_(i)))
            i += 1

    for event in pygame.event.get():
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                if curpos[0] > 0:
                    curpos[0] -= 1
            if event.key == pygame.K_RIGHT:
                if curpos[0] < (WIDTH-1):
                    curpos[0] += 1
            if event.key == pygame.K_UP:
                if curpos[1] > 0:
                    curpos[1] -= 1
            if event.key == pygame.K_DOWN:
                if curpos[1] < (HEIGHT-1):
                    curpos[1] += 1

            if event.key == pygame.K_SPACE or \
                event.key == pygame.K_PAGEUP or \
                event.key == pygame.K_PAGEDOWN:
                column = curpos[0]
                row = curpos[1]
                line = m.lines[row+1]
                char = line[column]

                if event.key == pygame.K_SPACE:
                    index = (KEYORDER.find('.'))
                elif event.key == pygame.K_PAGEUP:
                    index = (KEYORDER.find(char) - 1) % len(KEYORDER)
                elif event.key == pygame.K_PAGEDOWN:
                    index = (KEYORDER.find(char) + 1) % len(KEYORDER)
                newchar = KEYORDER[index]

                m.lines[row+1] = line[:column] + newchar + line[column+1:]
                m.tokens = m._tokenize_(m.lines)
                stderr.write('Now playing: ' + str(m) + '\n')

            redraw()

        elif event.type == pygame.QUIT:
            with open(argv[1], 'w') as f:
                f.write(str(m) + '\n')
                stderr.write(str(m) + ' saved.\n')

            running = False

    pygame.display.flip()
    
