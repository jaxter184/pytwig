# Class declarations of most Bitwig objects that arent Atoms, like contents

from collections import OrderedDict
from src.lib.util import *
from src.lib.luts import typeLists
from src.lib.obj import bwobj, atoms, panel_items

class Contents(bwobj.BW_Object):
	def add_atom(self, field, obj):
		if isinstance(obj, int):
			child = atoms.Atom(obj)
		elif isinstance(obj, atoms.Atom):
			child = obj
		else:
			raise TypeError("adding something thats not an atom")
		if isinstance(self.get(field), list):
			self.get(field).append(child)
		else:
			self.set(field, child)
		return child

	def add_child(self, obj):
		#child = atoms.Atom(classnum)
		#self.get(173).append(child)
		if isinstance(obj, atoms.Atom):
			return self.add_atom(173, obj)
		elif isinstance(obj, list):
			for i in obj:
				self.add_atom(173, i)
			return None

	def add_panel(self, classnum):
		panel = Panel(classnum)
		self.get(6213).append(panel)
		return panel

	def add_proxy(self, obj, dir = 'out'):
		if isinstance(obj, int):
			if not obj in (50, 154):
				raise TypeError()
			proxy = atoms.Proxy_Port(obj)
		elif isinstance(obj, atoms.Atom):
			proxy = obj
		if dir == 'in':
			self.get(177).append(proxy)
		elif dir == 'out':
			self.get(178).append(proxy)
		return proxy


class Panel(bwobj.BW_Object):
	def set_root_item(self, classnum):
		root_item = panel_items.Panel_Item(classnum)
		self.set("root_item(6212)", root_item)
		return root_item

	def set_WH(self, w, h):
		self.set(6232, w).set(6233, h)
		return self

#TODO make sub object for values
