import curses
from curses import wrapper
from curses.textpad import rectangle

VERSION = "v PROTOTYPE_02"

class MyWidget:
	def __init__(self,app,parent=None):
		self.app = app
		self.parent = parent
		self.winlist = []

	def addstr_centered_horizontally(self,window,y,text,attr=None):  # Extend curses.Window and add method to windows instead
		_,max_x = window.getmaxyx()
		len_text = len(text)
		if len_text > max_x:
			raise curses.error    # TODO: Check if curses does this automatically, or create own exception for this

		# startx should begin before the center depending on str length
		startx = (max_x-len_text) // 2

		window.addstr(y,max_x-1,"e",attr)
		window.addstr(y,startx,text,attr)

	def run(self,key):
		raise NotImplementedError()

	def refresh(self):
		raise NotImplementedError()


class StartWidget(MyWidget):
	def __init__(self,app,parent=None):
		super().__init__(app,parent)
		self.window = curses.newwin(MAXSIZE_Y-2,MAXSIZE_X-2,1,1)
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
				return
			elif self.selection == 1:
				return
			elif self.selection == 2:
				self.app.quit()
				return

		self.refresh()

	def refresh(self):
		self.window.clear()

		self.addstr_centered_horizontally(self.window,5,"   YOOOOO   ", curses.A_REVERSE if self.selection == 2 else curses.A_NORMAL)

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
		start_widget = StartWidget(self)
		self.add_widget(start_widget,"start",True)
		start_widget.refresh()

	def main(self,stdscr):
		rectangle(stdscr, 0, 0, MAXSIZE_Y-1, MAXSIZE_X-1)
		stdscr.refresh()

		self.maininit()

		key = None
		while not self.done:
			key = stdscr.getch()

			for widget in self.active_widgets:
				widget.run(key)		# TODO: distinguish between focused widgets




app = App()
wrapper(app.main)