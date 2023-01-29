__all__ = ["addstr_centered_horizontally", "Widget"]


def addstr_centered_horizontally(
    window, y, text, attr=None
):  # Extend curses.Window and add method to windows instead
    _, max_x = window.getmaxyx()
    len_text = len(text)

    # TODO: Check if curses does this automatically
    if len_text > max_x:
        raise curses.error

    # startx should begin before the center depending on str length
    startx = (max_x - len_text) // 2

    window.addstr(y, startx, text, attr)


class Widget:
    def __init__(self, app, parent=None):
        self.app: App = app
        self.parent = parent
        self.winlist = []

    def run(self, key):
        raise NotImplementedError()

    def refresh(self):
        raise NotImplementedError()
