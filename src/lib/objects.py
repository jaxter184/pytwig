# Class declarations of filetypes like devices and clips.
# Some content taken from stylemistake's Bitwig modulator stuff https://github.com/stylemistake

from collections import OrderedDict
from src.lib.util import *
from src.lib.luts import typeLists, names, non_overlap
from src.lib import color, route
import uuid
import struct

serialized = []
import json
class BW_Serializer(json.JSONEncoder):
	def default(self, obj):
		#if str(obj) in ('browsing_session_state_preset(1663)',):
		#	print("Debug")
		#	return "poop"
		#print(obj)
		#print("debug")
		from src.lib import bwfile
		if isinstance(obj, BW_Object):
			#print(serialized)
			if obj in serialized:
				return OrderedDict([("object_ref",serialized.index(obj))])
			else:
				#print(obj)
				serialized.append(obj)
				return OrderedDict([("class",obj.classname), ("object_id",serialized.index(obj)), ("data",obj.data)])
		elif isinstance(obj, uuid.UUID):
			return str(obj)
		elif isinstance(obj, route.Route):
			return obj.__dict__
		elif isinstance(obj, color.Color):
			return obj.__dict__
		elif isinstance(obj, bwfile.BW_File):
			return OrderedDict([("header",obj.header), ("meta",obj.meta), ("contents",obj.contents)])
		elif isinstance(obj, bytes):
			return str(obj)
		else:
			print(type(obj))
			json.JSONEncoder.default(self,obj)

class BW_Object():
	"""Anything that can be in the device contents, including atoms, types, and panels. Any object with the form {class, object_id, data}.

	BW_Objects can be printed and serialized, and their data can be set or get (got?).
	"""
	classname = ""
	data = {}
	def __init__(self, classnum = None, fields = None,):
		self.data = OrderedDict()

		if classnum == None:
			return
		if isinstance(classnum, int):
			if classnum in names.class_names:
				self.classname = "{}({})".format(names.class_names[classnum], classnum)
			elif classnum in non_overlap.potential_names and not classnum in non_overlap.confirmed_names:
			#if input(non_overlap.potential_names[classnum]) == "":
				self.classname = "{}({})".format(non_overlap.potential_names[classnum], classnum)
				non_overlap.confirmed_names[classnum] = non_overlap.potential_names[classnum]
			else:
				self.classname = "missing class (" + str(classnum) + ')'
			self.classnum = classnum
		elif isinstance(classnum, str):
			self.classname = classnum
			self.classnum = extract_num(classnum)
		if self.classnum in typeLists.class_type_list:
			for each_field in typeLists.class_type_list[self.classnum]:
				if each_field in names.field_names:
					fieldname = names.field_names[each_field] + '(' + str(each_field) + ')'
					self.data[fieldname] = typeLists.get_default(each_field)
				else:
					fieldname = "missing_field({})".format(each_field)
					self.data[fieldname] = None
		if not fields == None:
			for each_field in fields:
				if each_field in self.data:
					self.data[each_field] = fields[each_field]

	def __repr__(self):
	    return self.__str__()

	def __str__(self):
		return str(self.classname)

	def __dict__(self):
		return {"class":self.classname, "data":dict(self.data)}

	def show(self):
		print(str(self.__dict__()).replace(', ', ',\n').replace('{', '{\n').replace('}', '\n}'))

	def set(self, key, val):
		"""Sets a field in the object's data dictionary

		Args:
			key (str): The key of the data field that is being set.
			key (int): The classnum to be converted to the key of the data field that is being set.
			val (any): The data value that the field is being set to.

		Returns:
			Abstract_Serializable_BW_Object: self is returned so the function can be daisy-chained
		"""
		if isinstance(key, int):
			key = names.field_names[key] + '(' + str(key) + ')'
		if not key in self.data:
			raise KeyError()
		self.data[key] = val
		return self

	def set_multi(self, dict):
		"""Sets multiple fields in the object's data dictionary.

		Calls the set function once for each key-value pair input.

		Args:
			dict (dict): The set of key-value pairs that are being set

		Returns:
			Abstract_Serializable_BW_Object: self is returned so the function can be daisy-chained
		"""
		for each_key in dict:
			self.set(each_key, dict[each_key])
		return self

	def get(self, key):
		"""Gets the value at a data field in the object's data dictionary.

		Usually used to get a Bitwig object nested inside the self object's data.

		Args:
			key (str): The key of the data field that the data is fetched from.
			key (int): The classnum to be converted to the key of the data field that the data is fetched from.

		Returns:
			Any: Returns the value inside the object's data dictionary, which can be any encodeable/decodable value
		"""
		if isinstance(key, int):
			key = "{}({})".format(names.field_names[key], key)
		return self.data[key]

	def get_referenced_ids(self, output = [], visited = []):
		if self in visited:
			return output
		visited.append(self)

		for each_field in self.data:
			each_value = self.data[each_field]
			if extract_num(each_field) in (153, ):
				if each_value not in output:
					output.append(each_value)
			elif isinstance(each_value, BW_Object):
				each_value.get_referenced_ids(output, visited)
			elif isinstance(each_value, list):
				if len(each_value) > 0 and isinstance(each_value[0], BW_Object):
					for each_object in each_value:
						each_object.get_referenced_ids(output, visited)
		return output

	def check(self, key):
		"""Checks whether the key is in the object's data dictionary.

		Args:
			key (str): The key that is checked.
			key (int): The classnum to be converted to the key that is checked.

		Returns:
			bool: Returns true if the key exists in the data directory and false otherwise
		"""
		if isinstance(key, int):
			key = "{}({})".format(names.field_names[key], key)
		return key in self.data

	def clean(self, visited = []):
		if self in visited:
			return output
		visited.append(self)

		#if self.check(7029) and self.get(7029) == None:
		#	self.set(7029, BW_Object(1969))
			#self.get(7029).set(7026, "Common")
		if self.check(6093):
			self.set(6093, None)
		#if self.check(6726):
		#	self.set(6726, [])

		for each_field in self.data:
			each_value = self.data[each_field]
			if isinstance(each_value, BW_Object):
				each_value.clean(visited)
			elif isinstance(each_value, list):
				if len(each_value) > 0 and isinstance(each_value[0], BW_Object):
					for each_object in each_value:
						each_object.clean(visited)
		return

	# Decoding bytecode
	def parse_field(self, bytecode):
		"""Helper function for reading a field's value from Bitwig bytecode.

		Args:
			bytecode (bytes): Bytecode to be parsed. TODO: consider turning this into its own object so it only has to be passed in and not returned
			obj_list (list): List of objects that are currently in the file. Used to pass on to self.decode_object() so it can parse references.
			raw (bool): Passes a variable through to object decoders that decides whether or not to use the field template lookup tables. TODO: add this

		Returns:
			bytes: Passes back the remaining bytecode to be parsed
			Any: The input bytecode with the encoded field appended to the end
		"""
		bytecode.increment_position(-4)
		field_num = bytecode.read_int()
		if (not field_num in typeLists.field_type_list and not field_num in non_overlap.confirmed_fields):
			non_overlap.confirmed_fields[field_num] = btoi(bytecode.peek(1))

		#print(bytecode[:80])
		parse_type = bytecode.read_int(1)
		if parse_type == 0x01:		#8 bit int
			val = bytecode.read_int(1)
			if val & 0x80:
				val -= 0x100
		elif parse_type == 0x02:	#16 bit int
			val = bytecode.read_int(2)
			if val & 0x8000:
				val -= 0x10000
		elif parse_type == 0x03:	#32 bit int
			val = bytecode.read_int(4)
			if val & 0x80000000:
				val -= 0x100000000
		elif parse_type == 0x04:	#64 bit int
			val = bytecode.read_int(8)
			if val & 0x8000000000000000:
				val -= 0x10000000000000000
		elif parse_type == 0x05:	#boolean
			val = bool(bytecode.read() != b'\x00')
		elif parse_type == 0x06:	#float
			val = struct.unpack('>f', bytecode.read(4))[0]
		elif parse_type == 0x07:	#double
			val = struct.unpack('>d', bytecode.read(8))[0]
		elif parse_type == 0x08:	#string
			val = bytecode.read_str()
		elif parse_type == 0x09:	#object
			val = BW_Object.decode(bytecode)
		elif parse_type == 0x0a:	#null
			val = None
		elif parse_type == 0x0b:	#object reference
			obj_num = bytecode.read_int()
			if obj_num >= len(bytecode.obj_list):
				raise ReferenceError("Referenced object before decode")
				val = bytecode.obj_list[-1]
			else:
				val = bytecode.obj_list[obj_num]
		elif parse_type == 0x0d:	#file
			#raise TypeError('parse type 0d not yet implemented')
			#print(bytecode[:180])
			from src.lib import bwfile
			file_len = bytecode.read_int()
			if file_len == 16:
				val = bytecode.read(16)
			else:
				val = bwfile.BW_File()
				sub_bytecode = bwfile.BW_Bytecode()
				sub_bytecode.set_contents(bytecode.read(file_len))
				#sub_bytecode.set_string_mode("NULL_TERMINATED")
				val.decode(sub_bytecode)
			'''
			if currentSection == 2:
				#field_length += 57 #not sure when to put this in
				val = str(bytecode[:4]) + " - structure placeholder"
			elif header_len<54:
				raise TypeError("short header")
				string_mode = 1
				val = self.decode_object(bytecode, obj_list)
				string_mode = 0
			else:
				val = "structure placeholder"
			bytecode = bytecode[54:]
			'''
		elif parse_type == 0x12:	#object array
			val = []
			while (bytecode.peek_int() != 0x3):
				each_object = BW_Object.decode(bytecode)
				val.append(each_object)
			bytecode.increment_position(4)
		elif parse_type == 0x14:	#map string
			#field += 'type : "map<string,object>",\n' + 'data :\n' + '{\n'
			val = {"type": '', "data": {}}
			string = ''
			val["type"] = "map<string,object>"
			sub_parse_type = bytecode.read_int(1)
			while (sub_parse_type):
				if sub_parse_type == 0x1:
					string = bytecode.read_str()
					val["data"][string] = BW_Object.decode(bytecode)
				else:
					val["type"] = "unknown"
				sub_parse_type = bytecode.read_int(1)
		elif parse_type == 0x15:	#UUID
			val = str(uuid.UUID(bytes=bytecode.read(16)))
		elif parse_type == 0x16:	#color
			flVals = struct.unpack('>ffff', bytecode.read(16))
			val = color.Color(*flVals)
		elif parse_type == 0x17:	#float array (never been used before)
			arr_len = bytecode.read_int()
			val = []
			for i in range(arr_len):
				val.append(struct.unpack('>f', bytecode.read(4))[0])
		elif parse_type == 0x19:	#string array
			arr_len = bytecode.read_int()
			val = []
			for i in range(arr_len):
				val.append(bytecode.read_str())
		elif parse_type == 0x1a:	# route
			#print("untested section: 1a")
			#print("position: " + hex(bytecode.position))
			#print(bytecode.peek(30))
			sub_parse = bytecode.read_int() # someday, I'll figure this out and realize how stupid I was when I wrote this.
			if sub_parse == 0x90:
				bytecode.increment_position(-4)
				#print("nonenone")
				val = route.Route()
				obj = BW_Object.decode(bytecode)
				val.data['obj'] = obj
				val.data['str'] = bytecode.read_str()
				#print(bytecode.peek(40))
				#input()
			elif sub_parse == 0x01:
				val = route.Route()
				val.data['int'] = bytecode.read_int()
				val.data['str'] = bytecode.read_str()
				#print(val)
			else:
				raise TypeError("unparsable value in route")
		elif parse_type == 51:
			print("position: " + hex(bytecode.position))
			raise TypeError("this bug should be gone")
			#print(bytecode[:10])
			bytecode.increment_position(-2)
			val = BW_Object.decode(bytecode)
			#print(bytecode[:10])
		else:
			print(bytecode.obj_list[-1].data)
			print("position: " + hex(bytecode.position))
			bytecode.increment_position(-4)
			print(bytecode.peek(80))
			raise TypeError('unknown type ' + str(parse_type))
		return val

	def encode_field(self, bytecode, field):
		"""Helper function for recursively serializing Bitwig objects into Bitwig bytecode.

		Args:
			bytecode (bytes): Current bytecode to suffix the encoded field onto and output. TODO: consider turning this into its own object so it only has to be passed in and not returned.
			field (str): Key of the field of this object's data dictionary to be encoded into Bitwig bytecode

		Returns:
			bytes: The input bytecode with the encoded field appended to the end.
		"""
		value = self.data[field]
		fieldNum = extract_num(field)
		if value == None:
			bytecode.write('0a')
		else:
			if fieldNum in typeLists.field_type_list:
				if typeLists.field_type_list[fieldNum] == 0x01:
					if value <= 127 and value >= -128:
						bytecode.write('01')
						if value < 0:
							bytecode.write(hex(0xFF + value + 1)[2:])
						else:
							bytecode.write_int(value, 2)
					elif value <= 32767 and value >= -32768:
						bytecode.write('02')
						if value < 0:
							bytecode.write(hex(0xFFFF + value + 1)[2:])
						else:
							bytecode.write_int(value, 4)
					elif value <= 2147483647 and value >= -2147483648:
						bytecode.write('03')
						if value < 0:
							bytecode.write(hex(0xFFFFFFFF + value + 1)[2:])
						else:
							bytecode.write_int(value, 8)
					else:
						bytecode.write('04')
						if value < 0:
							bytecode.write(hex(0xFFFFFFFFFFFFFFFF + value + 1)[2:])
						else:
							bytecode.write_int(value, 16)
				elif typeLists.field_type_list[fieldNum] == 0x05:
					bytecode.write('05')
					bytecode.write('01' if value else '00')
				elif typeLists.field_type_list[fieldNum] == 0x06:
					flVal = struct.unpack('<I', struct.pack('<f', value))[0]
					bytecode.write('06')
					bytecode.write_int(flVal,8)
				elif typeLists.field_type_list[fieldNum] == 0x07:
					dbVal = struct.unpack('<Q', struct.pack('<d', value))[0]
					bytecode.write('07')
					bytecode.write_int(dbVal,16)
				elif typeLists.field_type_list[fieldNum] == 0x08:
					bytecode.write('08')
					value = value.replace('\\n', '\n')
					bytecode.write_str(value)
				elif typeLists.field_type_list[fieldNum] in (0x09, 0x14):
					if isinstance(value, BW_Object):
						if value in bytecode.obj_list:
							bytecode.write('0b')
							bytecode.write_int(bytecode.obj_list.index(value),8)
						else:
							bytecode.write('09')
							value.encode_to(bytecode)
					elif value is None:
						print("untested portion: NoneType")
						bytecode.write('0a')
					elif isinstance(value, dict):
						bytecode.write('14')
						if len(value['data']):
							bytecode.write('01')
							for key in value["data"]:
								bytecode.write_str(key)
								value["data"][key].encode_to(bytecode)
						bytecode.write('00')
				elif typeLists.field_type_list[fieldNum] == 0x0d:
					bytecode.write('0d')
					from src.lib import bwfile
					if isinstance(value, bwfile.BW_File):
						sub_bytecode = bwfile.BW_Bytecode()
						#sub_bytecode.set_string_mode("NULL_TERMINATED")
						value.encode_to(sub_bytecode)
						bytecode.write_int(sub_bytecode.contents_len)
						bytecode.write(sub_bytecode.contents)
					elif isinstance(value, bytes):
						bytecode.write_int(len(value))
						bytecode.write(value)
					else:
						raise TypeError("invalid structure type")
				elif typeLists.field_type_list[fieldNum] == 0x12:
					bytecode.write('12')
					for item in value:
						if isinstance(item, BW_Object):
							if item in bytecode.obj_list:
								bytecode.write('00000001')
								bytecode.write_int(bytecode.obj_list.index(item),8)
							else:
								item.encode_to(bytecode)
						else:
							print("something went wrong in objects.py: \'not object list\'")
					bytecode.write('00000003')
				elif typeLists.field_type_list[fieldNum] == 0x15:
					bytecode.write('15')
					placeholder = uuid.UUID(value)
					#print(placeholder.bytes)
					bytecode.write(placeholder.bytes)
				elif typeLists.field_type_list[fieldNum] == 0x16:
					bytecode.write('16')
					bytecode.write(value.encode()) # maybe I should change this to work how objects do?
				elif typeLists.field_type_list[fieldNum] == 0x17:
					bytecode.write('17')
					bytecode.write_int(len(value), 8)
					for item in value:
						flVal = hex(struct.unpack('<I', struct.pack('<f', item))[0])[2:]
						bytecode.write_int(flVal,8)
				elif typeLists.field_type_list[fieldNum] == 0x19: #string array
					bytecode.write('19')
					bytecode.write_int(len(value), 8)
					for each_str in value:
						each_str = each_str.replace('\\n', '\n')
						bytecode.write_str(each_str)
				elif typeLists.field_type_list[fieldNum] == 0x1a: # route
					bytecode.write('1a')
					if 'obj' in value.data:
						#bytecode.write_int(0x90)
						value.data['obj'].encode_to(bytecode)
					if 'int' in value.data:
						bytecode.write_int(1)
						bytecode.write_int(value.data["int"])
					if 'str' in value.data:
						bytecode.write_str(value.data["str"])
				else:
					if typeLists.field_type_list[fieldNum] == None:
						print("skipped in binary serialization: {}".format(fieldNum))
						pass
					else:
						print("jaxter stop being a lazy nerd and " + hex(typeLists.field_type_list[fieldNum]) + " to the atom encoder. obj: " + str(fieldNum))
			else:
				print("missing type in typeLists.field_type_list: {}".format(fieldNum))
		return

	def decode_fields(self, bytecode):
		"""Helper function for iteratively reading all of an object's fields from Bitwig bytecode

		Args:
			bytecode (bytes): Bytecode to be parsed. TODO: consider turning this into its own object so it only has to be passed in and not returned
			obj_list (list): List of objects that are currently in the file. Used to pass on to self.decode_object() so it can parse references.
			raw (bool): Passes a variable through to object decoders that decides whether or not to use the field template lookup tables. TODO: add this

		Returns:
			bytes: Passes back the remaining bytecode to be parsed
		"""
		field_num = bytecode.read_int()
		while (field_num): # compress to field_num = bytecode.read_int()
			if field_num in names.field_names:
				field_name = names.field_names[field_num] +  '(' + str(field_num) + ')'
			else:
				field_name = "missing_field" +  '(' + str(field_num) + ')'
				print("missing field: " + str(field_num))
			value = self.parse_field(bytecode)
			self.data[field_name] = value
			field_num = bytecode.read_int()

	@staticmethod
	def decode(bytecode):
		"""Helper function for recursively reading Bitwig objects from Bitwig bytecode.

		Args:
			bytecode (bytes): Bytecode to be parsed.

		Returns:
			bytes: Passes back the remaining bytecode to be parsed
		"""
		obj_num = bytecode.read_int()
		if obj_num == 0x1: #object references
			return bytecode.obj_list[bytecode.read_int()]
		else:
			if bytecode.raw:
				obj = BW_Object()
				obj.data = OrderedDict()
				from src.lib.luts import names
				if obj_num in names.class_names:
					obj.classname =  "{}({})".format(names.class_names[obj_num],obj_num)
				else:
					print("problematic missing class {}".format(obj_num))
					obj.classname = "missing_class({})".format(obj_num)
				obj.classnum = obj_num
			else:
				obj = BW_Object(obj_num)
			bytecode.obj_list.append(obj)
			obj.decode_fields(bytecode)
			return obj

	def encode_to(self, bytecode):
		bytecode.obj_list.append(self)
		bytecode.write(hexPad(self.classnum,8))
		for each_field in self.data:
			bytecode.write(hexPad(extract_num(each_field),8))
			self.encode_field(bytecode, each_field)
		bytecode.write('00000000')

	def serialize(self):
		"""Serializes the object into a json format.

		Returns:
			Any: Returns a string containing the json data representing the object.
		"""
		return json.dumps(self, cls=BW_Serializer,indent=2)

	def debug_list_fields(self):
		"""Debug function for listing all the data fields of a Bitwig object
		"""
		output = ''
		output += "class : " + str(self.classname) + '\n'
		for each_field in self.data:
			output += each_field + '\n'
		return output


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

class BW_Meta(BW_Object):

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

class Contents(BW_Object):
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


class Panel(BW_Object):
	def set_root_item(self, classnum):
		from src.lib import panel_items
		root_item = panel_items.Panel_Item(classnum)
		self.set("root_item(6212)", root_item)
		return root_item

	def set_WH(self, w, h):
		self.set(6232, w).set(6233, h)
		return self
