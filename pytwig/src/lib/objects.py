# Class declarations of filetypes like devices and clips.
# Some content taken from stylemistake's Bitwig modulator stuff https://github.com/stylemistake

from collections import OrderedDict
from src.lib import util, atoms
from src.lib.luts import typeLists
import uuid
import struct
import json

BW_VERSION = '2.4'

class BW_File:
	# header
	# meta
	# contents

	def __init__(self):
		print("this class should not be initialized")

    @staticmethod
	def read():
		print("TODO: read files")

class BW_Meta(atoms.Atom):

	def __init__(self, name = '', type = '', uuid = '41be8f3a-6d24-4442-9508-8548dbe62d47'):
		self.classname = 'meta'
		# Default headers
		if (type == 'application/bitwig-device'):
			self.data = OrderedDict([
				('application_version_name', BW_VERSION),
				('branch', 'releases'),
				('comment', ''),
				('creator', 'Bitwig'), # If it works), change this to 'Unknown'
				('device_category', 'Unknown'),
				('device_description' , ''),
				('device_id' , uuid),
				('device_name' , primary),
				('revision_id' , '4eab62ea750680f05a8515dd06615fa3efab6c0f'), # Find out what this can be
				('revision_no' , 53807), # Find out what this can be
				('tags' , ''),
				('type' , 'application/bitwig-device'),

				('device_type' , 'audio_to_audio'), # If it works), change this to ''
				('device_uuid' , uuid),

				(# TODO: find out what these do
				('has_audio_input' , False),
				('has_audio_output' , False),
				('has_note_input' , False),
				('has_note_output' , False),
				('suggest_for_audio_input' , True),
				('suggest_for_note_input' , True),
			])
		elif (type == 'application/bitwig-modulator'):
			self.data = OrderedDict([
				('application_version_name', BW_VERSION),
				('branch', 'releases'),
				('comment', ''),
				('creator', 'Bitwig'), # If it works, change this to 'Unknown'
				('device_category', 'Unknown'),
				('device_id' , 'modulator,' + uuid),
				('device_name' , primary),
				('revision_id' , '70ff9163e17adee5a5bec0966115c2d1db31d9d3'),
				('revision_no' , 69110),
				('tags' , ''),
				('type' , 'application/bitwig-modulator'),

				('device_description' , ''),
				('device_uuid' , uuid),
				('is_polyphonic' , False),
			])
		elif (type == 'application/bitwig-preset'):
			self.data = OrderedDict([
				('application_version_name', BW_VERSION),
				('branch', 'releases'),
				('comment', ''),
				('creator', 'Bitwig'), # If it works, change this to 'Unknown'
				('device_category', 'Unknown'),
				('device_id' , uuid),
				('device_name' , primary),
				('revision_id' , '7e2a6b1f43653ded07446c597894d45b0c562940'),
				('revision_no' , 43068),
				('tags' , ''),
				('type' , 'application/bitwig-preset'),

				('device_creator' , ''),
				('device_type' , ''),
				('preset_category' , 'Unknown'),
				('referenced_device_ids' , []),
				('referenced_packaged_file_ids' , []),
			])
		else:
			raise TypeError('Type "' + type + '" is an invalid header type')

    @staticmethod
	def read_header(self, text_data):
		if primary[:4] == 'BtWg' and primary[4:40].isdigit():
			# Interpreted header
			if not (primary[:4] == 'BtWg' and primary[4:40].isdigit()):
				raise TypeError('Text data ' + primary[:40] + ' is not a valid header')
		# Interpreted header

	def serialize(self):
		return self.header + json.dumps(self.meta, indent = 2) + json.dumps(self.data, indent = 2)

class BW_Device(BW_File):

	def __init__(self, name, description = '', type = '', tags = ''):
		self.meta = Meta(name, description, type = 'application/bitwig-device');
		self.contents = Device_Contents(name, description, type = 'application/bitwig-device');

	def __str__(self):
		return "Device: " +  self.meta.data['device_name']

class Device_Contents(atoms.Atom):

	self.classname = 'float_core.device_contents(151)'

	def __init__(self, name, description = '', type = '', tags = ''):
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

class BW_Modulator(BW_File):
	def __init__(self, name, description = 'Custom modulator'):
		self.meta = Meta(name, description, type='application/bitwig-modulator')
		self.contents = Modulator_Contents(name, description);
		self.header = header
		self.meta.set_uuid(util.uuid_from_text(name))
		self.contents.set_uuid(util.uuid_from_text(name))

	def set_uuid(self, value):
		self.contents.data['device_UUID'] = value
		self.meta.data['device_uuid'] = value
		self.meta.data['device_id'] = 'modulator:' + value
		return self

	def set_description(self, value):
		self.meta.data['device_description'] = value
		self.contents.data['description'] = value
		return self

class Modulator_Contents:

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
			('should_enable_perform_mode_by_default', False)
		])

	def add_component(self, atom):
		self.data['child_components'].append(atom)
		return self

	def add_panel(self, atom):
		self.data['panels'].append(atom)
		return self

	def add_proxy_in(self, atom): #should be consolidated with "add_component"
		self.data['proxy_in_ports'].append(atom)
		return self

	def add_proxy_out(self, atom): #should be consolidated with "add_component"
		self.data['proxy_out_ports'].append(atom)
		return self


	def serialize(self):
		return util.serialize_bitwig_device(OrderedDict([
			('header', self.header),
			('meta', serialize(self.meta)),
			('contents', serialize(self))
		]))
