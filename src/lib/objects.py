# Class declarations of filetypes like devices and clips.
# Some content taken from stylemistake's Bitwig modulator stuff https://github.com/stylemistake

from collections import OrderedDict
from src.lib.util import *
from src.lib.luts import typeLists, names
import uuid
import struct

serialized = []
import json
class BW_Serializer(json.JSONEncoder):
	def default(self, obj):
		#print("debug")
		if isinstance(obj, BW_Object):
			#print(serialized)
			if obj in serialized:
				return OrderedDict([("object_ref",serialized.index(obj))])
			else:
				#print(obj)
				serialized.append(obj)
				return OrderedDict([("class",obj.classname), ("object_id",serialized.index(obj)), ("data",obj.data)])
		elif isinstance(obj, bytes):
			return "TODO: replace with UUID interpreter"
		elif isinstance(obj, Color):
			return obj.__dict__
		elif isinstance(obj, List):
			print(obj)
			print("debug2")
			json.JSONEncoder.default(self,obj)
		else:
			json.JSONEncoder.default(self,obj)

class Abstract_Serializable_BW_Object:
	"""Abstract object for BW_Object and Color to inherit from.

	Object containing functions for printing, setting, getting and serializing Bitwig objects.
	"""
	def __init__(self):
		raise Error("please dont initialize me")

	def __repr__(self):
	    return self.__str__()

	def set(self, key, val):
		"""Sets a field in the object's data dictionary

		Args:
			key (str): The key of the data field that is being set. (int) inputs are automatically converted to their strings.
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
			key (str): The key of the data field that the data is fetched from. (int) inputs are automatically converted to their strings.

		Returns:
			Any: Returns the value inside the object's data dictionary, which can be any encodeable/decodable value.
		"""
		if isinstance(key, int):
			key = "{}({})".format(names.field_names[key], key)
		return self.data[key]

	def encode(self):
		raise Error()

	def serialize(self):
		"""Serializes the object into a json format.

		Returns:
			Any: Returns a string containing the json data representing the object.
		"""
		return json.dumps(self, cls=BW_Serializer,indent=2)

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
		for item in self.data:
			flVal = struct.unpack('>I', struct.pack('>f', item))[0]
			output += hexPad(flVal,8)
			count += 1
		if count == 3:
			output += struct.pack('>f', 1.0)
		return output

# BW Objects are anything that can be in the device contents, including types and panels
# Anything object the form {class, object_id, data}
class BW_Object(Abstract_Serializable_BW_Object): # the inheritence is mostly to simplify type checking
	decode_method_raw = False
	def __init__(self, classnum = None, fields = None,):
		self.data = OrderedDict()

		if classnum == None:
			return
		if isinstance(classnum, int):
			if classnum in names.class_names:
				self.classname = names.class_names[classnum] + '(' + str(classnum) + ')'
			else:
				self.classname = "missing class (" + str(classnum) + ')'
			self.classnum = classnum
		elif isinstance(classnum, str):
			from src.lib import util
			self.classname = classnum
			self.classnum = util.extract_num(classnum)
		if self.classnum in typeLists.class_type_list:
			for each_field in typeLists.class_type_list[self.classnum]:
				if each_field in names.field_names:
					fieldname = names.field_names[each_field] + '(' + str(each_field) + ')'
				else:
					self.classname = "missing field (" + str(each_field) + ')'
				self.data[fieldname] = typeLists.get_default(each_field)
		if not fields == None:
			for each_field in fields:
				if each_field in self.data:
					self.data[each_field] = fields[each_field]

	def __str__(self):
		return str(self.classname)

	# removed: def stringify(self, tabs = 0):

	def listFields(self):
		output = ''
		output += "class : " + str(self.classname) + '\n'
		for each_field in self.data:
			output += each_field + '\n'
		return output

	# Decoding bytecode
	def parse_field(self, bytecode, obj_list, string_mode = 0):
		parse_type = bytecode[0]
		bytecode = bytecode[1:]
		if parse_type == 0x01:	#8 bit int
			val = bytecode[0]
			if val & 0x80:
				val -= 0x100
			bytecode = bytecode[1:]
		elif parse_type == 0x02:	#16 bit int
			val = btoi(bytecode[:2])
			if val & 0x8000:
				val -= 0x10000
			bytecode = bytecode[2:]
		elif parse_type == 0x03:	#32 bit int
			val = btoi(bytecode[:4])
			if val & 0x80000000:
				val -= 0x100000000
			bytecode = bytecode[4:]
		elif parse_type == 0x05:	#boolean
			val = bool(bytecode[0])
			bytecode = bytecode[1:]
		elif parse_type == 0x06:	#float
			val = struct.unpack('>f', bytecode[:4])[0]
			bytecode = bytecode[4:]
		elif parse_type == 0x07:	#double
			val = struct.unpack('>d', bytecode[:8])[0]
			bytecode = bytecode[8:]
		elif parse_type == 0x08:	#string
			if string_mode == 0:
				stringLength = btoi(bytecode[:4])
				bytecode = bytecode[4:]
				val = ''
				char_enc = False #false:utf-8, true:utf-16
				if (stringLength & 0x80000000):
					stringLength &= 0x7fffffff
					char_enc = True
				if (stringLength > 100000):
					raise TypeError('String is too long')
				else:
					val = bytecode[:stringLength*(2 if char_enc else 1)].decode('utf-16' if char_enc else 'utf-8')
				bytecode = bytecode[stringLength*(2 if char_enc else 1):]
			elif string_mode == 1:
				while (bytecode[0]) != 0x00:
					val += chr(bytecode[0])
					bytecode = bytecode[1:]
				bytecode = bytecode[1:]
		elif parse_type == 0x09:	#object
			(bytecode, val,) = self.decode_object(bytecode, obj_list)
		elif parse_type == 0x0a:	#null
			val = None
			#bytecode = bytecode
		elif parse_type == 0x0b:	#object reference
			obj_num = btoi(bytecode[:4])
			val = obj_list[obj_num]
			bytecode = bytecode[4:]
		elif parse_type == 0x0d:	#structure									#TODO: implement structure field decoding
			raise TypeError('parse type 0d not yet implemented')
			headerLength = btoi(bytecode[:4])
			bytecode = bytecode[4:]
			if currentSection == 2:
				#field_length += 57 #not sure when to put this in
				val = str(bytecode[:4]) + " - structure placeholder"
			elif headerLength<54:
				raise TypeError("short header")
				string_mode = 1
				val = self.decode_object(bytecode, obj_list)
				string_mode = 0
			else:
				val = "structure placeholder"
			bytecode = bytecode[54:]
		elif parse_type == 0x12:	#object array
			val = []
			while (btoi(bytecode[:4]) != 0x3):
				(bytecode, each_class,) = self.decode_object(bytecode, obj_list)
				val.append(each_class)
			bytecode = bytecode[4:]
		elif parse_type == 0x14:	#map string									#TODO: make this work for other types
			#field += 'type : "map<string,object>",\n' + 'data :\n' + '{\n'
			val = {"type": '', "data": {}}
			string = ''
			val["type"] = "map<string,object>"
			while (bytecode[0]):
				sub_parse_type = bytecode[0]
				bytecode = bytecode[1:]
				if sub_parse_type == 0x0:
					val["data"][''] = None
				elif sub_parse_type == 0x1:
					string_len = btoi(bytecode[:4])
					bytecode = bytecode[4:]
					string = str(bytecode[:string_len], 'utf-8')
					bytecode = bytecode[string_len:]
					(val["data"][string], bytecode) = self.decode_object(bytecode, obj_list)
				else:
					val["type"] = "unknown"
		elif parse_type == 0x15:	#UUID
			val = str(uuid.UUID(bytes=bytecode[:16]))
			bytecode = bytecode[16:]
		elif parse_type == 0x16:	#color
			flVals = struct.unpack('>ffff', bytecode[:16])
			val = Color(*flVals)
			bytecode = bytecode[16:]
		elif parse_type == 0x17:	#float array (never been used before)		#TODO: implement this
			arr_len = btoi(bytecode[:4])
			bytecode = bytecode[:4+arr_len*4]
		elif parse_type == 0x19: #string array
			arr_len = btoi(bytecode[:4])
			bytecode = bytecode[4:]
			val = []
			for i in range(arr_len):
				str_len = btoi(bytecode[:4])
				bytecode = bytecode[4:]
				val.append(bytecode[:str_len].decode('utf-8'))
				bytecode = bytecode[str_len:]
			bytecode = bytecode[16:]
		elif parse_type == 0x1a: #source?													#not done yet
			#print("shit,1a ")
			num_len = btoi(bytecode[:4])
			bytecode = bytecode[4:]
			if num_len == 0x90:
				return (None, None)
			num_val = btoi(bytecode[:4*num_len])
			bytecode = bytecode[4*num_len:]
			str_len = btoi(bytecode[:4])
			bytecode = bytecode[4:]
			str_val = str(bytecode[:str_len].decode("utf-8"))
			bytecode = bytecode[str_len:]
			val = route.Route(num_val, str_val)
		else:
			raise TypeError('unknown type ' + str(parse_type))
		return bytecode, val

	# Encoding to bytecode
	def encode_field(self, output, field, obj_list):
		value = self.data[field]
		fieldNum = extract_num(field)
		if value==None:
			output += bytearray.fromhex('0a')
		else:
			if fieldNum in typeLists.field_type_list:
				if typeLists.field_type_list[fieldNum] == 0x01:
					if value <= 127 and value >= -128:
						output += bytearray.fromhex('01')
						if value < 0:
							output += bytearray.fromhex(hex(0xFF + value + 1)[2:])
						else:
							output += hexPad(value, 2)
					elif value <= 32767 and value >= -32768:
						output += bytearray.fromhex('02')
						if value < 0:
							output += bytearray.fromhex(hex(0xFFFF + value + 1)[2:])
						else:
							output += hexPad(value, 4)
					elif value <= 2147483647 and value >= -2147483648:
						output += bytearray.fromhex('03')
						if value < 0:
							output += bytearray.fromhex(hex(0xFFFFFFFF + value + 1)[2:])
						else:
							output += hexPad(value, 8)
				elif typeLists.field_type_list[fieldNum] == 0x05:
					output += bytearray.fromhex('05')
					output += bytearray.fromhex('01' if value else '00')
				elif typeLists.field_type_list[fieldNum] == 0x06:
					flVal = struct.unpack('<I', struct.pack('<f', value))[0]
					output += bytearray.fromhex('06')
					output += hexPad(flVal,8)
				elif typeLists.field_type_list[fieldNum] == 0x07:
					dbVal = struct.unpack('<Q', struct.pack('<d', value))[0]
					output += bytearray.fromhex('07')
					output += hexPad(dbVal,16)
				elif typeLists.field_type_list[fieldNum] == 0x08:
					output += bytearray.fromhex('08')
					value = value.replace('\\n', '\n')
					try: value.encode("ascii")
					except UnicodeEncodeError:
						output += bytearray.fromhex(hex(0x80000000 + len(value))[2:])
						output.extend(value.encode('utf-16be'))
					else:
						output += hexPad(len(value), 8)
						output.extend(value.encode('utf-8'))
				elif typeLists.field_type_list[fieldNum] == 0x09:
					if isinstance(value, BW_Object):
						if value in obj_list:
							output += bytearray.fromhex('0b')
							output += hexPad(obj_list.index(value),8)
						else:
							output += bytearray.fromhex('09')
							output += value.encode(obj_list)
					elif value is None:
						print("untested portion: NoneType")
						output += bytearray.fromhex('0a')
				elif typeLists.field_type_list[fieldNum] == 0x12:
					output += bytearray.fromhex('12')
					for item in value:
						if isinstance(item, BW_Object):
							if item in obj_list:
								output += bytearray.fromhex('00000001')
								output += hexPad(obj_list.index(item),8)
							else:
								output += item.encode(obj_list)
						else:
							print("something went wrong in objects.py: \'not object list\'")
					output += bytearray.fromhex('00000003')
				elif typeLists.field_type_list[fieldNum] == 0x14:
					output += bytearray.fromhex('14')
					if '' in value["type"]:
						pass
					else:
						output += bytearray.fromhex('01')
						for key in value["data"]:
							output += hexPad(len(key), 8)
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
					output += hexPad(len(value), 8)
					for item in value:
						flVal = hex(struct.unpack('<I', struct.pack('<f', item))[0])[2:]
						output += hexPad(flVal,8)
				elif typeLists.field_type_list[fieldNum] == 0x19: #string array
					output += bytearray.fromhex('19')
					output += hexPad(len(value), 8)
					for i in value:
						i = i.replace('\\n', '\n')
						output += hexPad(len(i), 8)
						output.extend(i.encode('utf-8'))
				else:
					if typeLists.field_type_list[fieldNum] == None:
						pass
					else:
						print("jaxter stop being a lazy nerd and " + hex(typeLists.fieldList[fieldNum]) + " to the atom encoder. obj: " + str(fieldNum))
			else:
				print("missing type in typeLists.fieldList: " + str(fieldNum))
		return output

	def decode_fields(self, bytecode, obj_list):
		field_num = btoi(bytecode[:4])
		bytecode = bytecode[4:]
		while (field_num):
			if field_num in names.field_names:
				field_name = names.field_names[field_num] +  '(' + str(field_num) + ')'
			else:
				field_name = "missing_field" +  '(' + str(field_num) + ')'
				print("missing field: " + str(field_num))
			(bytecode, value,) = self.parse_field(bytecode, obj_list)
			self.data[field_name] = value
			field_num = btoi(bytecode[:4])
			bytecode = bytecode[4:]
		return bytecode

	def decode_object(self, bytecode, obj_list):
		from src.lib import atoms
		from src.lib.luts import names
		obj_num = btoi(bytecode[:4])
		bytecode = bytecode[4:]
		if obj_num == 0x1: #object references
			#print("untested section, stuff may go wrong")
			obj_num = btoi(bytecode[:4])
			#print(obj_num)
			bytecode = bytecode[4:]
			return bytecode, obj_list[obj_num]
		else:
			if self.decode_method_raw:
				obj = BW_Object()
				obj.data = OrderedDict()
				obj.classname = names.class_names[obj_num] + '(' + str(obj_num) + ')'
				obj.classnum = obj_num
				obj_list.append(obj)
				bytecode = obj.decode_fields(bytecode, obj_list)
				#print(obj_list)
				return bytecode, obj
			else:
				obj = BW_Object(obj_num)
				obj_list.append(obj)
				bytecode = obj.decode_fields(bytecode, obj_list)
				#print(obj_list)
				return bytecode, obj

	def decode(self, bytecode, obj_list, raw = False):
		if raw:
			self.decode_method_raw = True
		from src.lib import atoms
		from src.lib.luts import names
		obj_num = btoi(bytecode[:4])
		bytecode = bytecode[4:]
		if obj_num == 0x1: #object references
			raise TypeError("Primary contents cannot be a reference")
		else:
			self.data = OrderedDict()
			self.classname = names.class_names[obj_num] + '(' + str(obj_num) + ')'
			self.classnum = obj_num
			obj_list.append(self)
			bytecode = self.decode_fields(bytecode, obj_list)
			#print(obj_list)
			return bytecode
		#bytecode = self.contents.decode_object(bytecode) # I think this does nothing

	def encode(self, obj_list):
		obj_list.append(self)
		output = bytearray(b'')
		output += hexPad(self.classnum,8)
		for each_field in self.data:
			output += hexPad(extract_num(each_field),8)
			output = self.encode_field(output, each_field, obj_list)
		output += bytearray.fromhex('00000000')
		return output

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

	def encode(self):
		output = bytearray(b'')
		output += bytearray.fromhex('00000004')
		output += bytearray.fromhex('00000004')
		output.extend('meta'.encode('utf-8'))
		for each_field in self.data:
			output += bytearray.fromhex('00000001')
			output += hexPad(len(each_field), 8)
			output.extend(each_field.encode('utf-8'))
			output = self.encode_field(output, each_field, None)
		output += bytearray.fromhex('00000000')
		return output

	# Decoding bytecode
	@staticmethod
	def parse_field(bytecode, string_mode = 0):
		parse_type = bytecode[0]
		bytecode = bytecode[1:]
		if parse_type == 0x01:	#8 bit int
			val = bytecode[0]
			if val & 0x80:
				val -= 0x100
			return val, bytecode[1:]
		elif parse_type == 0x02:	#16 bit int
			val = btoi(bytecode[:2])
			if val & 0x8000:
				val -= 0x10000
			return val, bytecode[2:]
		elif parse_type == 0x03:	#32 bit int
			val = btoi(bytecode[:4])
			if val & 0x80000000:
				val -= 0x100000000
			return val, bytecode[4:]
		elif parse_type == 0x05:	#boolean
			return bool(bytecode[0]), bytecode[1:]
		elif parse_type == 0x06:	#float
			val = struct.unpack('>f', bytecode[:4])[0]
			return val, bytecode[4:]
		elif parse_type == 0x07:	#double
			val = struct.unpack('>d', bytecode[:8])[0]
			return val, bytecode[8:]
		elif parse_type == 0x08:	#string
			if string_mode == 0:
				stringLength = btoi(bytecode[:4])
				bytecode = bytecode[4:]
				val = ''
				char_enc = False #false:utf-8, true:utf-16
				if (stringLength & 0x80000000):
					stringLength &= 0x7fffffff
					char_enc = True
				if (stringLength > 100000):
					raise TypeError('String is too long')
				else:
					val = bytecode[:stringLength*(2 if char_enc else 1)].decode('utf-16' if char_enc else 'utf-8')
				return val, bytecode[stringLength*(2 if char_enc else 1):]
			elif string_mode == 1:
				while (bytecode[0]) != 0x00:
					val += chr(bytecode[0])
					bytecode = bytecode[1:]
				return val, bytecode[1:]
		elif parse_type == 0x0a:	#null
			return None, bytecode
		elif parse_type == 0x15:	#UUID
			val = str(uuid.UUID(bytes=bytecode[:16]))
			return val, bytecode[16:]
		elif parse_type == 0x17:	#float array (never been used before)		#TODO: implement this
			arr_len = btoi(bytecode[:4])
			return val, bytecode[:4+arr_len*4]
		elif parse_type == 0x19: #string array
			arr_len = btoi(bytecode[:4])
			bytecode = bytecode[4:]
			arr = []
			for i in range(arr_len):
				str_len = btoi(bytecode[:4])
				bytecode = bytecode[4:]
				arr.append(bytecode[:str_len].decode('utf-8'))
				bytecode = bytecode[str_len:]
			return arr, bytecode
		else:
			raise TypeError('unknown type ' + str(parse_type))

	def decode(self, bytecode):
		if bytecode[:4] != bytearray([0,0,0,0x04]):
			raise TypeError()
		bytecode = bytecode[4:]
		length = btoi(bytecode[:4])
		bytecode = bytecode[4:]
		self.classname = str(bytecode[:length], 'utf-8')
		bytecode = bytecode[length:]
		while bytecode[:4] != bytearray([0,0,0,0]):
			if btoi(bytecode[:4]) == 0x1: #parameter
				bytecode = bytecode[4:]
				key_len = btoi(bytecode[:4]) #length of the string
				bytecode = bytecode[4:]
				key = bytecode[:key_len].decode('utf-8')
				bytecode = bytecode[key_len:]
				(value, bytecode) = BW_Meta.parse_field(bytecode) #TODO: Fix order of parse_field output
				self.data[key] = value
			elif btoi(bytecode[:4]) == 0x4: #object
				raise TypeError()
				str_len = btoi(bytecode[:4])
				bytecode = bytecode[4:]
				name = str(bytecode[:length], 'utf-8')
				bytecode = bytecode[str_len:]
				#objList.append(Atom(name))
			else:
				raise TypeError()
		bytecode = bytecode[4:]
		return bytecode

class Contents(BW_Object):

	def add_child(self, classnum):
		from src.lib import atoms
		child = atoms.Atom(classnum)
		self.get(173).append(child)
		return child

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
