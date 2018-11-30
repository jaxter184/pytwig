# Class declarations of filetypes like devices and clips.
# Some content taken from stylemistake's Bitwig modulator stuff https://github.com/stylemistake

from collections import OrderedDict
from src.lib import util
from src.lib.luts import typeLists, names
import uuid
import struct

g_object_id = 0
g_unique_object_id = 10000
obj_id_hash = {}
import json
class MyEncoder(json.JSONEncoder):
	def default(self, o):
		global g_object_id
		if isinstance(o, BW_Object):
			obj_id_hash[o.object_id] = g_object_id
			g_object_id += 1
			return OrderedDict([("class",o.classname), ("object_id",obj_id_hash[o.object_id]), ("data",o.data)])
		elif isinstance(o, BW_Meta):
			obj_id_hash[o.object_id] = g_object_id
			g_object_id += 1
			return OrderedDict([("class",o.classname), ("object_id",obj_id_hash[o.object_id]), ("data",o.data)])
		elif isinstance(o, Reference):
			return OrderedDict([("object_ref",obj_id_hash[o.object_ref])])
		elif isinstance(o, bytes):
			return "TODO: replace with UUID interpreter"
		return o.__dict__

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

	def __init__(self, type = ''):
		self.header = 'BtWgXXXXX'
		self.meta = BW_Meta(type)
		self.meta.data['application_version_name'] = BW_VERSION
		self.meta.data = OrderedDict(sorted(self.meta.data.items(), key=lambda t: t[0])) # Sorts the dict. CLEAN: maybe put this somewhere else?
		self.contents = None

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
		from src.lib import atoms
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
		global g_object_id
		g_object_id = 0
		output = self.header
		output += self.meta.encode_to_json()
		output += '\n'
		output += self.contents.encode_to_json()
		return output

class Abstract_Serializable_BW_Object:
	def __init__(self):
		print("please dont initialize me")

	def set(self, key, val):
		if isinstance(key, int):
			#if not key in names.field_names # KeyError detection is automatic
			key = names.field_names[key] + '(' + str(key) + ')'
		#if not key in self.data # KeyError detection is automatic
		self.data[key] = val
		return self

	def get(self, key):
		if isinstance(key, int):
			#if not key in names.field_names # KeyError detection is automatic
			key = names.field_names[key] + '(' + str(key) + ')'
		#if not key in self.data # KeyError detection is automatic
		return self.data[key]

	def encodeField(self, output, field):
		value = self.data[field]
		fieldNum = self.extractNum(field)
		if value==None:
			output += bytearray.fromhex('0a')
			#print("none")
		else:
			#print(typeLists.fieldList[fieldNum])
			#print(value)
			if fieldNum in typeLists.field_type_list:
				if typeLists.field_type_list[fieldNum] == 0x01:
					if value <= 127 and value >= -128:
						output += bytearray.fromhex('01')
						if value < 0:
							#print(hex(0xFF + value + 1)[2:])
							output += bytearray.fromhex(hex(0xFF + value + 1)[2:])
						else:
							output += util.hexPad(value, 2)
					elif value <= 32767 and value >= -32768:
						output += bytearray.fromhex('02')
						if value < 0:
							#print(value)
							#print(hex((value + (1 << 4)) % (1 << 4)))
							output += bytearray.fromhex(hex(0xFFFF + value + 1)[2:])
						else:
							output += util.hexPad(value, 4)
					elif value <= 2147483647 and value >= -2147483648:
						output += bytearray.fromhex('03')
						if value < 0:
							output += bytearray.fromhex(hex(0xFFFFFFFF + value + 1)[2:])
						else:
							output += util.hexPad(value, 8)
				elif typeLists.field_type_list[fieldNum] == 0x05:
					output += bytearray.fromhex('05')
					output += bytearray.fromhex('01' if value else '00')
				elif typeLists.field_type_list[fieldNum] == 0x06:
					flVal = struct.unpack('<I', struct.pack('<f', value))[0]
					output += bytearray.fromhex('06')
					output += util.hexPad(flVal,8)
				elif typeLists.field_type_list[fieldNum] == 0x07:
					dbVal = struct.unpack('<Q', struct.pack('<d', value))[0]
					output += bytearray.fromhex('07')
					output += util.hexPad(dbVal,16)
				elif typeLists.field_type_list[fieldNum] == 0x08:
					output += bytearray.fromhex('08')
					value = value.replace('\\n', '\n')
					try: value.encode("ascii")
					except UnicodeEncodeError:
						output += bytearray.fromhex(hex(0x80000000 + len(value))[2:])
						output.extend(value.encode('utf-16be'))
					else:
						output += util.hexPad(len(value), 8)
						output.extend(value.encode('utf-8'))
				elif typeLists.field_type_list[fieldNum] == 0x09:
					if type(value) == Reference:
						output += bytearray.fromhex('0b')
						output += value.encode()
					elif type(value) == Atom:
						output += bytearray.fromhex('09')
						output += value.encode()
					elif type(value) == NoneType:
						output += bytearray.fromhex('0a')
				elif typeLists.field_type_list[fieldNum] == 0x12:
					output += bytearray.fromhex('12')
					for item in value:
						if type(item) == Atom:
							output += item.encode()
						elif type(item) ==  Reference:
							output += bytearray.fromhex('00000001')
							output += item.encode()
						else:
							print("something went wrong in atoms.py: \'not object list\'")
					output += bytearray.fromhex('00000003')
				elif typeLists.field_type_list[fieldNum] == 0x14:
					output += bytearray.fromhex('14')
					if '' in value["type"]:
						#print("empty string: this shouldnt happen in devices and presets")
						pass
					else:
						output += bytearray.fromhex('01')
						for key in value["data"]:
							output += util.hexPad(len(key), 8)
							output.extend(key.encode('utf-8'))
							output += value["data"][key].encode()
					output += bytearray.fromhex('00')
				elif typeLists.field_type_list[fieldNum] == 0x15:
					output += bytearray.fromhex('15')
					placeholder = uuid.UUID(value)
					output.extend(placeholder.bytes)
				elif typeLists.field_type_list[fieldNum] == 0x16:
					output += bytearray.fromhex('16')
					output += value.encode()
				elif typeLists.field_type_list[fieldNum] == 0x17:
					output += bytearray.fromhex('17')
					output += util.hexPad(len(value), 8)
					for item in value:
						flVal = hex(struct.unpack('<I', struct.pack('<f', item))[0])[2:]
						output += util.hexPad(flVal,8)
				elif typeLists.field_type_list[fieldNum] == 0x19: #string array
					output += bytearray.fromhex('19')
					output += util.hexPad(len(value), 8)
					for i in value:
						i = i.replace('\\n', '\n')
						output += util.hexPad(len(i), 8)
						output.extend(i.encode('utf-8'))
				else:
					if typeLists.field_type_list[fieldNum] == None:
						#print("atoms.py: 'None' in atom encoder. obj: " + str(fieldNum)) #temporarily disabling this error warning because i have no clue what any of these fields are
						pass
					else:
						print("jaxter stop being a lazy nerd and " + hex(typeLists.fieldList[fieldNum]) + " to the atom encoder. obj: " + str(fieldNum))
			else:
				print("missing type in typeLists.fieldList: " + str(fieldNum))
		return output

	def encode_to_json(self):
		return json.dumps(self, cls=MyEncoder,indent=2)

class Reference(Abstract_Serializable_BW_Object):
	def __init__(self, id = 0):
		if isinstance(id, BW_Object):
			self.object_ref = id.object_id
		elif isinstance(id, int):
			self.object_ref = id
		else:
			raise TypeError()

	def __str__(self):
		return "Reference: " + str(self.object_ref)

	def setID(self, id):
		self.object_ref = id

	def serialize(self):
		return {'object_ref': self.object_ref}

	def encode(self):
		output = bytearray(b'')
		output += util.hexPad(self.object_ref,8)
		return output

class Color(Abstract_Serializable_BW_Object):
	def __init__(self, rd, gr, bl, al):
		self.type = 'color'
		self.data = [rd, gr, bl, al]
		if (al == 1.0):
			self.data = self.data[:-1]

	def __str__(self):
		return "Color: " + str(self.data)

	def encode(self):
		output = bytearray(b'')
		count = 0
		for item in self.data["data"]:
			flVal = struct.unpack('<I', struct.pack('<f', item))[0]
			output += util.hexPad(flVal,8)
			count += 1
		if count == 3:
			output += struct.pack('<f', 1.0)
		return output

# BW Objects are anything that can be in the device contents, including types and panels
class BW_Object(Abstract_Serializable_BW_Object): # the inheritence is mostly to simplify type checking

	def __init__(self, classnum, fields = None,):
		self.classname = names.class_names[classnum] + '(' + str(classnum) + ')'
		self.classnum = classnum
		global g_unique_object_id
		g_unique_object_id += 1
		self.object_id = g_unique_object_id
		self.data = OrderedDict()
		for each_field in typeLists.class_type_list[classnum]:
			fieldname = names.field_names[each_field] + '(' + str(each_field) + ')'
			self.data[fieldname] = typeLists.get_default(each_field)
		if not fields == None:
			for each_field in fields:
				if each_field in self.data:
					self.data[each_field] = fields[each_field]

	def __str__(self):
		return "Object: " + str(self.classname)

	def setID(self, id):
		self.object_id = id

	# removed: def stringify(self, tabs = 0):

	def listFields(self):
		output = ''
		output += "class : " + str(self.classname) + '\n'
		for each_field in self.data:
			output += each_field + '\n'
		return output

	def extractNum(self, text = None):
		if text == None:
			text = self.classname
		if text[-1:] == ')':
			start = len(text)-1
			end = start
			while text[start] != '(':
				start-=1
			return int(str(text[start+1:end]))
		else:
			return text

	def encode(self):
		output = bytearray(b'')
		if self.classname == 'meta':
			output += bytearray.fromhex('00000004')
			output += bytearray.fromhex('00000004')
			output.extend('meta'.encode('utf-8'))
			for each_field in self.data:
				output += bytearray.fromhex('00000001')
				output += util.hexPad(len(each_field), 8)
				output.extend(data.encode('utf-8'))
				output = self.encodeField(output, each_field)
			output += bytearray.fromhex('00000000')
		else:
			output += util.hexPad(self.extractNum(),8)
			for each_field in self.data:
				output += util.hexPad(self.extractNum(each_field),8)
				output = self.encodeField(output, each_field)
			output += bytearray.fromhex('00000000')
		return output


class BW_Meta(Abstract_Serializable_BW_Object):

	def __init__(self, type = ''):
		self.classname = 'meta'
		global g_unique_object_id
		g_unique_object_id += 1
		self.object_id = g_unique_object_id
		self.data = OrderedDict()
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
