""" Module "Helper" : Helper functions and classes

    Contains classes and functions for wrapping text, task modification status,
    text menus, date-time etc.
"""

# Standard Library Imports
import time
import curses
from datetime import datetime, timedelta
from dateutil import tz, relativedelta

# Custom Module Imports

import habitican_curse.config as C
from habitican_curse.screen import Screen
import habitican_curse.global_objects as G
import habitican_curse.debug as DEBUG
import habitican_curse.content as CT
import habitican_curse.menu as M

#Set up logging
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug logging started for %s..." % __name__)

class Status(object):

    def __init__(self, task_type, checklist=[0, 0], due='', isChallenge=False):
        if task_type == "habit":
            self.attributes = C.HabitStatus.copy()
        elif task_type == "habitpos":
            self.attributes = C.HabitPosStatus.copy()
        elif task_type == "habitneg":
            self.attributes = C.HabitNegStatus.copy()
        elif task_type == "unscoredhabit":
            self.attributes = C.UnscoredHabitStatus.copy()
        elif task_type == "checklist":
            self.attributes = C.ChecklistStatus.copy()
        else:
            self.attributes = C.TODODailyStatus.copy()

        self.checklist = checklist
        self.due = due
        self.x = 0
        self.y = 0
        self.newItem = False
        self.isChallenge = isChallenge

    def ReturnLenString(self):
        length = 2*len([i for i in self.attributes if self.attributes[i]!=None])
        if self.isChallenge: length += 2 # Challenge tasks - Display a flag
        length-=2 #Deletion attribute is not shown in status line (represented with strikethrough)
        if self.checklist[1] != 0:
            # (Done/Total) - 4 extra symbols - '(', ')', '/' and a space
            length += 5 + len(str(self.checklist[0])) + len(str(self.checklist[1]))

        if self.due!='':
            length += len(self.due) + 3 # To account for a space

        return length

    def SetXY(self, x=0, y=0):
        self.x = x
        self.y = y

    def SetChecklist(self, checklist):
        self.checklist = checklist

    def SetDue(self, due):
        self.due = due

    def Display(self):
        X, Y = self.x, self.y

        if self.checklist[1] != 0:
            display_string = '('+str(self.checklist[0])+'/'+str(self.checklist[1])+')'
            Y -= (len(display_string))
            display_string = C.SYMBOL_DOWN_TRIANGLE + display_string
            G.screen.Display(display_string,X, Y,
                                            color=C.SCR_COLOR_LIGHT_GRAY, bold=True)
            Y -= 2

        if self.due != '':
            Y -= (len(self.due) + 1)
            G.screen.Display(C.SYMBOL_DUE + " " + self.due, X, Y,
                    color=C.SCR_COLOR_LIGHT_GRAY, bold=True)
            Y -= 2

        #Always show the edit symbol first (it's guaranteed to be there)
        if(self.attributes[C.SYMBOL_EDIT]):
            G.screen.Display(C.SYMBOL_EDIT, X, Y,
                    color=C.SCR_COLOR_YELLOW, bold=True)
        else:
            G.screen.Display(C.SYMBOL_EDIT, X, Y,
                    color=C.SCR_COLOR_DARK_GRAY, bold=True)
        Y -= 2

        # Challenge tasks
        if self.isChallenge:
            G.screen.Display(C.SYMBOL_CHALLENGE_FLAG, X, Y,
                    color=C.SCR_COLOR_DARK_GRAY, bold=True)
            Y -= 2


        for (key, value) in self.attributes.items():

            if key == C.SYMBOL_DELETE or key == C.SYMBOL_EDIT:
                #Edit status is always shown first
                #Deletion status is shown with strikethrough, not needed here
                continue

            if value != None:
                if value:
                    G.screen.Display(key, X, Y,
                            color=C.SCR_COLOR_YELLOW, bold=True)
                    if( value > 1):
                        DEBUG.logging.debug("Upvote Value is >1, displaying: %s", str(value))
                        G.screen.Display(str(value), X, Y+1,
                                color=C.SCR_COLOR_YELLOW, bold=True)
                        Y-=1
                    else:
                        Y-=2
                else:
                    G.screen.Display(key, X, Y,
                            color=C.SCR_COLOR_DARK_GRAY, bold=True)
                    Y -= 2

    def ToggleMarkUp(self):
        # Return if the delete option has already
        # been enabled or the edit status is true
        if (self.attributes[C.SYMBOL_DELETE] or
            self.attributes[C.SYMBOL_EDIT]):
            return

        #Decrement the mark down or increment mark up (if it's allowed)
        if(self.attributes.get("-",0) > 0):
            self.attributes["-"] -= 1
        elif( "+" in self.attributes ):
            self.attributes["+"] += 1

    def ToggleMarkDown(self):
        # Return if there is no down direction, or the delete option has already
        # been enabled or the edit status is true
        if (self.attributes[C.SYMBOL_DELETE] or
            self.attributes[C.SYMBOL_EDIT]):
            return

        if(self.attributes.get("+",0) > 0):
            self.attributes["+"] -= 1
        elif( "-" in self.attributes ):
            self.attributes["-"] += 1

    def ToggleMark(self):
        # Return if the delete option has already been enabled or the edit
        # status is true
        if (self.attributes[C.SYMBOL_DELETE] or
            self.attributes[C.SYMBOL_EDIT]):
            return

        if self.attributes[C.SYMBOL_TICK]:
            self.attributes[C.SYMBOL_TICK] = False
        else:
            self.attributes[C.SYMBOL_TICK] = True

    def ToggleDelete(self):
        # Take care of challenge tasks
        if self.isChallenge:
            DEBUG.Display("Challenge tasks cannot be deleted from here")
            return

        # Nothing can be enabled along with delete
        for key in self.attributes:
            if key != C.SYMBOL_DELETE:
                self.attributes[key] = False

        if self.attributes[C.SYMBOL_DELETE]:
            self.attributes[C.SYMBOL_DELETE] = False
        else:
            self.attributes[C.SYMBOL_DELETE] = True

    def ToggleEdit(self):
        # Return if the delete option has already been enabled or the edit
        # status is true
        if self.attributes[C.SYMBOL_DELETE]:
            return

        for key in self.attributes:
            if key != C.SYMBOL_EDIT:
                self.attributes[key] = False

        if not self.attributes[C.SYMBOL_EDIT]: # Edits cannot be turned "off"
            self.attributes[C.SYMBOL_EDIT] = True

    def Reset(self):
        for key in self.attributes:
            self.attributes[key] = False

        self.newItem = False

    def IsNewItem(self):
        return self.newItem

    def SetNewItem(self):
        self.newItem = True



class DateTime(object):
    """ Class for handling various date-time formats used in Habitica """

    def __init__(self, inpDate=-1):
        if inpDate == -1:
            inpDate = time.time()*1000

        self.date = self.ConvertDate(inpDate)

    def ConvertDate(self, date):
        if type(date) == datetime:
            retDate = date.replace(tzinfo=tz.tzlocal())
            return retDate

        elif type(date) == int or type(date) == float:
            # Milliseconds included in the timestamp
            retDate = datetime.fromtimestamp(date*1.0/1000)
            retDate = retDate.replace(tzinfo=tz.tzlocal())

            return retDate

        elif type(date) == str:
            # UTC Format. We'll convert it to local time.
            # We assume that local time zone can be computed by dateutil
            try:
                retDate = datetime.strptime(date,"%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                retDate = datetime.strptime(date,"%Y-%m-%dT%H:%M:%SZ")

            retDate = retDate.replace(tzinfo=tz.tzutc()) # UTC Time zone convert
            retDate = retDate.astimezone(tz.tzlocal())   # Local Time

            return retDate

    def ConvertUTC(self):
        retDate = self.date.replace(tzinfo=tz.tzlocal())
        retDate = retDate.astimezone(tz.tzutc())
        try:
            res = retDate.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        except:
            res = retDate.strftime("%Y-%m-%dT%H:%M:%SZ")

        return res

    def DueDateFormat(self):
        return self.date.strftime('[%d/%m]')

    def DateCreatedFormat(self):
        # dd-mm-YY format. I'm Indian :)
        return self.date.strftime('%d/%m/%Y')


def GetDifferenceTime(d2, d1=-1): # d1 - d2
    Date1 = DateTime(d1)
    Date2 = DateTime(d2)
    #DEBUG.Display(Date1.DueDateFormat())
    #time.sleep(20)


    diffDate = relativedelta.relativedelta(Date1.date, Date2.date)
    if diffDate.years!=0:
        return str(diffDate.years)+'y ago'
    if diffDate.months!=0:
        return str(diffDate.months)+'months ago'
    if diffDate.days!=0:
        return str(diffDate.days)+'d ago'
    if diffDate.hours!=0:
        return str(diffDate.hours)+'h ago'

    return str(diffDate.minutes)+'m ago'


def isDueDaily(task):
    if task['frequency'] == 'weekly':
        translateDict = {0: 'm', 1: 't', 2: 'w', 3: 'th', 4: 'f', 5: 's', 6: 'su'}
        if task['repeat'][translateDict[datetime.today().weekday()]]:
            return True
        else:
            return False

    elif task['frequency'] == 'daily':
        if (task['everyX'] == 0):
            return False # Unintuitive, but this is what happens on the main site

        start       = DateTime(str(task['startDate']))
        startDate   = datetime(start.date.year, start.date.month, start.date.day)
        current     = DateTime(-1)
        currentDate = datetime(current.date.year, current.date.month, current.date.day)
        diff        = (currentDate - startDate)
        # Taking care of offsets
        diffDay     = diff.days
        if diffDay % (task['everyX']) == 0:
            return True
        else:
            return False

    return False


def GetUserStats(data):
    stats = data['stats']
    gear  = data['items']['gear']['equipped']
    userClass = stats['class']

    # Intelligence
    statInt = (stats['int'] +            # Allocated
              stats['buffs']['int'] +    # Buffed
              min(stats['lvl'],100)/2)   # Level Bonus

    for i in gear.values():
        gearStats = G.content.Equipment(i)
        if ((gearStats['klass'] == userClass) or
                (gearStats['klass'] == "special" and gearStats.get('specialClass', '') == userClass)):
            statInt += gearStats['int']*1.5
        else:
            statInt += gearStats['int']

    # Perception
    statPer = (stats['per'] +            # Allocated
               stats['buffs']['per'] +   # Buffed
               min(stats['lvl'],100)/2)  # Level Bonus

    for i in gear.values():
        gearStats = G.content.Equipment(i)
        if ((gearStats['klass'] == userClass) or
                (gearStats['klass'] == "special" and gearStats.get('specialClass', '') == userClass)):
            statPer += gearStats['per']*1.5
        else:
            statPer += gearStats['per']

    # Strength
    statStr = (stats['str'] +            # Allocated
               stats['buffs']['str'] +   # Buffed
               min(stats['lvl'],100)/2)  # Level Bonus

    for i in gear.values():
        gearStats = G.content.Equipment(i)
        if ((gearStats['klass'] == userClass) or
                (gearStats['klass'] == "special" and gearStats.get('specialClass', '') == userClass)):
            statStr += gearStats['str']*1.5
        else:
            statStr += gearStats['str']

    # Constitution
    statCon = (stats['con'] +            # Allocated
               stats['buffs']['con'] +   # Buffed
               min(stats['lvl'],100)/2)  # Level Bonus

    for i in gear.values():
        gearStats = G.content.Equipment(i)
        if ((gearStats['klass'] == userClass) or
                (gearStats['klass'] == "special" and gearStats.get('specialClass', '') == userClass)):
            statCon += gearStats['con']*1.5
        else:
            statCon += gearStats['con']

    if statInt == int(statInt):
        statInt = int(statInt)

    if statStr == int(statStr):
        statStr = int(statStr)

    if statPer == int(statPer):
        statPer = int(statPer)

    if statCon == int(statCon):
        statCon = int(statCon)

    return {'int': statInt, 'per': statPer, 'str': statStr, 'con': statCon}


def DatePicker():
    X, Y = C.SCR_X - 4, 5

    # Clear Text Region
    G.screen.ClearTextArea()

    helpString = "Enter Date (dd/mm/yyyy): "
    G.screen.Display(helpString, X,5,color=C.SCR_COLOR_MAGENTA, bold=True)
    Y += len(helpString)
    DEBUG.Display("Enter 'q' to exit.")

    while(1):
        inpDate = G.screen.StringInput(X, Y)
        if inpDate == "q":
            DEBUG.Display("")
            return

        finalDate = None
        success = False
        for dateFormat in C.DATEFORMATS:
            try:
                # Time will be the midnight of the previous day. So we need to add a day
                finalDate = (DateTime(datetime.strptime(inpDate, dateFormat)
                             + timedelta(hours=23, minutes=59, seconds=59)))
                success = True
                if finalDate.date < DateTime(-1).date:
                    success = False
                break
            except:
                pass

        if success:
            break

        DEBUG.Display("Invalid Date. Please try again. Enter 'q' to cancel.")
        G.screen.ClearTextArea()
        G.screen.Display(helpString, X,5,color=C.SCR_COLOR_MAGENTA, bold=True)

    DEBUG.Display("")
    return finalDate


def RepeatPicker(original=C.DEFAULT_REPEAT):
    newRepeat = original.copy()
    translate = {"m": "Mon", "t": "Tue", "w": "Wed", "th": "Thurs", "f": "Fri", "s": "Sat", "su": "Sun"}
    sequence = ["m", "t", "w", "th", "f", "s", "su"]

    X, Y = C.SCR_X-4, 5
    G.screen.ClearTextArea()
    DEBUG.Display("Press arrow keys to navigate. (t) Toggle; (c) Confirm; (q) Cancel")
    current = 0
    while(1):
        dY = Y
        G.screen.Display("Set Weekly: ", X-1, Y,bold=True)
        for i in range(7):
            if i == current:
                if newRepeat[sequence[i]]:
                    G.screen.Display(translate[sequence[i]], X, dY,
                            color=C.SCR_COLOR_MAGENTA_GRAY_BGRD, bold=True)
                else:
                    G.screen.Display(translate[sequence[i]], X, dY,
                            color=C.SCR_COLOR_WHITE_GRAY_BGRD,  bold=True)
            else:
                if newRepeat[sequence[i]]:
                    G.screen.Display(translate[sequence[i]], X, dY,
                            color=C.SCR_COLOR_MAGENTA,  bold=True)
                else:
                    G.screen.Display(translate[sequence[i]], X, dY,
                            color=C.SCR_COLOR_NEUTRAL,  bold=True)
            dY += len(translate[sequence[i]]) + 1

        c = G.screen.GetCharacter()
        if c == ord('t'):
            newRepeat[sequence[current]]^=True
        elif c == ord('q'):
            DEBUG.Display("")
            return None
        elif c == ord('c'):
            DEBUG.Display("")
            return newRepeat
        elif c == curses.KEY_LEFT or c == ord('h'):
            current = max(0, current-1)
        elif c == curses.KEY_RIGHT or c == ord('l'):
            current = min(6, current+1)


def TitlePicker():
    X, Y = C.SCR_X - 4, 5

    # Clear Text Region
    G.screen.ClearTextArea()

    helpString = "Enter Title: "
    G.screen.Display(helpString, X, 5,
                     color=C.SCR_COLOR_MAGENTA, bold=True)
    Y += len(helpString)

    while(1):
        inpTitle = G.screen.StringInput(X, Y)
        success = True
        if inpTitle == "":
            success = False

        if success:
            break

        DEBUG.Display(" Please enter a non-empty title string.")
        G.screen.ClearTextArea()
        G.screen.Display(helpString,X, 5,
                color=C.SCR_COLOR_MAGENTA, bold=True)

    DEBUG.Display("")
    return inpTitle


def HelpPage():
    help_items = [ "##########################################################",
                   "Movement/Scrolling",
                   " Use Arrow keys or the vim-style h, j, k, l",
                   "##########################################################",
                   "Marking/Deletion",
                   " 'm' - Mark/Unmark a TODO/Daily to toggle completion status",
                   " 'd' - Mark/Unmark a Habit/Daily/TODO to toggle deletion status",
                   " '+' - Mark/Unmark a Habit to toggle mark-UP status",
                   " '-' - Mark/Unmark a Habit to toggle mark-DOWN status",
                   "##########################################################",
                   "Checklists",
                   " 'c' - View checklist associated with a daily/TODO. The same marking/deletion rules as above for TODOS/dailies apply here.",
                   " Press Enter on a checklist name to change its title. Press Enter on 'Add an Item' to add a checklist item with the entered title",
                   "##########################################################",
                   "Creating Tasks",
                   " ':et <taskname>' - Create a TODO with the given taskname. Put the name in quotes if it has multiple words. Empty taskname will prompt for a title",
                   " ':ed <taskname>' - Create a Daily with the given taskname. Put the name in quotes if it has multiple words. Empty taskname will prompt for a title",
                   " ':eh <taskname>' - Create a Habit with the given taskname. Put the name in quotes if it has multiple words. Empty taskname will prompt for a title",
                   "##########################################################",
                   "Modifying Tasks",
                   " ':set d [trivial|easy|medium|hard] - Change difficulty of a task",
                   " ':set due' - Set a due-date for a TODO (A separate date-picker will launch)",
                   " ':set every <int>' - Change the 'every <int> days' parameter for a daily",
                   " ':set weekly' - Select the weekdays on which the daily is due (A separate picker will launch)",
                   " ':set direction [both|pos|neg|none] - Set the directions for a habit (both means both pos and neg)",
                   "##########################################################",
                   "Managing Changes",
                   " ':w' - Flush all the mark/deletion/edit changes and push them onto the server",
                   " ':r' - Reload data from the Habitica Server (similar to startup). Changes, if any, are not flushed forcibly)",
                   "##########################################################",
                   "Extra Tools",
                   " ':party' - Display information related to current party if any.",
                   " ':data-display' - Display useful information regarding damage, uncompleted dailies etc. Functions borrowed from the excellent Data-Display Tool by @LadyAlys",
                   "##########################################################"
                   ]

    help_items = [M.SimpleTextItem(i) for i in help_items]
    G.screen.SaveInRegister(1)
    helpMenu = M.SimpleTextMenu(help_items, C.SCR_TEXT_AREA_LENGTH)
    helpMenu.SetXY(C.SCR_FIRST_HALF_LENGTH, 5)
    helpMenu.Display()
    helpMenu.Input()
    G.screen.RestoreRegister(1)
