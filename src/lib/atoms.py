# Class declarations of atoms and references and special data types that only atoms use (modified from original)
# author: stylemistake https://github.com/stylemistake

from collections import OrderedDict
from src.lib import util, objects
from src.lib.luts import typeLists
import uuid, struct, json

class Atom(objects.BW_Object):
	def __init__(self, classnum = None, fields = None):
		super().__init__(classnum, fields)
		self.data["settings(6194)"] = objects.BW_Object("float_core.component_settings(236)")
		self.data["settings(6194)"].data["desktop_settings(612)"] = objects.BW_Object("float_core.desktop_settings(17)")

	# component, panel, proxy_in, proxy_out
	'''def add_atom_to_list(self, list_name, atom):
		if not isinstance(atom, atoms.Atom):
			raise TypeError("Object " + atom + " is not an atom")
		if not list_name in self.data:
			raise TypeError("List " + list_name + " does not exist in " + self.__str__())
		if not isinstance(self.data[list_name], List): # TODO: check to make sure the list is an atom list using typeLists.field_type_list
			raise TypeError(list_name + " is not a list of atoms")
		self.data[list_name].append(atom)
		return self
'''
	def create_inport(self, classnum, quality = False):
		if isinstance(classnum, int):
			try:
				self.get(6194).get(614).append(Atom(105))
				if classnum in (60, 154):
					self.get(6194).get(614)[-1].set(248, Proxy_Port(classnum))
				else:
					self.get(6194).get(614)[-1].set(248, Atom(classnum))
				if quality:
					self.get(6194).get(614)[-1].set(1943, True)
				return self.get(6194).get(614)[-1].get(248)
			except:
				raise KeyError("There was an issue adding an inport. Perhaps this isn't an atom?")
		elif isinstance(classnum, Atom):
			self.get(6194).get(614).append(Atom(105))
			self.get(6194).get(614)[-1].set(248, classnum)
			if quality:
				self.get(6194).get(614)[-1].set(1943, True)
			return self.get(6194).get(614)[-1].get(248)
		else:
			raise TypeError("Input is not a valid inport type")

	def set_XY(self, x, y):
		self.get(6194).get(612).set(17, x).set(18, y)
		return self

class Proxy_Port(Atom):
	def set_port(self, type):
		if type == 'audio':
			port = objects.BW_Object("float_core.audio_port(242)")
			if self.classnum == 154:
				port.set_multi({499: " Audio out (PARENT)", 372: 3,})
			elif self.classnum == 50:
				port.set_multi({499: " Audio in (PARENT)", 372: 3, 500: True,})
			else:
				print(self.classnum)
				raise Error()
		elif type == 'note':
			port = objects.BW_Object("float_core.note_port(61)")
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
#class Value_Type(objects.BW_Object):
