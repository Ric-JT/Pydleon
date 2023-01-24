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

