""" Module "Menu" : Menu classes

    All classes required to implement menus including task menus, chat menus
    etc.
"""
import curses
# Standard Library Imports
import textwrap

import habitican_curse.config as C
import habitican_curse.debug as DEBUG
import habitican_curse.global_objects as G
import habitican_curse.helper as H
import habitican_curse.task as T


# Custom Module Imports


def truncate(string, size):
    return (string[:size - 3] + "...") if len(string) > size else string


class MenuItem(object):
    """ A class for storing a single menu item. It will contain the task object
    as well as the status object. It is general enough to be used as a
    checklist item, and an actual task item"""

    def __init__(self, task, task_type, taskname,
                 width=-1, front=True):
        self.task = task
        self.task_type = task_type

        self.taskname = taskname
        self.taskname: str = str(self.taskname)

        if self.task_type == "habit":
            if self.task.up and self.task.down:
                self.status = H.Status("habit")
            elif self.task.up:
                self.status = H.Status("habitpos")
            elif self.task.down:
                self.status = H.Status("habitneg")
            else:
                self.status = H.Status("unscoredhabit")

            # Set Coordinates for a task
            self.task.SetXY(C.SCR_MAX_MENU_ROWS + 7, 5)

            if self.task.isChallenge:
                self.status.isChallenge = True

        elif self.task_type == "todo" or self.task_type == "daily":
            checklist_tuple = self.task.ChecklistTuple()
            dueDate = getattr(self.task, "dueDate", "")
            self.status = H.Status(self.task_type, checklist_tuple, dueDate)

            # Set Coordinates for a task
            self.task.SetXY(C.SCR_MAX_MENU_ROWS + 7, 5)

            if self.task.isChallenge:
                self.status.isChallenge = True

        else:  # task_type = 'checklist'
            self.status = H.Status(self.task_type)

        self.x = 0
        self.y = 0

        # Width specification
        if width == -1:
            self.width = C.SCR_MENU_ITEM_WIDTH
        else:
            self.width = width
        self.width = int(self.width)

        # Should the status be at the front or the back (True/False
        # respectively)
        self.front = front

    def SetXY(self, x=0, y=0):
        self.x = (x)
        self.y = (y)
        self.SetStatusXY()

    def SetStatusXY(self):
        if self.front:
            self.status.SetXY(self.x,
                              self.y + self.status.ReturnLenString() - 2)
        else:
            self.status.SetXY(self.x, self.y + self.width - 1)

    def DisplayName(self, color=0, highlight=False):
        if hasattr(self.task, "color"):
            color = self.task.color

        # Current task is higlighted, display the details
        if (highlight):
            self.task.Display()

        status_length = self.status.ReturnLenString()
        first_row_size = self.width - status_length - 1

        # Display Task Name
        G.screen.Display(" " * self.width, self.x, self.y,
                         color=C.SCR_COLOR_NEUTRAL, bold=True)
        G.screen.Display(" " * (first_row_size + 1), self.x,
                         self.y + status_length, highlight=highlight)
        G.screen.Display(" " * self.width, self.x + 1, self.y,
                         color=color, highlight=highlight)

        # Show the attributes that can be set (mark,delete, up,down,etc)
        self.status.Display()

        # Add a gray tick if it's completed
        if hasattr(self.task, 'completed') and self.task.completed:
            G.screen.Display(C.SYMBOL_TICK, self.x, self.y + status_length,
                             color=C.SCR_COLOR_NEUTRAL, bold=True,
                             highlight=highlight)

        # If we are set to delete, strikethrough the task name
        strike = self.status.attributes.get(C.SYMBOL_DELETE, False)

        # Print the task name
        if len(self.taskname) < first_row_size:  # No need to truncate
            if self.front:
                G.screen.Display(self.taskname, self.x,
                                 self.y + status_length + 1,
                                 color=color, bold=True, strike=strike,
                                 highlight=highlight)

            else:
                G.screen.Display(self.taskname, self.x, self.y,
                                 color=color, bold=True, strike=strike,
                                 highlight=highlight)

            G.screen.Display(" " * self.width, self.x + 1, self.y,
                             highlight=highlight)
        else:  # We need truncation
            if self.taskname[first_row_size - 1] != ' ':
                if self.front:
                    G.screen.Display(self.taskname[:first_row_size - 1] + "-",
                                     self.x, self.y + status_length + 1,
                                     color=color, bold=True, strike=strike,
                                     highlight=highlight)
                else:
                    G.screen.Display(self.taskname[:first_row_size - 1] + "-",
                                     self.x, self.y,
                                     color=color, bold=True, strike=strike,
                                     highlight=highlight)
                G.screen.Display(
                    truncate(self.taskname[first_row_size - 1:], self.width),
                    self.x + 1, self.y,
                    color=color, bold=True, strike=strike, highlight=highlight)
            elif self.taskname[first_row_size - 1] == ' ':
                if self.front:
                    G.screen.Display(self.taskname[:first_row_size],
                                     self.x, self.y + status_length + 1,
                                     color=color, bold=True, strike=strike,
                                     highlight=highlight)
                else:
                    G.screen.Display(self.taskname[:first_row_size],
                                     self.x, self.y,
                                     color=color, bold=True, strike=strike,
                                     highlight=highlight)
                G.screen.Display(
                    truncate(self.taskname[first_row_size:], self.width),
                    self.x + 1, self.y,
                    color=color, bold=True, strike=strike, highlight=highlight)

    def HighlightName(self):
        self.DisplayName(self, highlight=True)

    def ToggleMarkUp(self):
        self.status.ToggleMarkUp()
        self.HighlightName()

    def ToggleMarkDown(self):
        self.status.ToggleMarkDown()
        self.HighlightName()

    def ToggleMark(self):
        self.status.ToggleMark()
        self.HighlightName()

    def ToggleDelete(self):
        self.status.ToggleDelete()
        self.HighlightName()

    def ToggleEdit(self):
        self.status.ToggleEdit()
        self.HighlightName()

    def EnterNewName(self):
        # Used for changing names of checklist items
        # and adding new items
        G.screen.Display(" " * (C.SCR_Y - self.y - 1), self.x, self.y)
        G.screen.Display(" " * (C.SCR_Y - self.y - 1), self.x + 1, self.y)
        newName = G.screen.StringInput(self.x, self.y)
        self.task.newName = newName
        self.taskname = newName  # Will be restored if changes are cancelled

        # Clear it up a bit
        G.screen.Display(" " * (C.SCR_Y - self.y - 1), self.x, self.y)
        G.screen.Display(" " * (C.SCR_Y - self.y - 1), self.x + 1, self.y)

        self.HighlightName()

    def ShowChecklist(self):
        self.task.ShowChecklist(self)

    def ChangePriority(self, key):
        if self.task_type != "checklist" and self.task.isChallenge:
            # Cannot change the difficulty of a challenge task
            DEBUG.Display("Cannot change the diffifculty of a challenge task")
            return

        self.task.ChangePriority(key)
        self.status.ToggleEdit()

    def ChangeDueDate(self, date):
        if self.task_type != "todo":
            return

        if self.task_type != "checklist" and self.task.isChallenge:
            # Cannot change the due-date parameter of a challenge
            DEBUG.Display("Cannot change the due-date for a challenge TODO")
            return

        self.task.ChangeDueDate(date)
        self.status.SetDue(H.DateTime(date).DueDateFormat())
        self.SetStatusXY()
        self.status.ToggleEdit()

    def RemoveDueDate(self):
        if self.task_type != "todo":
            return

        if self.task_type != "checklist" and self.task.isChallenge:
            # Cannot change the due-date parameter of a challenge
            DEBUG.Display("Cannot change the due-date for a challenge TODO")
            return

        self.task.RemoveDueDate()
        self.status.SetDue("")
        self.status.ToggleEdit()

    def SetWeekly(self, repeat):
        if self.task_type != "daily":
            return

        if self.task_type != "checklist" and self.task.isChallenge:
            # Cannot change the 'weekdays' parameter of a challenge
            DEBUG.Display(
                "Cannot change the 'weekdays' parameter of a challenge daily task")
            return

        self.task.SetWeekly(repeat)
        self.status.ToggleEdit()

    def SetEvery(self, days):
        if self.task_type != "daily":
            return

        if self.task_type != "checklist" and self.task.isChallenge:
            # Cannot change the 'every x days' parameter of a challenge
            DEBUG.Display(
                "Cannot change the 'every x days' parameter of a challenge daily task")
            return

        self.task.SetEvery(days)
        self.status.ToggleEdit()

    def SetDirection(self, up=True, down=True):
        if self.task_type != "habit":
            return

        if self.task_type != "checklist" and self.task.isChallenge:
            # Cannot change direction of a challenge
            DEBUG.Display("Cannot change directions of a challenge habit")
            return

        self.task.SetDirection(up, down)
        if up and down:
            self.status = H.Status("habit", isChallenge=self.task.isChallenge)
        elif up:
            self.status = H.Status("habitpos",
                                   isChallenge=self.task.isChallenge)
        elif down:
            self.status = H.Status("habitneg",
                                   isChallenge=self.task.isChallenge)
        else:
            self.status = H.Status("unscoredhabit",
                                   isChallenge=self.task.isChallenge)

        self.SetStatusXY()
        self.status.ToggleEdit()


class Menu(object):
    """ The menu class - For selecting tasks from the interface. General enough
    to be used for tasks as well as checklists"""

    def __init__(self, items, title, rows=-1, menu_type="task"):
        self.items = items  # Item List
        self.backupItems = []  # Will be used for backing up tasks when
        # adding items to checklists
        self.title = title
        self.menu_type = menu_type

        # Special behavior of checklist
        if self.menu_type == "checklist_menu":
            self.items.append(T.DummyChecklistItem())

        # Defining the menu window using start and end
        if rows == -1:
            rows = C.SCR_MAX_MENU_ROWS
        self.rows = rows

        self.start = 0
        self.end = min(self.rows // 2, len(self.items))
        self.current = 0  # Current task number

        # Coordinates
        self.x = 0
        self.y = 0

    def SetXY(self, x=0, y=0):
        self.x = int(x)
        self.y = int(y)

    def IsEmpty(self):
        if self.items:
            return False
        return True

    def Init(self):
        if self.menu_type == "checklist_menu":
            G.screen.ClearTextArea()
        X, Y = self.x, self.y
        G.screen.Display(self.title, X, Y, bold=True)
        X += 2
        G.screen.ScrollBar(X, Y - 2, self.start, self.end, len(self.items),
                           self.rows)

        for i in range(self.start, self.end):
            self.items[i].SetXY(X, Y)
            self.items[i].DisplayName()

            X += 2  # All task items occupy two rows

    def ScrollUp(self):
        if self.start == 0 and self.current == self.start:
            return  # Nothing to do as we've reached the top

        if self.menu_type == "task":
            G.prevTask = G.currentTask

        if self.current != self.start:
            if self.menu_type == "checklist_menu":
                self.items[self.current].DisplayName()
            self.current -= 1
            if self.menu_type == "task":
                G.currentTask = self.items[self.current]
            elif self.menu_type == "checklist_menu":
                self.items[self.current].HighlightName()

        else:
            if self.menu_type == "checklist_menu":
                self.items[self.current].DisplayName()
            self.start -= 1
            self.current -= 1
            self.end -= 1
            if self.menu_type == "task":
                G.currentTask = self.items[self.current]
            self.Init()  # Reload the menu
            if self.menu_type == "checklist_menu":
                self.items[self.current].HighlightName()

    def ScrollDown(self):
        if self.end == len(self.items) and (self.current == self.end - 1):
            return  # Nothing to do as we've reached the bottom

        if self.menu_type == "task":
            G.prevTask = G.currentTask

        if self.current != self.end - 1:
            if self.menu_type == "checklist_menu":
                self.items[self.current].DisplayName()
            self.current += 1
            if self.menu_type == "task":
                G.currentTask = self.items[self.current]
            elif self.menu_type == "checklist_menu":
                self.items[self.current].HighlightName()

        else:
            self.start += 1
            self.current += 1
            self.end += 1
            if self.menu_type == "task":
                G.currentTask = self.items[self.current]
            self.Init()  # Reload the menu
            if self.menu_type == "checklist_menu":
                self.items[self.current].HighlightName()

    def Input(self):  # This takes control away from Interface
        # Implemented specially for checklists and similar menus
        if self.menu_type == "checklist_menu":
            self.items[self.current].HighlightName()
            DEBUG.Display("(c) confirm; (q) cancel")
            self.backupItems = self.items[:-1]
        while (1):
            c = G.screen.GetCharacter()
            if c == curses.KEY_UP or c == ord('k'):
                self.ScrollUp()
            elif c == curses.KEY_DOWN or c == ord('j'):
                self.ScrollDown()
            elif c == ord('m'):
                if self.current != self.end - 1:
                    self.items[self.current].ToggleMark()
            elif c == ord('d'):
                if self.current != self.end - 1:
                    self.items[self.current].ToggleDelete()
            elif c == ord('\n'):
                self.items[self.current].EnterNewName()
                if self.current != self.end - 1:
                    self.items[self.current].ToggleEdit()
                else:
                    self.items[self.current].task.ChangeName()
                    self.items[self.current].status.SetNewItem()
                    self.items.append(T.DummyChecklistItem())

                    self.Reload()
                    self.Init()
                    self.items[self.current].HighlightName()

            elif c == ord('q') or c == 27:
                return 0
            elif c == ord('c'):
                return 1

    def InitialCurrentTask(self):
        G.prevTask = G.currentTask
        G.currentTask = self.items[self.current]

    def Reload(self):
        self.start = 0
        self.end = min(self.rows // 2, len(self.items))
        self.current = 0  # Current task number

    def Remove(self, ID):
        for i in self.items:
            if i.task.taskID == ID:
                self.items.remove(i)
                break

    def Insert(self, item):
        self.items.insert(0, item)
        self.Reload()
        self.Init()

    def WriteChanges(self):
        for i in self.items:

            # Multiple changes allowed for habits
            while (i.status.attributes.get("+", 0) > 0):
                G.reqManager.MarkUpQueue.append(i)
                i.status.attributes["+"] -= 1
            while (i.status.attributes.get("-", 0) > 0):
                G.reqManager.MarkDownQueue.append(i)
                i.status.attributes["-"] -= 1

            # Process singleton edits
            if i.status.attributes.get(C.SYMBOL_TICK, False):
                G.reqManager.MarkQueue.append(i)
                i.status.Reset()
            elif i.status.attributes.get(C.SYMBOL_DELETE, False):
                G.reqManager.DeleteQueue.append(i)
                i.status.Reset()
            elif i.status.attributes.get(C.SYMBOL_EDIT, False):
                G.reqManager.EditQueue.append(i)
                i.status.Reset()

    def WriteChecklistChanges(self, mainTask):

        # This is used only for checklists
        anyChange = False
        newChecklist = []
        newItems = []
        for i in self.items[:-1]:
            if i.status.attributes.get(C.SYMBOL_TICK, False):
                anyChange = True
                i.task.Mark()
                newChecklist += [i.task.data]
                newItems += [i]
            elif i.status.attributes.get(C.SYMBOL_DELETE, False):
                anyChange = True
            elif i.status.attributes.get(C.SYMBOL_EDIT, False):  # Name Change
                anyChange = True
                i.task.ChangeName()
                newChecklist += [i.task.data]
                newItems += [i]
            elif i.status.IsNewItem():
                anyChange = True
                newChecklist += [i.task.data]
                newItems += [i]
            else:
                newChecklist += [i.task.data]
                newItems += [i]

            i.status.Reset()

        if not anyChange:  # No change, continue.
            return

        # Accomodate any deletions
        self.items = newItems + [self.items[-1]]
        newItems = []
        self.Reload()

        mainTask.ToggleEdit()
        mainTask.task.ChangeChecklist(newChecklist)
        mainTask.status.SetChecklist(mainTask.task.ChecklistTuple())
        mainTask.SetStatusXY()
        self.backupItems = []

    def CancelChecklistChanges(self):
        for i in self.items:
            i.status.Reset()
            i.task.newName = ""
            i.taskname = i.task.text

        self.items = self.backupItems[:] + [self.items[-1]]
        self.Reload()
        self.backupItems = []


class SimpleTextItem(object):
    """ Simple scrollable text menu. Used for displaying party chats,
    drop messages etc. """

    def __init__(self, string, width=-1, additional=''):
        if width == -1:
            width = C.SCR_Y - 20

        self.width = width
        self.string = string

        self.wrap = textwrap.wrap(string, self.width)

        if additional != '':
            self.additional_wrap = textwrap.wrap(additional, self.width)
            self.additional_wrap = ['#' + i for i in self.additional_wrap]
            self.wrap = self.additional_wrap + self.wrap

    def ReturnNumLines(self):
        return len(self.wrap) + 2  # Plus the number of border lines


class SimpleTextMenu(object):
    """ Simple scrollable text menu. Used for displaying party chats,
    drop messages etc. """

    def __init__(self, items, num_rows=-1):

        if num_rows == -1:
            num_rows = C.SCR_MAX_MENU_ROWS

        self.num_rows = num_rows

        self.items = items
        self.text = []

        self.text += ["-" * (self.items[0].width)]  # Border Line
        for i in self.items:
            self.text += i.wrap
            self.text += ["-" * (i.width)]  # Border Line

        # Menu Window Specifications
        self.start = 0
        self.end = min(self.num_rows, len(self.text))

        # Coordinates
        self.x = 0
        self.y = 0

    def SetXY(self, x=0, y=0):
        self.x = x
        self.y = y

    def SetNumRows(self, numRows):
        self.num_rows = numRows

        # Menu Window Specifications
        self.start = 0
        self.end = min(self.num_rows, len(self.text))

    def Display(self):
        G.screen.ClearRegion(self.x, self.x + self.num_rows, self.y,
                             C.SCR_Y - 1)
        X, Y = self.x, self.y

        G.screen.ScrollBar(X, C.SCR_Y - 5, self.start, self.end,
                           len(self.text), self.num_rows)

        for i in range(self.start, self.end):
            if self.text[i][:3] == "---" or self.text[i][0] == "#":
                G.screen.Display(self.text[i], X, Y,
                                 color=C.SCR_COLOR_LIGHT_GRAY, bold=True)
                X += 1
            else:
                G.screen.Display(self.text[i], X, Y,
                                 color=C.SCR_COLOR_WHITE, bold=True)
                X += 1

    def ScrollUp(self):
        if self.start == 0:
            return

        self.start -= 1
        self.end -= 1
        self.Display()

    def ScrollDown(self):
        if self.end == len(self.text):
            return

        self.start += 1
        self.end += 1
        self.Display()

    def Input(self):
        DEBUG.Display("Press q to exit...")
        while (1):
            c = G.screen.GetCharacter()
            if c == curses.KEY_UP or c == ord('k'):
                self.ScrollUp()
            elif c == curses.KEY_DOWN or c == ord('j'):
                self.ScrollDown()
            elif c == 27 or c == ord('q'):
                break

            DEBUG.Display("Press q to exit...")
