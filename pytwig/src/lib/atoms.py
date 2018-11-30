# Class declarations of atoms and references and special data types that only atoms use (modified from original)
# author: stylemistake https://github.com/stylemistake

from collections import OrderedDict
from src.lib import util, objects
from src.lib.luts import typeLists
import uuid, struct, json

class Atom(objects.BW_Object):
	# removed: def add_field(self, field, value): # wow I was dumb a year ago. This is totally unnecessary.

	# component, panel, proxy_in, proxy_out
	def add_atom_to_list(self, list_name, atom):
		if not isinstance(atom, atoms.Atom):
			raise TypeError("Object " + atom + " is not an atom")
		if not list_name in self.data:
			raise TypeError("List " + list_name + " does not exist in " + self.__str__())
		if not isinstance(self.data[list_name], List): # TODO: check to make sure the list is an atom list using typeLists.field_type_list
			raise TypeError(list_name + " is not a list of atoms")
		self.data[list_name].append(atom)
		return self

	def create_inport(self, classnum, quality = False):
		if isinstance(classnum, int):
			try:
				self.get(6194).get(614).append(Atom(105))
				self.get(6194).get(614)[-1].set(248, Atom(classnum))
				if quality:
					self.get(6194).get(614)[-1].set(1943, True)
				return self.get(6194).get(614)[-1].get(248)
			except:
				raise KeyError("There was an issue adding an inport. Perhaps this isn't an atom?")
		elif isinstance(classnum, objects.Reference):
			self.get(6194).get(614).append(Atom(105))
			self.get(6194).get(614)[-1].set(248, classnum)
			if quality:
				self.get(6194).get(614)[-1].set(1943, True)
			return self.get(6194).get(614)[-1].get(248)
		elif isinstance(classnum, atoms.Atom):
			self.get(6194).get(614).append(Atom(105))
			self.get(6194).get(614)[-1].set(248, classnum)
			if quality:
				self.get(6194).get(614)[-1].set(1943, True)
			return self.get(6194).get(614)[-1].get(248)
		else:
			raise TypeError("Input is not a valid inport type")

class AbstractValue(Atom):

	def __init__(self, name, default = None, tooltip = '', label = ''):
		self.data = OrderedDict([
			('settings', Settings()),
			('channel_count', 0),
			('oversampling', 0),
			('name', name),
			('label', label),
			('tooltip_text', tooltip),
			('preset_identifier', name.upper()),
			('modulations_to_ignore', 'MATH'),
			('value_type', None),
			('value', default)
		])

class IndexedValue(AbstractValue):

	classname = 'float_core.indexed_value_atom'

	def __init__(self, name, default = 0, tooltip = '', label = '',
			items = []):
		super().__init__(name, default, tooltip, label)
		self.data['value_type'] = Atom('float_core.indexed_value_type', OrderedDict([
			('items', []),
			('edit_style', 0),
			('columns', 0),
			('default_value', default)
		]))
		for x in items:
			self.add_item(x)

	def add_item(self, name):
		items = self.data['value_type'].data['items']
		seq_id = len(items)
		items.append(Atom('float_core.indexed_value_item', OrderedDict([
			('id', seq_id),
			('name', name)
		])))
		return self
