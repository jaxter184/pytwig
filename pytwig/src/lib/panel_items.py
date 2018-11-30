# Class declarations of atoms and references and special data types that only atoms use (modified from original)
# author: stylemistake https://github.com/stylemistake

from collections import OrderedDict
from src.lib import util, objects
from src.lib.luts import typeLists
import uuid
import struct

class Panel_Item(objects.BW_Object):
	# removed: def add_field(self, field, value): # wow I was dumb a year ago. This is totally unnecessary.

	def create_item(self, classnum):
		'''if isinstance(classnum, objects.Reference):
			self.get(6194).get(614).append(Atom(105))
			self.get(6194).get(614)[-1].set(248, classnum)
			if quality:
				self.get(6194).get(614)[-1].set(1943, True)
			return self.get(6194).get(614)[-1].get(248)'''
		if self.classnum == 1680:
			self.set(6212, Panel_Item(classnum))
			return self.get(6212)
		else:
			self.get(6221).append(Panel_Item(classnum))
			return self.get(6221)[-1]

	def serialize(self):
		return json.dumps(self.data, indent = 2)
