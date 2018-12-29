# Class declarations of most Bitwig objects like metadata and contents
# Some content taken from stylemistake's Bitwig modulator stuff https://github.com/stylemistake

from collections import OrderedDict
from src.lib.util import *
from src.lib.luts import typeLists
from src.lib import bwobj

# Templates for meta data in the case that the file is created from scratch.
BW_VERSION = '2.4.2'
BW_FILE_META_TEMPLATE = [
	'application_version_name', 'branch', 'comment', 'creator', 'device_category', 'device_id' , 'device_name',
	'revision_id', 'revision_no', 'tags', 'type',]
BW_DEVICE_META_TEMPLATE = [
	'additional_device_types', 'device_description', 'device_type', 'device_uuid',
	# TODO: find out what these do
	'has_audio_input', 'has_audio_output', 'has_note_input', 'has_note_output',
	'suggest_for_audio_input', 'suggest_for_note_input',]
BW_MODULATOR_META_TEMPLATE = [
	'device_creator', 'device_type', 'preset_category', 'referenced_device_ids', 'referenced_packaged_file_ids',]
BW_PRESET_META_TEMPLATE = [
	'device_creator', 'device_type', 'preset_category',
	'referenced_device_ids', "referenced_modulator_ids", "referenced_module_ids", "referenced_packaged_file_ids",]

class BW_Meta(bwobj.BW_Object):

	def __init__(self, type = None):
		self.data = OrderedDict()

		if type == None:
			return
		self.classname = 'meta'
		# Default headers
		for each_field in BW_FILE_META_TEMPLATE:
			self.data[each_field] = typeLists.get_default(each_field)
		if (type == 'application/bitwig-device'):
			for each_field in BW_DEVICE_META_TEMPLATE:
				self.data[each_field] = typeLists.get_default(each_field)
		elif (type == 'application/bitwig-modulator'):
			for each_field in BW_MODULATOR_META_TEMPLATE:
				self.data[each_field] = typeLists.get_default(each_field)
		elif (type == 'application/bitwig-preset'):
			for each_field in BW_PRESET_META_TEMPLATE:
				self.data[each_field] = typeLists.get_default(each_field)
		else:
			raise TypeError('Type "' + type + '" is an invalid application type')
		self.data['application_version_name'] = BW_VERSION

	def encode_to(self, bytecode):
		bytecode.write('00000004')
		bytecode.write_str('meta')
		for each_field in self.data:
			bytecode.write('00000001')
			bytecode.write_str(each_field)
			self.encode_field(bytecode, each_field)
		bytecode.write('00000000')

	def decode(self, bytecode):
		if not bytecode.reading_meta:
			raise SyntaxError("BW_Bytecode in wrong read mode")
		if bytecode.read(4) != bytes([0,0,0,4]):
			raise TypeError()
		self.classname = bytecode.read_str()
		while bytecode.peek(4) != bytes([0,0,0,0]):
			type = bytecode.read_int()
			if type == 0x1: #field
				key = bytecode.read_str()
				self.data[key] = self.parse_field(bytecode)
			elif type == 0x4: #object
				raise TypeError("No objects should be in root of metadata")
				str_len = btoi(bytecode[:4])
				bytecode = bytecode[4:]
				name = str(bytecode[:length], 'utf-8')
				bytecode = bytecode[str_len:]
				#objList.append(Atom(name))
			else:
				bytecode.increment_position(-48)
				print(bytecode.peek(40))
				raise TypeError("mystery type?!?")
		bytecode.increment_position(4)
		return

class Contents(bwobj.BW_Object):
	def add_atom(self, field, classnum):
		from src.lib import atoms
		child = atoms.Atom(classnum)
		if isinstance(self.get(field), list):
			self.get(field).append(child)
		else:
			self.set(field, child)
		return child

	def add_child(self, classnum):
		#from src.lib import atoms
		#child = atoms.Atom(classnum)
		#self.get(173).append(child)
		return self.add_atom(173, classnum)

	def add_panel(self, classnum):
		panel = Panel(classnum)
		self.get(6213).append(panel)
		return panel

	def add_proxy(self, classnum):
		from src.lib import atoms
		if classnum != 50:
			raise TypeError()
		proxy = atoms.Proxy_Port(50)
		self.get(178).append(proxy)
		return proxy


class Panel(bwobj.BW_Object):
	def set_root_item(self, classnum):
		from src.lib import panel_items
		root_item = panel_items.Panel_Item(classnum)
		self.set("root_item(6212)", root_item)
		return root_item

	def set_WH(self, w, h):
		self.set(6232, w).set(6233, h)
		return self
