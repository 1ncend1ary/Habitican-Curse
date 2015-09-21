""" Module "Screen" : Wrapper for the ncurses screen

    All screen related functions such as displaying text, colors, background,
    saving/restoring context etc. go here.
"""
# Standard Library Imports
import curses
import tempfile
import math

# Custom Module Imports

import config as C
import debug as DEBUG

class Screen(object):

    def __init__(self, screen):
        self.screen = screen

        # These are special context registers.
        # Use these to store some important backtrack points.
        self.ctxts = []
        for i in xrange(C.NUM_CONTEXT_REGISTERS):
            self.ctxts += [tempfile.TemporaryFile()]

        self.active_registers = [False]*C.NUM_CONTEXT_REGISTERS

        # This is the stack for saving contexts.
        # Use these to get a proper order of backtrack points
        self.stackFile = tempfile.TemporaryFile()
        self.stack = []
        self.SCR_X=0
        self.SCR_Y=0
        self.SCR_MENU_ITEM_WIDTH=0

    def Initialize(self):
        #global SCR_X, SCR_Y, SCR_MENU_ITEM_WIDTH
        # Cursor not visible
        curses.curs_set(0)

        # Color and Background
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(C.SCR_COLOR_RED, curses.COLOR_RED, C.SCR_COLOR_BGRD)
        curses.init_pair(C.SCR_COLOR_CYAN, curses.COLOR_CYAN, C.SCR_COLOR_BGRD)
        curses.init_pair(C.SCR_COLOR_GREEN, curses.COLOR_GREEN, C.SCR_COLOR_BGRD)
        curses.init_pair(C.SCR_COLOR_YELLOW, curses.COLOR_YELLOW, C.SCR_COLOR_BGRD)
        curses.init_pair(C.SCR_COLOR_MAGENTA, curses.COLOR_MAGENTA, C.SCR_COLOR_BGRD)
        curses.init_pair(C.SCR_COLOR_BLUE, curses.COLOR_BLUE, C.SCR_COLOR_BGRD)
        curses.init_pair(C.SCR_COLOR_WHITE, curses.COLOR_WHITE, C.SCR_COLOR_BGRD)

        curses.init_pair(C.SCR_COLOR_LIGHT_ORANGE, 209, C.SCR_COLOR_BGRD)
        curses.init_pair(C.SCR_COLOR_DARK_ORANGE, 208, C.SCR_COLOR_BGRD)
        curses.init_pair(C.SCR_COLOR_DARK_GRAY, 237, C.SCR_COLOR_BGRD)
        curses.init_pair(C.SCR_COLOR_LIGHT_GRAY, 244, C.SCR_COLOR_BGRD)

        curses.init_pair(C.SCR_COLOR_BLUE_GRAY_BGRD, 19, 244)
        curses.init_pair(C.SCR_COLOR_GRAY_BLUE_BGRD, 244, 19)

        curses.init_pair(C.SCR_COLOR_WHITE_GRAY_BGRD, curses.COLOR_WHITE, 234)
        curses.init_pair(C.SCR_COLOR_GRAY_WHITE_BGRD, 236, curses.COLOR_WHITE)

        # Same as writing " " in white on a black background
        self.screen.bkgd(' ', curses.color_pair(C.SCR_COLOR_WHITE))

        # Screen Specifications
        self.SCR_Y, self.SCR_X = self.screen.getmaxyx()
        self.SCR_MENU_ITEM_WIDTH = (self.SCR_X - 10)/3

    def Refresh(self):
        self.screen.refresh()

    def Erase(self):
        self.screen.erase()

    def Clear(self):
        self.screen.clear()

    def SaveInRegister(self, register):
        # Should be between 0 and C.NUM_CONTEXT_REGISTERS-1
        if register >= C.NUM_CONTEXT_REGISTERS:
            return

        self.ctxts[register].seek(0)
        self.screen.putwin(self.ctxts[register])
        self.active_registers[register] = True

    def RestoreRegister(self, register):
        # Should be between 0 and C.NUM_CONTEXT_REGISTERS-1
        if register >= C.NUM_CONTEXT_REGISTERS:
            return

        # Register is empty
        if not self.active_registers[register]:
            return

        self.screen = curses.getwin(self.ctxts[register])
        self.Refresh()

    def Save(self):
        self.stack.append(self.stackFile.tell())
        self.screen.putwin(self.stackFile)

    def Restore(self):
        # Stack cannot be empty
        if len(self.stack) == 0:
            return

        self.stackFile.seek(self.stack[-1])
        self.screen = curses.getwin(self.stackFile)
        self.Refresh()

    def Display(self, string, x=0, y=0):
        self.screen.addstr(x, y, string)
        self.Refresh()

    def DisplayBold(self, string, x=0, y=0):
        self.screen.addstr(x, y, string, curses.A_BOLD)
        self.Refresh()

    def Highlight(self, string, x=0, y=0):
        self.screen.addstr(x, y, string, curses.A_BOLD |
                                         curses.color_pair(C.SCR_COLOR_WHITE_GRAY_BGRD))
        self.Refresh()

    def DisplayCustomColor(self, string, color=0, x=0, y=0):
        self.screen.addstr(x, y, string, curses.color_pair(color))
        self.Refresh()

    def DisplayCustomColorBold(self, string, color=0, x=0, y=0):
        self.screen.addstr(x, y, string, curses.A_BOLD |
                                         curses.color_pair(color))
        self.Refresh()

    def GetCharacter(self):
        return self.screen.getch()

    def ScrollBar(self, X, Y, start, end, length, rows = -1):
        if rows == -1:
            rows = C.SCR_MAX_MENU_ROWS

        start_space = int(math.ceil((start * 1.0)/(length) * rows))
        end_space   = int(math.floor(((length - end) * 1.0)/(length) * rows))

        self.DisplayCustomColor(C.SYMBOL_UP_TRIANGLE, C.SCR_COLOR_DARK_GRAY,
                                    X-1, Y)
        self.DisplayCustomColorBold(C.SYMBOL_DOWN_TRIANGLE, C.SCR_COLOR_DARK_GRAY,
                                    X+rows, Y)

        starting = X
        ending   = X + rows
        for i in xrange(start_space):
            self.DisplayCustomColorBold(" ", C.SCR_COLOR_WHITE_GRAY_BGRD, X+i, Y)
            starting = X + i
        
        for i in xrange(end_space):
            self.DisplayCustomColorBold(" ", C.SCR_COLOR_WHITE_GRAY_BGRD, 
                                        X+rows-1-i, Y)
            ending = X + rows - 1 - i

        for i in xrange(starting, ending):
            self.DisplayCustomColorBold(" ", C.SCR_COLOR_GRAY_WHITE_BGRD, i, Y)

