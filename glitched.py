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
import numpy

#import pycallgraph

GRAPH_WIDTH = 16
GRAPH_HEIGHT = 16
TEXT_HEIGHT = 16
TEXT_WIDTH = 16

TILESIZE = 11
SCALE = 2
GRID = TILESIZE * SCALE

BUFSIZE = 256

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
    'b': (1, 2),
    'c': (2, 2),
    'd': (3, 2),
    'e': (4, 2),
    'f': (5, 2),
    'g': (6, 2),
    'h': (7, 2),
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

KEYMAP = {
    pygame.K_SPACE: '.',
    pygame.K_PERIOD: '.',
    pygame.K_t : 'a',
    pygame.K_ASTERISK: 'd',
    pygame.K_KP_MULTIPLY : 'd',
    pygame.K_SLASH : 'e',
    pygame.K_KP_DIVIDE : 'e',
    pygame.K_PLUS : 'f',
    pygame.K_KP_PLUS : 'f',
    pygame.K_MINUS : 'g',
    pygame.K_KP_MINUS : 'g',
    pygame.K_LESS : 's',
    pygame.K_GREATER : 't',
    pygame.K_EQUALS: 'u',
    pygame.K_KP_EQUALS: 'u',
    pygame.K_0 : '0',
    pygame.K_1 : '1',
    pygame.K_2 : '2',
    pygame.K_3 : '3',
    pygame.K_4 : '4',
    pygame.K_5 : '5',
    pygame.K_6 : '6',
    pygame.K_7 : '7',
    pygame.K_8 : '8',
    pygame.K_9 : '9',
    pygame.K_a : 'A',
    pygame.K_b : 'B',
    pygame.K_c : 'C',
    pygame.K_d : 'D',
    pygame.K_e : 'E',
    pygame.K_f : 'F'
}

KEYORDER = '0123456789ABCDEFabcdefghjklmnopqrstu.'

if len(argv) != 2:
    stderr.write('Usage: glitched.py [glitchfile]\n')
    exit(1)

with open(argv[1]) as f:
    input = f.read().replace('\n', '')
    m = glitch.Melody(input)

m._expand_(m.lines)

pygame.mixer.pre_init(8000, 8, 1, BUFSIZE)
pygame.init()

icon = pygame.image.load('glitched.png')
pygame.display.set_icon(icon)

screen = pygame.display.set_mode((
        (TEXT_WIDTH + GRAPH_WIDTH)*GRID, \
        max(TEXT_HEIGHT, GRAPH_HEIGHT)*GRID
    ), pygame.HWSURFACE)
tileset = pygame.transform.scale(
    pygame.image.load('tileset.png'),
    (8*GRID, 7*GRID)
).convert()

curpos = [0, 0]

tilecache = {}

def tile(char):
    global tilecache
    try:
        return tilecache[char]
    except KeyError:
        tile = pygame.Surface((GRID, GRID), pygame.HWSURFACE).convert()
        tile.set_colorkey((0, 0, 0))
        x = GRID * TILEMAP[char][0]
        y = GRID * TILEMAP[char][1]
        tile.blit(tileset, (0, 0), (x, y, GRID, GRID))
        tilecache[char] = tile
        return tile

def draw_controls():
    screen.fill(
        (253, 246, 227),  # Solarized Base03
        (GRAPH_WIDTH*GRID, 0, TEXT_WIDTH*GRID + GRAPH_WIDTH*GRID, TEXT_HEIGHT*GRID)
    )

    for i, line in enumerate(m.lines[1:]):
        for j, char in enumerate(line):
            if (char != '.'):  # NOP, not drawn
                screen.blit(tile(char), (j*GRID + GRAPH_WIDTH*GRID, i*GRID))

    screen.blit(tile('CURSOR'), (curpos[0]*GRID + GRAPH_WIDTH*GRID, curpos[1]*GRID))
    pygame.display.update((GRAPH_WIDTH*GRID, 0, TEXT_WIDTH*GRID, TEXT_HEIGHT*GRID))

draw_controls()

valuepattern = pygame.Surface((136, 128), pygame.HWSURFACE)
valuepattern.convert()

def draw_valuepattern(buf, target, drop_frame=False):
    """
    Draws a pattern with color determined by sample.
    """
    global valuepattern
    if not drop_frame:
        for x, y in enumerate(buf):
            valuepattern.set_at((127, 127-x/2), (y, y, y))
    target.fill((133, 153, 0))  # Solarized Green
    target.blit(valuepattern, (0, 0), (0, 0, 128, 128), pygame.BLEND_ADD)
    valuepattern.scroll(-1, 0)

ypattern = pygame.Surface((136, 128), pygame.HWSURFACE)
ypattern.convert()
ypattern.set_colorkey((0, 0, 0))

def draw_ypattern(buf, target, drop_frame=False):
    """
    Draws a pattern with y coordinate determined by sample.
    """
    global ypattern
    if not drop_frame:
        yarray = pygame.surfarray.pixels2d(ypattern)
        for sample in buf: # shadow
            y = 127-sample/2
            yarray[127][y] = 0x073642  # Solarized Base02
            yarray[126][y] = 0x073642
        for sample in buf:
            y = 126-sample/2
            yarray[127][y] = 0xdc322f  # Solarized Red
            yarray[126][y] = 0xdc322f
        del yarray
    target.blit(ypattern, (0, 0), (0, 0, 128, 128))
    ypattern.scroll(-2, 0)

oldsample = 0

def draw_wave(buf, target, drop_frame=False):
    """
    Draws the local wave (256 samples).
    """
    if not drop_frame:
        global oldsample
        for x, sample in enumerate(buf):
            pygame.draw.line(target, (7, 54, 66), (x/2, 128-sample/2),
                (x/2, 128-oldsample/2))  # shadow
            pygame.draw.line(target, (7, 54, 66), (x/2+1, 128-sample/2),
                (x/2+1, 128-oldsample/2))  # shadow
            pygame.draw.line(target, (38, 139, 210), (x/2, 127-sample/2),
                (x/2, 127-oldsample/2))  # Solarized Blue
            oldsample = sample

import colorsys

def draw_stack(stack, target, drop_frame):
    """
    Draws the stack as a 16x16 square using a HSV model.

    Hue is determined by 12 highest bytes.
    Saturation is determined by the next 12 bits.
    Value is determined using the last 8 bits.
    """
    pixels = pygame.Surface((16, 16), pygame.HWSURFACE)
    if not drop_frame:
        stackarray = pygame.surfarray.pixels3d(pixels)
        for i, value in enumerate(stack):
            x = (i % 16)
            y = ((i / 16) % 16)
            h = (value >> 20 & 0xFFF) / 4095.0
            s = (value >> 8 & 0xFFF) / 4095.0
            v = (value & 0xFF) / 255.0
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            stackarray[-x][-y][0] = r * 0xFF
            stackarray[-x][-y][1] = g * 0xFF
            stackarray[-x][-y][2] = b * 0xFF
        del stackarray
    pixels = pygame.transform.scale(pixels, (128, 128))
    target.blit(pixels, (0, 0), (0, 0, GRAPH_WIDTH*GRID, GRAPH_HEIGHT*GRID))

font = pygame.font.SysFont("DejaVu Sans Mono", GRID)

RENDER_WAVE = True
RENDER_YPATTERN = True
RENDER_VALUEPATTERN = True

RENDER_STACK = False
RENDER_ITERATOR = False

def draw_graph(buf, stack, t, drop_frame=False):
    graph = pygame.Surface((128, 128), pygame.HWSURFACE)
    graph.convert()

    if RENDER_STACK:
        draw_stack(stack, graph, drop_frame)

    for b in [buf[i:i+256] for i in xrange(0, len(buf), 256)]:
        if RENDER_VALUEPATTERN:
            draw_valuepattern(b, graph, drop_frame)
        if RENDER_YPATTERN:
            draw_ypattern(b, graph, drop_frame)
        if RENDER_WAVE:
            draw_wave(b, graph, drop_frame)

    graph = pygame.transform.scale(graph, (GRAPH_WIDTH*GRID, GRAPH_HEIGHT*GRID))
    screen.blit(graph, (0, 0), (0, 0, GRAPH_WIDTH*GRID, GRAPH_HEIGHT*GRID))

    if RENDER_ITERATOR:
        text = font.render("%08X" % t, 0, (0, 0, 0))
        screen.blit(text, (GRAPH_WIDTH*GRID - text.get_width(), 0), (0, 0, GRAPH_WIDTH*GRID, GRAPH_HEIGHT*GRID))
    pygame.display.update((0, 0, GRAPH_WIDTH*GRID, GRAPH_HEIGHT*GRID))

channel = pygame.mixer.find_channel()
i = 0
running = True
while running:
    starttime = time()
    if (channel.get_queue() == None):  # no excess output
        buf = [m._compute_(j) for j in xrange(i, i+BUFSIZE)]
        sound = pygame.sndarray.make_sound(numpy.array(buf, numpy.uint8))
        channel.queue(sound)
        i += BUFSIZE

        drop_frame = ((time() - starttime)*8000 > BUFSIZE)
        draw_graph(buf, m.stack, i, drop_frame)
        if drop_frame:
            stderr.write('Dropped frame; your system may be too slow.\n')

    for event in pygame.event.get():
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                if curpos[0] > 0:
                    curpos[0] -= 1
            if event.key == pygame.K_RIGHT:
                if curpos[0] < (TEXT_WIDTH-1):
                    curpos[0] += 1
            if event.key == pygame.K_UP:
                if curpos[1] > 0:
                    curpos[1] -= 1
            if event.key == pygame.K_DOWN:
                if curpos[1] < (TEXT_HEIGHT-1):
                    curpos[1] += 1

            if event.key == pygame.K_HOME:
                curpos[0] = 0
            if event.key == pygame.K_END:
                curpos[0] = 15

            if event.key == pygame.K_ESCAPE:
                i = 0

            if event.key == pygame.K_F5:
                RENDER_WAVE = not RENDER_WAVE

            if event.key == pygame.K_F6:
                RENDER_YPATTERN = not RENDER_YPATTERN

            if event.key == pygame.K_F7:
                RENDER_VALUEPATTERN = not RENDER_VALUEPATTERN

            if event.key == pygame.K_F8:
                RENDER_STACK = not RENDER_STACK

            if event.key == pygame.K_F9:
                RENDER_ITERATOR = not RENDER_ITERATOR

            if event.key in KEYMAP.keys() or \
                event.key == pygame.K_PAGEUP or \
                event.key == pygame.K_PAGEDOWN:
                column = curpos[0]
                row = curpos[1]
                line = m.lines[row+1]
                char = line[column]

                try:
                    newchar = KEYMAP[event.key]
                except KeyError:
                    if event.key == pygame.K_PAGEUP:
                        index = (KEYORDER.find(char) - 1) % len(KEYORDER)
                        newchar = KEYORDER[index]
                    elif event.key == pygame.K_PAGEDOWN:
                        index = (KEYORDER.find(char) + 1) % len(KEYORDER)
                    newchar = KEYORDER[index]

                m.lines[row+1] = line[:column] + newchar + line[column+1:]
                m.tokens = m._tokenize_(m.lines[1:])
                m._reset_()
                stderr.write('Now playing: ' + str(m) + '\n')

            draw_controls()

        elif event.type == pygame.QUIT:
            with open(argv[1], 'w') as f:
                f.write(str(m) + '\n')
                stderr.write(str(m) + ' saved.\n')

            running = False
    
