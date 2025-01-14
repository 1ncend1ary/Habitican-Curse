""" Module "Config" : Global Config File

    This file contains all the constants used in the program that pertain
    to the configuration of the terminal
"""

# Standard Library imports
import curses
import datetime
import os

NUM_CONTEXT_REGISTERS = 4

# Screen Specifications - Will be adjusted during runtime
SCR_MAX_MENU_ROWS   = 22   # Keep this as an even number please
SCR_X = 0
SCR_Y = 0
SCR_MENU_ITEM_WIDTH = 0
SCR_FIRST_HALF_LENGTH = 0  # Space taken up by the upper half menu of tasks
SCR_TEXT_AREA_LENGTH = 0

# Colors
SCR_COLOR_RED          = 2
SCR_COLOR_GREEN        = 3
SCR_COLOR_YELLOW       = 4
SCR_COLOR_BLUE         = 5
SCR_COLOR_WHITE        = 6
SCR_COLOR_MAGENTA      = 7
SCR_COLOR_CYAN         = 14
SCR_COLOR_LIGHT_ORANGE = 8
SCR_COLOR_DARK_ORANGE  = 9
SCR_COLOR_DARK_GRAY    = 15
SCR_COLOR_LIGHT_GRAY    = 16

# Display Colors with Background
SCR_COLOR_WHITE_GRAY_BGRD = 12
SCR_COLOR_GRAY_WHITE_BGRD = 13

SCR_COLOR_RED_GRAY_BGRD     = 17
SCR_COLOR_GREEN_GRAY_BGRD   = 18
SCR_COLOR_YELLOW_GRAY_BGRD  = 19
SCR_COLOR_BLUE_GRAY_BGRD    = 20
SCR_COLOR_WHITE_GRAY_BGRD   = 21
SCR_COLOR_MAGENTA_GRAY_BGRD = 22

# Background Color (Default black)
SCR_COLOR_BGRD = curses.COLOR_BLACK

# Special Color Codes
SCR_COLOR_NEUTRAL = SCR_COLOR_LIGHT_GRAY

# Special Symbols
SYMBOL_TICK = '\u2714'
SYMBOL_DISC = '\u25CF'
SYMBOL_DOWN_TRIANGLE = '\u25BC'
SYMBOL_UP_TRIANGLE = '\u25B2'
SYMBOL_DELETE = 'x'
SYMBOL_HEART = '\u2665'
SYMBOL_EXPERIENCE = '\u2605'
SYMBOL_GOLD = '\u25CF'
SYMBOL_MANA = '\u2600'
SYMBOL_EDIT = '\u270E'
SYMBOL_LEVEL = '\u2949'
SYMBOL_DUE = '\u29D6'
SYMBOL_CHALLENGE_FLAG = '\u2691'

# Status Attributes
HabitStatus = {'+': 0, '-': 0, SYMBOL_DELETE: False, SYMBOL_EDIT: False}
HabitPosStatus = {'+': 0, SYMBOL_DELETE: False, SYMBOL_EDIT: False}
HabitNegStatus = {'-': 0, SYMBOL_DELETE: False, SYMBOL_EDIT: False}
UnscoredHabitStatus = {SYMBOL_DELETE: False, SYMBOL_EDIT: False}
TODODailyStatus = {SYMBOL_TICK: False, SYMBOL_DELETE: False, SYMBOL_EDIT: False}
ChecklistStatus = {SYMBOL_TICK: False, SYMBOL_DELETE: False, SYMBOL_EDIT: False}

# Function for setting values at runtime

def ConfigureRuntime(screen):
    global SCR_Y, SCR_X, SCR_MENU_ITEM_WIDTH, SCR_TEXT_AREA_LENGTH, SCR_FIRST_HALF_LENGTH
    SCR_X, SCR_Y = screen.getmaxyx()
    SCR_MENU_ITEM_WIDTH = (SCR_Y - 10)/3
    SCR_TEXT_AREA_LENGTH = (SCR_X - (SCR_MAX_MENU_ROWS + 7 + 4))
    SCR_FIRST_HALF_LENGTH = SCR_MAX_MENU_ROWS + 7

# Parser Settings
SET_COMMANDS = ["d", "due", "every", "weekly", "direction"]
DIFFS      = ["trivial", "easy", "medium", "hard"]
DATEPARSER = datetime.datetime.strptime
DATEFORMATS = ["%d/%m/%Y", "%d/%m/%y"]
DEFAULT_REPEAT = {'m': True, 't': True, 'w': True, 'th': True, 'f': True, 's': True, 'su': True}


# Configuration file settings
user_config = None

#Read in the configuration files
def ReadConfigFile():
    global user_config
    user_config = dict()

    CONFIG_FILE = os.getenv("HOME")+'/.habiticarc'

    try:
        f = open(CONFIG_FILE, 'r')
    except:
        import sys
        print("Enter UUID: ", end=' ')
        uuid = input().strip()
        print(" ")
        print("Enter API-Key: ", end=' ')
        key = input().strip()

        f = open(CONFIG_FILE, 'w+')
        f.write("uuid="+uuid+"\n")
        f.write("key="+key+"\n")
        f.write("debug_lvl=50\n")
        f.close()

        f = open(CONFIG_FILE, 'r')

    for x in f.readlines():
        x = x[:-1].split("=")
        user_config[x[0]] = x[1]

    f.close()

def getConfig(value):
    if( user_config is None):
        ReadConfigFile()

    if( value in user_config ):
        return user_config[value]

    return None
