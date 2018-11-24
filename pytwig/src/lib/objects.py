# Class declarations of filetypes like devices and clips.
# Some content taken from stylemistake's Bitwig modulator stuff https://github.com/stylemistake

from collections import OrderedDict
from src.lib import util, atoms
from src.lib.luts import typeLists
import uuid
import struct
import json

BW_VERSION = '2.4'

BW_FILE_META_TEMPLATE = [
	'application_version_name', 'branch', 'comment', 'creator', 'device_category', 'device_id' , 'device_name', 'revision_id', 'revision_no', 'tags', 'type',]

BW_DEVICE_META_TEMPLATE = [
	'device_description', 'device_type', 'device_uuid',
	# TODO: find out what these do
	'has_audio_input', 'has_audio_output', 'has_note_input', 'has_note_output', 'suggest_for_audio_input', 'suggest_for_note_input',]

BW_MODULATOR_META_TEMPLATE = [
	'device_creator', 'device_type', 'preset_category', 'referenced_device_ids', 'referenced_packaged_file_ids',]

BW_PRESET_TEMPLATE = [
	'device_creator', 'device_type', 'preset_category', 'referenced_device_ids', 'referenced_packaged_file_ids',]

class BW_File:
	# header
	# meta
	# contents

	def __init__(self):
		print("this should not be initialized")
		for each_field in BW_FILE_META_TEMPLATE:
			if not each_field in self.meta.data:
				self.meta.data[each_field] = typeLists.get_default(typeLists.field_type_list[each_field])
		self.meta.data['application_version_name'] = BW_VERSION

	@staticmethod
	def read(text_data): # TODO: Fix this
		if text_data[:4] == 'BtWg' and text_data[4:40].isdigit():
			# Interpreted header
			if not (text_data[:4] == 'BtWg' and text_data[4:40].isdigit()):
				raise TypeError('"' + text_data[:40] + '" is not a valid header')
		# Interpreted header

	def __str__(self):
		return "File: " +  self.meta.data['device_name']

	def set_header(self, value):
		if not (value[:4] == 'BtWg' and value[4:].isdigit() and len(value) == 40):
			raise TypeError('"' + value + '" is not a valid header')
		else:
			self.header = value
		return self

	def set_contents(self, value):
		if not isintance(value, atoms.Atom):
			raise TypeError('"' + m + '" is not a valid header')
		else:
			self.contents = value
		return self


	def set_uuid(self, value):
		self.contents.data['device_UUID'] = value
		self.meta.data['device_uuid'] = value
		self.meta.data['device_id'] = 'modulator:' + value
		return self

	def set_description(self, value):
		self.meta.data['device_description'] = value
		self.contents.data['description'] = value
		return self

class BW_Meta(atoms.Atom):

	def __init__(self, type = ''):
		self.classname = 'meta'
		# Default headers
		if (type == ''):
			self.data = BW_FILE_META_TEMPLATE
		elif (type == 'application/bitwig-device'):
			self.data = BW_DEVICE_META_TEMPLATE
		elif (type == 'application/bitwig-modulator'):
			self.data = BW_MODULATOR_META_TEMPLATE
		elif (type == 'application/bitwig-preset'):
			self.data = BW_PRESET_META_TEMPLATE
		else:
			raise TypeError('Type "' + type + '" is an invalid application type')

	def serialize(self):
		return self.header + json.dumps(self.meta, indent = 2)

class Device_Contents(atoms.Atom):

	classname = 'float_core.device_contents(151)'

	def __init__(self, name = '', description = '', type = '', tags = ''):
		self.data = OrderedDict([
			('settings(6194)', None),
			('child_components(173)', []),
			('panels(6213)', []),
			('proxy_in_ports(177)', []),
			('proxy_out_ports(178)', []),
			('fft_order(6566)', 0),
			('context_menu_panel(6834)', None),
			("polyphony(179)", 1), # double quotes are things that arent in Modulator_Contents
			("sleep_level_threshold(1977)", -96.0),
			("sleep_level_timeout(1978)", 0.05),
			('device_UUID(385)', '6146bcd7-f813-44c6-96e5-2e9d77093a81'),
			('device_name(386)', name),
			('description(2057)', description),
			('creator(387)', 'Bitwig'),
			('comment(388)', ''),
			('keywords(389)', ''),
			('category(390)', 'Control'),
			("device_type(391)", 0),
			("suggest_for_note_input(4846)", false),
			("suggest_for_audio_input(4847)", true),
			('has_been_modified', True),
			("color_tint(6384)", 0),
			("header_area_panel(6417)", null)
		])

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

class Modulator_Contents(atoms.Atom):

	classname = 'float_core.modulator_contents'

	def __init__(self, name, description = ''):
		self.data = OrderedDict([
			('settings', None),
			('child_components', []),
			('panels', []),
			('proxy_in_ports', []),
			('proxy_out_ports', []),
			('fft_order', 0),
			('context_menu_panel', None),
			('device_UUID', '6146bcd7-f813-44c6-96e5-2e9d77093a81'),
			('device_name', name),
			('description', description),
			('creator', 'Bitwig'),
			('comment', ''),
			('keywords', ''),
			('category', 'Control'),
			('has_been_modified', True),
			('detail_panel', None),
			('can_be_polyphonic', True),
			('should_be_polyphonic_by_default', False),
			('should_enable_perform_mode_by_default', False),
		])
