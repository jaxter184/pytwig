# Class declarations of most Bitwig objects that arent atoms, like contents

from collections import OrderedDict
from pytwig.src.lib.util import *
from pytwig.src.lib.luts import typeLists
from pytwig import object as bwobj
from pytwig import atom as bwatom
from pytwig import panrl as bwpanel

class Contents(bwobj.BW_Object):
	def add_atom(self, field, obj):
		if isinstance(obj, int):
			child = bwatom.Atom(obj)
		elif isinstance(obj, bwatom.Atom):
			child = obj
		else:
			raise TypeError("adding something thats not an atom")
		if isinstance(self.get(field), list):
			self.get(field).append(child)
		else:
			self.set(field, child)
		return child

	def add_child(self, obj):
		#child = bwatom.Atom(classnum)
		#self.get(173).append(child)
		if isinstance(obj, bwatom.Atom):
			return self.add_atom(173, obj)
		elif isinstance(obj, list):
			for i in obj:
				self.add_atom(173, i)
			return None

	def add_panel(self, classnum):
		panel = bwpanel.Panel(classnum)
		self.get(6213).append(panel)
		return panel

	def add_proxy(self, obj, dir = 'out'):
		if isinstance(obj, int):
			if not obj in (50, 154):
				raise TypeError()
			proxy = bwatom.Proxy_Port(obj)
		elif isinstance(obj, bwatom.Atom):
			proxy = obj
		if dir == 'in':
			self.get(177).append(proxy)
		elif dir == 'out':
			self.get(178).append(proxy)
		return proxy


#TODO make sub object for values
