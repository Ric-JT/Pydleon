import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle

VERSION = "v PROTOTYPE_01"

class MyException(Exception):
	pass

class MyWidget:
	def __init__(self,app,parent=None):
		self.app = app
		self.parent = parent
		self.winlist = []

	def run(self,key):
		raise NotImplementedError()

	def refresh(self):
		raise NotImplementedError()


class Widget1(MyWidget):
	def __init__(self,app,parent=None):
		super().__init__(app,parent)
		self.window = curses.newwin(26,16,2,2)
		self.selection = 0
		

	def run(self,key):
		if key == curses.KEY_DOWN:
			self.selection += 1
			self.selection = min(2, self.selection)
		elif key == curses.KEY_UP:
			self.selection -= 1
			self.selection = max(0, self.selection)
		elif key == 10:
			if self.selection == 0:
				widget2 = self.app.get("widget2")
				self.app.goto_widget(self,widget2)
				return
			elif self.selection == 1:
				widget3 = self.app.get("widget3")
				self.app.goto_widget(self,widget3)
				return
			elif self.selection == 2:
				self.app.quit()
				return

		self.refresh()

	def refresh(self):
		self.window.clear()

		self.window.addstr(2,2,"  Goto 2 ", curses.A_REVERSE if self.selection == 0 else curses.A_NORMAL)
		self.window.addstr(3,2,"  Goto 3 ", curses.A_REVERSE if self.selection == 1 else curses.A_NORMAL)
		self.window.addstr(5,2,"  Quit   ", curses.A_REVERSE if self.selection == 2 else curses.A_NORMAL)

		self.window.refresh()


class Widget2(MyWidget):
	def __init__(self,app,parent=None):
		super().__init__(app,parent)
		self.window = curses.newwin(26,16,2,2)
		self.window.clear()
		self.selection = 0

	def run(self,key):
		if key == curses.KEY_DOWN:
			self.selection += 1
			self.selection = min(2, self.selection)
		elif key == curses.KEY_UP:
			self.selection -= 1
			self.selection = max(0, self.selection)
		elif key == 10:
			if self.selection == 0:
				widget1 = self.app.get("widget1")
				self.app.goto_widget(self,widget1)
				return
			elif self.selection == 1:
				widget3 = self.app.get("widget3")
				self.app.goto_widget(self,widget3)
				return
			elif self.selection == 2:
				self.app.quit()
				return

		self.refresh()

	def refresh(self):
		self.window.clear()

		self.window.addstr(2,2,"  Goto 1 ", curses.A_REVERSE if self.selection == 0 else curses.A_NORMAL)
		self.window.addstr(3,2,"  Goto 3 ", curses.A_REVERSE if self.selection == 1 else curses.A_NORMAL)
		self.window.addstr(5,2,"  Quit   ", curses.A_REVERSE if self.selection == 2 else curses.A_NORMAL)

		self.window.refresh()


class Widget3(MyWidget):
	def __init__(self,app,parent=None):
		super().__init__(app,parent)
		self.window = curses.newwin(26,16,2,2)
		self.window.clear()
		self.selection = 0

	def run(self,key):
		if key == curses.KEY_DOWN:
			self.selection += 1
			self.selection = min(2, self.selection)
		elif key == curses.KEY_UP:
			self.selection -= 1
			self.selection = max(0, self.selection)
		elif key == 10:
			if self.selection == 0:
				widget1 = self.app.get("widget1")
				self.app.goto_widget(self,widget1)
				return
			elif self.selection == 1:
				widget2 = self.app.get("widget2")
				self.app.goto_widget(self,widget2)
				return
			elif self.selection == 2:
				pass

		self.refresh()

	def refresh(self):
		self.window.clear()

		self.window.addstr(2,2,"  Goto 1 ", curses.A_REVERSE if self.selection == 0 else curses.A_NORMAL)
		self.window.addstr(3,2,"  Goto 2 ", curses.A_REVERSE if self.selection == 1 else curses.A_NORMAL)
		self.window.addstr(5,2,"Cant Quit", curses.A_REVERSE if self.selection == 2 else curses.A_NORMAL)

		self.window.refresh()
		

class App:
	def __init__(self):
		self.widget_list = {}
		self.active_widgets = []
		self.done = False

	def add_widget(self,widget,widget_identifier,active=False):
		if self.widget_list.get(widget_identifier) is None:	# checks if identifier doesnt exist
			self.widget_list.update({widget_identifier: widget})
		else:	
			raise MyException(message="add_widget tried to add an existing widget")

		if active:
			self.activate_widget(widget)

	def get(self,widget_identifier):
		return self.widget_list.get(widget_identifier)

	def activate_widget(self,widget):
		if widget not in self.widget_list.values():
			raise MyException(message="activate_widget tried to activate a non-existing widget")

		self.active_widgets.append(widget)

	def deactivate_widget(self,widget):
		if widget not in self.widget_list.values():
			raise MyException(message="deactivate_widget tried to deactivate a non-existing widget")

		self.active_widgets.remove(widget)

	def goto_widget(self,origin_widget,target_widget):
		self.deactivate_widget(origin_widget)
		self.activate_widget(target_widget)
		target_widget.refresh()

	def quit(self):
		self.done = True

	def maininit(self):		# where add widget usually goes
		initial_widget = Widget1(self)
		widget2 = Widget2(self)
		widget3 = Widget3(self)
		self.add_widget(initial_widget,"widget1",True)
		self.add_widget(widget2,"widget2")
		self.add_widget(widget3,"widget3")

		initial_widget.refresh()

	def main(self,stdscr):
		rectangle(stdscr, 0, 0, 29, 79)
		stdscr.refresh()

		self.maininit()

		key = None
		while not self.done:
			key = stdscr.getch()

			for widget in self.active_widgets:
				widget.run(key)		# TODO: distinguish between focused widgets




app = App()
wrapper(app.main)