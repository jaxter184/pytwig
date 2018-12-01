# All classes regarding bitwig files
from src.lib import objects
from collections import OrderedDict

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

BW_PRESET_TEMPLATE = [
	'device_creator', 'device_type', 'preset_category', 'referenced_device_ids', 'referenced_packaged_file_ids',]

class BW_File:
	contents_obj_list = []

	def __init__(self, type = None):
		if type == None:
			self.header = ''
			self.meta = objects.BW_Meta(None)
			self.contents = None
			return
		self.header = 'BtWgXXXXX'
		self.meta = objects.BW_Meta(type)
		self.meta.data['application_version_name'] = BW_VERSION
		self.meta.data = OrderedDict(sorted(self.meta.data.items(), key=lambda t: t[0])) # Sorts the dict. CLEAN: maybe put this somewhere else?
		self.contents = None

	def __str__(self):
		return "File: " +  self.meta.data['device_name']

	def set_header(self, value):
		if not (value[:4] == 'BtWg' and value[4:].isdigit() and len(value) == 40):
			raise TypeError('"' + value + '" is not a valid header')
		else:
			self.header = value
		return self

	def set_contents(self, value):
		if not isinstance(value, BW_Object):
			raise TypeError('"' + str(value) + '" is not an atom')
		else:
			self.contents = value
		return self

	def set_uuid(self, value):
		self.contents.data['device_UUID'] = value
		self.meta.data['device_uuid'] = value
		self.meta.data['device_id'] = value
		return self

	def set_description(self, value):
		self.meta.data['device_description'] = value
		self.contents.data['description'] = value
		return self

	def serialize(self):
		global g_serialize_object_id
		g_serialize_object_id = 0
		output = self.header
		output += self.meta.serialize()
		output += '\n'
		output += self.contents.serialize()
		return output

	def encode(self):
		output = bytearray(self.header, "utf-8")
		output += self.meta.encode()
		output += bytearray('\n', "utf-8")
		output += self.contents.encode()
		return output

	def decode(self, bytecode):
		self.header = str(bytecode[:40], "utf-8")
		if self.header[:4] == 'BtWg' and int(self.header[4:40], 16):
			if self.header[11] == '2':
				bytecode = self.meta.decode(bytecode[40:])
				while bytecode[0] == 0x20:
					bytecode = bytecode[1:]
				bytecode = bytecode[1:]
				(self.contents, bytecode) = objects.Abstract_Serializable_BW_Object.decode_object(bytecode)
			elif self.header[11] == '1':
				raise TypeError('"' + self.header + '" is a json typed file')
			else:
				raise TypeError('"' + self.header + '" is not a valid header')
		else:
			raise TypeError('"' + self.header + '" is not a valid header')

	def write(self, path, json = False):
		from src.lib import fs
		fs.write_binary(path, self.encode())

	def export(self, path):
		from src.lib import fs
		fs.write(path, self.serialize().replace('":', '" :'))

	def read(self, path):
		from src.lib import fs
		self.decode(fs.read_binary('hidden/Chain.bwdevice'))
