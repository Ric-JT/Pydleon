import curses
from curses import wrapper
from curses.textpad import rectangle

from pydleon import *

VERSION = "v PROTOTYPE_02"
MAXSIZE_X = 60
MAXSIZE_Y = 24


class App:
    def __init__(self):
        self.widget_list = {}
        self.active_widgets = []
        self.done = False

    def add_widget(self, widget, widget_identifier, active=False):
        if (
            self.widget_list.get(widget_identifier) is None
        ):  # checks if identifier doesnt exist
            self.widget_list.update({widget_identifier: widget})
        else:
            message = "add_widget tried to add an existing widget"
            raise MyException(message=message)

        if active:
            self.activate_widget(widget)

    def get(self, widget_identifier):
        return self.widget_list.get(widget_identifier)

    def activate_widget(self, widget):
        if widget not in self.widget_list.values():
            message = "activate_widget tried to deactivate a non-existing widget"
            raise MyException(message=message)

        self.active_widgets.append(widget)

    def deactivate_widget(self, widget):
        if widget not in self.widget_list.values():
            message = "deactivate_widget tried to deactivate a non-existing widget"
            raise MyException(message=message)

        self.active_widgets.remove(widget)

    def goto_widget(self, origin_widget, target_widget):
        self.deactivate_widget(origin_widget)
        self.activate_widget(target_widget)
        target_widget.refresh(True)

    def quit(self):
        self.done = True

    def maininit(self):  # where add widget usually goes
        start_widget = StartWidget(self)
        smithing_grindlist_widget = SmithingGrindlistWidget(self)
        self.add_widget(start_widget, "start", True)
        self.add_widget(smithing_grindlist_widget, "smithing_grindlist")

        start_widget.refresh()

    def main(self, stdscr):
        rectangle(stdscr, 0, 0, MAXSIZE_Y - 1, MAXSIZE_X - 1)
        stdscr.refresh()

        self.maininit()

        key = None
        while not self.done:
            key = stdscr.getch()

            for widget in self.active_widgets:
                widget.run(key)  # TODO: distinguish between focused widgets


class StartWidget(Widget):
    keyfuncs = {}

    def __init__(self, app: App, parent=None):
        super().__init__(app, parent)
        self.window = curses.newwin(MAXSIZE_Y - 2, MAXSIZE_X - 2, 1, 1)
        self.selection = 0

    @Widget.bind(keyfuncs, curses.KEY_DOWN)
    def go_down(self):
        self.selection += 1
        self.selection = min(1, self.selection)
        self.refresh()

    @Widget.bind(keyfuncs, curses.KEY_UP)
    def go_up(self):
        self.selection -= 1
        self.selection = max(0, self.selection)
        self.refresh()

    @Widget.bind(keyfuncs, 10)
    def press_button(self):
        if self.selection == 0:
            grindlist_widget = self.app.get("smithing_grindlist")
            self.app.goto_widget(self, grindlist_widget)
            return
        elif self.selection == 1:
            self.app.quit()
            return

    def refresh(self, clr=False):
        if clr:
            self.window.clear()

        addstr_centered_horizontally(
            self.window,
            3,
            " Smithing Grindlist ",
            curses.A_REVERSE if self.selection == 0 else curses.A_NORMAL,
        )
        addstr_centered_horizontally(
            self.window,
            5,
            "        QUIT        ",
            curses.A_REVERSE if self.selection == 1 else curses.A_NORMAL,
        )

        self.window.refresh()


class SmithingGrindlistWidget(Widget):
    keyfuncs = {}

    def __init__(self, app, parent=None):
        super().__init__(app, parent)
        self.window = curses.newwin(MAXSIZE_Y - 2, MAXSIZE_X - 2, 1, 1)
        self.selection = 0

    @Widget.bind(keyfuncs, curses.KEY_DOWN)
    def go_down(self):
        self.selection += 1
        self.selection = min(1, self.selection)
        self.refresh()

    @Widget.bind(keyfuncs, curses.KEY_UP)
    def go_up(self):
        self.selection -= 1
        self.selection = max(0, self.selection)
        self.refresh()

    @Widget.bind(keyfuncs, 10)
    def press_button(self):
        if self.selection == 0:
            return
        elif self.selection == 1:
            start_widget = self.app.get("start")
            self.app.goto_widget(self, start_widget)
            return
        self.refresh()

    def refresh(self, clr=False):
        if clr:
            self.window.clear()

        addstr_centered_horizontally(
            self.window,
            3,
            " I don't do nothin' ",
            curses.A_REVERSE if self.selection == 0 else curses.A_NORMAL,
        )

        addstr_centered_horizontally(
            self.window,
            5,
            "      Go back       ",
            curses.A_REVERSE if self.selection == 1 else curses.A_NORMAL,
        )

        self.window.refresh()


app = App()
wrapper(app.main)
