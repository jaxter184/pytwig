# Class declarations of atoms and references and special data types that only atoms use (modified from original)
# author: stylemistake https://github.com/stylemistake

from collections import OrderedDict
from pytwig.src.lib.luts import field_lists
from pytwig import bw_object
#import uuid, struct, json

class Atom(bw_object.BW_Object):
	"""Any BW_Object that has a settings field (fieldnum 6194) that contains component_settings
	"""
	def __init__(self, classnum = None, fields = None):
		if classnum == None:
			self.data["settings(6194)"] = bw_object.BW_Object("float_core.component_settings(236)")
			self.data["settings(6194)"].data["desktop_settings(612)"] = bw_object.BW_Object("float_core.desktop_settings(17)")
			return
		if classnum in field_lists.class_type_list and field_lists.class_type_list[classnum][0] != 6194:
			raise TypeError("Non-atom initialized with atom initializer: {}".format(classnum))
		super().__init__(classnum, fields)
		self.data["settings(6194)"] = bw_object.BW_Object("float_core.component_settings(236)")
		self.data["settings(6194)"].data["desktop_settings(612)"] = bw_object.BW_Object("float_core.desktop_settings(17)")

	def connect(self, obj, quality = False, self_index = -1, outport_index = 0):
		# add blank inports
		if self_index == -1:
			self.get(6194).get(614).append(bw_object.BW_Object(105))
		elif self_index >= 0:
			while(len(self.get(6194).get(614)) <= self_index):
				self.get(6194).get(614).append(bw_object.BW_Object(105))

		# set inport
		if isinstance(obj, int):
			try:
				if obj in (60, 154):
					self.get(6194).get(614)[self_index].set(248, Proxy_Port(obj))
				else:
					self.get(6194).get(614)[self_index].set(248, Atom(obj))
				if quality:
					self.get(6194).get(614)[self_index].set(1943, True)
				return self.get(6194).get(614)[self_index].get(248)
			except:
				raise KeyError("There was an issue adding an inport. Perhaps this isn't an atom?")
		elif isinstance(obj, Atom):
			self.get(6194).get(614)[self_index].set(248, obj)
			if quality:
				self.get(6194).get(614)[self_index].set(1943, True)
			if outport_index:
				self.get(6194).get(614)[self_index].set(249, outport_index)
			return self.get(6194).get(614)[self_index].get(248)
		else:
			raise TypeError("Input is not a valid inport type")

	def set_XY(self, x, y):
		self.get(6194).get(612).set(17, x).set(18, y)
		return self

class Proxy_Port(Atom):
	def set_port(self, type):
		if type == 'audio':
			port = bw_object.BW_Object("float_core.audio_port(242)")
			if self.classnum == 154:
				port.set_multi({499: " Audio out (PARENT)", 372: 3,})
			elif self.classnum == 50:
				port.set_multi({499: " Audio in (PARENT)", 372: 3, 500: True,})
			else:
				print(self.classnum)
				raise Error()
		elif type == 'note':
			port = bw_object.BW_Object("float_core.note_port(61)")
			if self.classnum == 154:
				port.set_multi({499: " Note out",})
			elif self.classnum == 50:
				port.set_multi({499: " Note in", 500: True,})
			else:
				raise Error()
		else:
			raise Error()
		self.set(301, port)
		return self

#class Value_Atom(Atom):
#class Value_Type(bw_object.BW_Object):
