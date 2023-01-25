import curses

VERSION = "v PROTOTYPE_02"

class MyWidget:
	def __init__(self,app,parent=None):
		self.app = app
		self.parent = parent
		self.winlist = []
	def run(self,key):
		raise NotImplementedError()

	def refresh(self):
		raise NotImplementedError()


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
		pass

	def main(self,stdscr):
		pass

app = App()
wrapper(app.main)