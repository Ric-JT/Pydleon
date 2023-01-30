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
    keyfuncs = {}

    def __init__(self, app, parent=None):
        self.app: App = app
        self.parent = parent
        self.winlist = []

    def bind(keyfuncs, key):
        def decorator(func):
            keyfuncs.update({key: func})

            def wrapper(self):
                bound_func = func.__get__(type(self), self)
                return bound_func(self)

            return wrapper

        return decorator

    def run(self, key):
        if key not in self.keyfuncs:
            return
        self.keyfuncs[key](self)

    def refresh(self, clr=False):
        raise NotImplementedError()
