# Class declarations of atoms and references and special data types that only atoms use (modified from original)
# author: stylemistake https://github.com/stylemistake

from collections import OrderedDict
#from pytwig.src.lib.luts import field_lists
from pytwig import bw_object

class Panel(bw_object.BW_Object):
	def set_root_item(self, classnum):
		if isinstance(classnum, Panel_Item):
			self.set("root_item(6212)", classnum)
			return classnum
		root_item = Panel_Item(classnum)
		self.set("root_item(6212)", root_item)
		return root_item

	def set_WH(self, w, h):
		self.set(6232, w).set(6233, h)
		return self

class Panel_Item(bw_object.BW_Object):
	def __init__(self, classnum = None, fields = None):
		super().__init__(classnum, fields)
		self.data["layout_settings(6226)"] = bw_object.BW_Object("float_core.grid_panel_item_layout_settings(1694)")

	def add_item(self, classnum):
		if isinstance(classnum, Panel_Item):
			self.get(6221).append(classnum)
			return self.get(6221)[-1]
		item = Panel_Item(classnum)
		self.get(6221).append(item)
		return self.get(6221)[-1]

	def set_XY(self, x, y):
		self.get(6226).set(6215, x).set(6216, y)
		return self

	def set_WH(self, w, h):
		self.get(6226).set(6217, w).set(6218, h)
		return self

	def serialize(self):
		return json.dumps(self.data, indent = 2)
